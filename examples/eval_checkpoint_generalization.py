"""Zero-shot evaluation of a trained checkpoint on new agent counts / shelf mixing.

No training happens here. Agents are copied from the checkpoint round-robin
(target k <- source k % n_source), which keeps team parity because both the
environment and the checkpoint use team_id = agent_id % n_teams.

Example:
  python examples/eval_checkpoint_generalization.py \
      --checkpoint runs/.../checkpoint_09700.pt --agent-counts 4 8 16 \
      --home-ratios 1.0 0.875 0.75 0.5 --episodes 20
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from itertools import product
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import train_recurrent_ippo_consensus as T  # noqa: E402

KEYS = [
    "eval_deliveries", "eval_returns_home", "eval_task_return",
    "eval_full_cycle_success_rate", "eval_delivery_success_rate",
    "eval_wrong_returns", "eval_failed_forward_rate",
    "eval_blocking_agent_rate", "eval_deadlock_agent_rate",
    "eval_position_change_rate",
]


MAP_SIZES = {"tiny": (1, 3), "small": (2, 3), "medium": (2, 5)}


def build_env_kwargs(base_kwargs, n_agents, home_ratio, sensor_range, map_size="checkpoint"):
    kw = copy.deepcopy(base_kwargs)
    for key in ("n_agents", "request_queue_size", "request_queue_size_per_team"):
        kw.pop(key, None)
    kw["sensor_range"] = sensor_range
    kw["shelf_team_mode"] = "balanced_soft_zones"
    kw["shelf_soft_zone_ratio"] = float(home_ratio)
    # Same rule as the ex5 launcher: one request per agent, split per team.
    kw["request_queue_size"] = n_agents
    kw["request_queue_size_per_team"] = n_agents // 2
    kw["n_agents"] = n_agents
    kw["n_teams"] = 2
    if map_size != "checkpoint":
        if kw.get("layout"):
            raise ValueError("map size overrides are not supported for custom layouts")
        kw["shelf_rows"], kw["shelf_columns"] = MAP_SIZES[map_size]
        kw["column_height"] = 8
    return kw


def checkpoint_pgct_gate(ckpt, n_agents):
    """Lift the saved policy gate through the same mapping as the frozen actors.

    Distinct copies of an identical actor have zero common-probe distance.
    Other pairs retain the checkpoint's measured EMA distances. This is a
    frozen, transferred graph, not graph re-estimation on the new environment.
    The environment still applies its current spatial eligibility each step.
    """
    cfg = ckpt["config"]
    if (not cfg.get("communication_enabled", True)
            or cfg.get("peer_transfer_mode") == "none"
            or cfg.get("pgct_peer_loss_coef", 0) <= 0):
        return np.zeros((n_agents, n_agents), dtype=np.float32)
    if cfg.get("graph_mode") != "policy" or cfg.get("peer_transfer_mode") != "pgct":
        raise ValueError("checkpoint graph transfer requires policy PGCT; use --communication-graph none")
    source_n = len(ckpt["agents"])
    graph = ckpt["graph"]
    estimator = T.TeamGraphEstimator(
        n_agents=source_n, edge_threshold=cfg["edge_threshold"],
        min_probe_count=cfg["min_probe_count"],
        uncertainty_scale=cfg["uncertainty_scale"],
        value_uncertainty_decay=cfg["value_uncertainty_decay"],
        min_policy_information=cfg.get("pgct_min_policy_information", 0),
        gate_style=cfg.get("pgct_gate_style", "soft"),
    )
    for name, shape in (("distance_ema", (source_n, source_n)),
                        ("distance_count", (source_n, source_n)),
                        ("policy_information", (source_n,))):
        value = np.asarray(graph[name]).copy()
        if value.shape != shape:
            raise ValueError(f"checkpoint graph {name} shape {value.shape} != {shape}")
        setattr(estimator, name, value)
    warm = ckpt["iteration"] >= cfg["pgct_warmup_updates"]
    threshold = cfg["pgct_distance_threshold"]
    source_gate = estimator.pgct_gate_matrix(
        warm, threshold, cfg["pgct_distance_temperature"], cfg["pgct_gate_power"])
    sources = np.arange(n_agents) % source_n
    gate = source_gate[np.ix_(sources, sources)].copy()
    if warm and threshold > 0:
        informed = estimator.policy_information[sources] >= estimator.min_policy_information
        identical = sources[:, None] == sources[None, :]
        gate[identical & informed[:, None] & informed[None, :]] = 1.0
    np.fill_diagonal(gate, 0.0)
    return gate


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--agent-counts", type=int, nargs="+", default=[4, 8, 16])
    p.add_argument("--home-ratios", type=float, nargs="+", default=[1.0, 0.875, 0.75, 0.5])
    p.add_argument("--map-sizes", nargs="+", choices=["checkpoint", *MAP_SIZES], default=["checkpoint"])
    p.add_argument("--episodes", type=int, default=20)
    p.add_argument("--horizon", type=int, default=500)
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--out", default="")
    p.add_argument("--video-dir", default="")
    p.add_argument("--video-fps", type=int, default=8)
    p.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    p.add_argument("--torch-threads", type=int, default=1)
    p.add_argument("--communication-graph", choices=["checkpoint", "none"], default="checkpoint")
    args = p.parse_args()

    if any(n < 2 or n % 2 for n in args.agent_counts):
        p.error("agent counts must be positive multiples of two")
    if any(not 0.5 <= r <= 1.0 for r in args.home_ratios):
        p.error("home ratios must be in [0.5, 1.0]")
    if min(args.episodes, args.horizon, args.video_fps, args.torch_threads) < 1:
        p.error("episodes, horizon, video FPS and torch threads must be positive")
    torch.set_num_threads(args.torch_threads)
    device = torch.device(
        ("cuda" if torch.cuda.is_available() else "cpu")
        if args.device == "auto" else args.device
    )
    ckpt = T._load_checkpoint(args.checkpoint, device)
    cfg = ckpt["config"]
    base_kwargs = ckpt["effective_env_kwargs"]
    src_states = ckpt["agents"]
    if len(src_states) % 2:
        p.error("round-robin team-preserving transfer requires an even source agent count")
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    results = []
    for n_agents in args.agent_counts:
        gate = (checkpoint_pgct_gate(ckpt, n_agents)
                if args.communication_graph == "checkpoint"
                else np.zeros((n_agents, n_agents), dtype=np.float32))
        for map_size, ratio in product(args.map_sizes, args.home_ratios):
            kw = build_env_kwargs(base_kwargs, n_agents, ratio, cfg["sensor_range"], map_size)
            env = T.make_env(cfg["env_id"], kw, observation_format=cfg["observation_format"])
            env.reset(seed=args.seed)
            spec = T.get_semantic_observation_spec(env)
            obs_dim = int(T.get_flat_obs_dims(env)[0])
            action_dim = int(T.get_discrete_action_dims(env)[0])
            teams = env.unwrapped.agent_team_ids.tolist()
            grid_shape = list(map(int, env.unwrapped.grid_size))
            shelf_count = len(env.unwrapped.shelfs)
            env.close()
            agents = []
            for k in range(n_agents):
                net = T.RecurrentActorCritic(
                    obs_dim=obs_dim, action_dim=action_dim,
                    mlp_hidden_dim=cfg["mlp_hidden_dim"],
                    recurrent_hidden_dim=cfg["recurrent_hidden_dim"],
                    encoder_type=cfg["obs_encoder"],
                    spatial_channels=int(spec.spatial_channels),
                    spatial_size=int(spec.spatial_size), ego_dim=int(spec.ego_dim),
                ).to(device)
                net.load_state_dict(src_states[k % len(src_states)])
                net.eval()
                agents.append(net)
            want_video = bool(args.video_dir)
            t0 = time.time()
            metrics, video = T.evaluate(
                cfg["env_id"], kw, cfg["observation_format"], agents,
                episodes=args.episodes, horizon=args.horizon, gamma=cfg["gamma"],
                obs_dim=obs_dim, recurrent_hidden_dim=cfg["recurrent_hidden_dim"],
                device=device, seed=args.seed, collect_video=want_video,
                use_action_mask=cfg.get("action_mask", True),
                communication_gate=gate,
            )
            row = {"n_agents": n_agents, "home_ratio": ratio, "teams": teams,
                   "seconds": round(time.time() - t0, 1),
                   "checkpoint": str(Path(args.checkpoint).resolve()),
                   "source_agent_indices": [k % len(src_states) for k in range(n_agents)],
                   "episodes": args.episodes, "horizon": args.horizon, "seed": args.seed,
                   "device": str(device), "evaluation": "zero-shot deterministic"}
            row["communication_graph"] = args.communication_graph
            row["communication_gate"] = gate.tolist()
            row.update(map_size=map_size, grid_shape=grid_shape, shelf_count=shelf_count)
            row.update({k: float(metrics.get(k, float("nan"))) for k in KEYS})
            row["deliveries_per_agent"] = row["eval_deliveries"] / n_agents
            results.append(row)
            print(json.dumps(row), flush=True)
            if want_video and video is not None:
                Path(args.video_dir).mkdir(parents=True, exist_ok=True)
                map_label = "" if map_size == "checkpoint" else f"_{map_size}"
                T.save_local_eval_video(
                    video, Path(args.video_dir) / f"eval_{n_agents}ag{map_label}_home{ratio:.3f}.mp4", args.video_fps)
            if args.out:
                Path(args.out).write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
