"""Train IPPO / PGCT / critic-sharing baselines from random initialization (no curriculum).

Every mode of one (map, seed) uses the same environment, PPO settings, budget,
evaluation seeds, random initial weights and canonical probe bank. Only the donor
set of the existing critic peer loss differs:

  ippo    no communication, no critic sharing
  pgct    existing JS gate (policy graph, physical neighbours)
  oracle  same-team physical neighbours (ground-truth labels)
  all     every physical neighbour
  wrong   cross-team physical neighbours only

The original trainer is reused unchanged. Settings come from the completed E1/E2
PGCT run of the spatial experiment, except: no initial checkpoint, and the
learning rate / entropy of the earlier successful from-scratch run (2e-4 / .05).
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import time
import traceback
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

try:
    from . import common as C
    from .exp_b_oracle_consensus import matched_transfer, transfer_summary
    from . import marl_baselines as B
    from . import probes_v2 as P2
except ImportError:
    import common as C
    from exp_b_oracle_consensus import matched_transfer, transfer_summary
    import marl_baselines as B
    import probes_v2 as P2

from examples import train_recurrent_ippo_consensus as T
from examples.train_pgct_spatial_experiments import MAPS, experiment_logging

SHARING_MODES = ["ippo", "pgct", "oracle", "all", "wrong"]
MODES = SHARING_MODES + B.ALGORITHMS  # mappo / seps / hetdps: separate learners, same env/budget/evaluation
GRAPH = {"pgct": "policy", "oracle": "oracle", "all": "unrestricted", "wrong": "wrong"}
THRESHOLDS = [10, 20, 30, 40]


def base_config(reference, map_name, *, seed, timesteps, home_ratio, learning_rate, entropy_coef,
                save_interval, output, track, save_video, smoke, stage="single", wandb_project="rware-from-scratch",
                wandb_mode="online", env_variant="e1", team_reward="individual"):
    template = next((j for j in reference["jobs"] if j["map"] == map_name and j["mode"] == "pgct"), None)
    if template is None:
        raise ValueError(f"No PGCT template for map {map_name} in the reference experiment.")
    cfg = copy.deepcopy(template["config"])
    env = json.loads(cfg["env_kwargs_json"])
    env.update(MAPS[map_name], shelf_soft_zone_ratio=home_ratio)
    env.update(P2.ENV_VARIANTS[env_variant])  # e1f: team goals at the two bottom corners
    env.update(team_reward_mode=team_reward)  # individual (default) or team: shared within each team
    cfg.update(init_checkpoint="", transfer_components="all", seed=seed, total_timesteps=timesteps,
               learning_rate=learning_rate, entropy_coef=entropy_coef, env_kwargs_json=json.dumps(env),
               save_dir=str(output), save_interval=save_interval, track=track, save_eval_video=save_video,
               wandb_log_eval_video=track and save_video, wandb_group=output.name, log_interval=10,
               wandb_project=wandb_project, wandb_mode=wandb_mode, wandb_tags=f"{stage},{env_variant},{team_reward},seed{seed}")
    if smoke:
        cfg.update(total_timesteps=64, rollout_steps=32, sequence_length=8, ppo_epochs=1, minibatch_chunks=4,
                   device="cpu", probe_interval=1, min_probe_count=1, pgct_warmup_updates=0,
                   policy_probe_batch_size=8, eval_interval=0, eval_episodes=1, eval_horizon=16,
                   save_interval=0, save_eval_video=False, wandb_log_eval_video=False)
    return cfg


def mode_config(cfg, mode, name):
    cfg = copy.deepcopy(cfg)
    cfg.update(exp_name=name, wandb_name=name, wandb_tags=cfg["wandb_tags"] + f",{mode}")
    config = T.TrainConfig(**cfg)
    if mode == "ippo" or mode in B.ALGORITHMS:
        config.communication_enabled = False
        T.enforce_communication_config(config)
        env = json.loads(config.env_kwargs_json)
        env.update(communication_enabled=False, communication_topology="none")
        config.env_kwargs_json = json.dumps(env)
    else:
        config.graph_mode = GRAPH[mode]
    return asdict(config)


def build_bank(cfg, path):
    """One canonical bank per (map, seed), built like the trainer's own first probe call."""
    config = T.TrainConfig(**cfg)
    env_kwargs = json.loads(config.env_kwargs_json)
    with T.make_env(config.env_id, env_kwargs, config.observation_format) as env:
        env.reset(seed=config.seed)
        sequences, metadata = T.sample_policy_probe_sequences(config, env, None, np.random.default_rng(config.seed + 9173))
    torch.save(dict(sequences=sequences, metadata=metadata, seed=config.seed + 9173,
                    note="Shared by every mode of this map/seed; built from a fresh reset."), path)


def plan(args):
    reference = json.loads((args.reference_experiment / "experiment.json").read_text(encoding="utf-8"))
    output = (args.output_dir or C.ROOT / "runs" / ("scratch_" + datetime.now().strftime("%Y%m%d_%H%M%S"))).resolve()
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    jobs, banks = [], {}
    args.env_variant = getattr(args, "env_variant", "e1")      # older callers: defaults unchanged
    args.probe_bank = getattr(args, "probe_bank", "canonical")
    args.team_reward = getattr(args, "team_reward", "individual")
    for map_name in args.maps:
        for seed in args.seeds:
            cfg = base_config(reference, map_name, seed=seed, timesteps=args.timesteps, home_ratio=args.home_ratio,
                              learning_rate=args.learning_rate, entropy_coef=args.entropy_coef,
                              save_interval=args.save_interval, output=output, track=args.track,
                              save_video=args.save_video, smoke=args.smoke_test, stage=args.stage_label,
                              wandb_project=args.wandb_project, wandb_mode=args.wandb_mode,
                              env_variant=args.env_variant, team_reward=args.team_reward)
            label = args.env_variant if args.env_variant != "e1" else map_name
            if args.team_reward != "individual":
                label += f"_{args.team_reward}rew"
            bank = output / (f"canonical_bank_{label}_s{seed}.pt" if args.probe_bank == "canonical"
                             else f"probe_bank_v2_{label}_s{seed}.pt")
            banks[str(bank)] = cfg
            warmup = 0 if args.smoke_test else cfg["pgct_warmup_updates"]
            for mode in args.modes:
                name = f"{label}_{mode}_s{seed}"
                config = mode_config(cfg, mode, name)
                jobs.append(dict(name=name, map=map_name, mode=mode, seed=seed, config=config,
                                 canonical_bank=None if mode == "ippo" or mode in B.ALGORITHMS else str(bank),
                                 transfer_warmup_updates=warmup,
                                 effective_timesteps=math.ceil(config["total_timesteps"] / config["rollout_steps"])
                                 * config["rollout_steps"]))
    output.mkdir(parents=True)
    for path, cfg in banks.items():
        if args.probe_bank == "canonical":
            build_bank(cfg, Path(path))
        else:
            v2, summary = P2.build_bank(cfg["env_id"], json.loads(cfg["env_kwargs_json"]), seed=cfg["seed"])
            P2.save_bank(v2, summary, Path(path))
    manifest = dict(created=datetime.now().astimezone().isoformat(timespec="seconds"),
                    initialization="random (no checkpoint, no curriculum)", home_ratio=args.home_ratio,
                    env_variant=args.env_variant, probe_bank=args.probe_bank, team_reward=args.team_reward,
                    stage=args.stage_label, wandb_project=args.wandb_project if args.track else None,
                    learning_rate=args.learning_rate, entropy_coef=args.entropy_coef,
                    reference_experiment=str(args.reference_experiment.resolve()), eval_seed=args.eval_seed,
                    smoke_test=args.smoke_test, jobs=jobs,
                    note="Same seed => same random initial weights for every mode (checked via "
                         "initial_weights_sha256.txt). Only the critic peer-loss donor set differs.")
    (output / "experiment.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output, manifest


def job_status(run_dir, **values):
    path = Path(run_dir) / "job_status.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(dict(values, updated=datetime.now().astimezone().isoformat(timespec="seconds")),
                                    indent=2), encoding="utf-8")
    # Parallel jobs read each other's status while comparing; replace atomically. Windows
    # refuses the replace while another process has the target open, so retry briefly.
    for attempt in range(100):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 99:
                raise
            time.sleep(.1)


def read_status(run_dir):
    try:
        return json.loads((Path(run_dir) / "job_status.json").read_text(encoding="utf-8"))["status"]
    except FileNotFoundError:
        return "planned"
    except (json.JSONDecodeError, KeyError, PermissionError):
        return "unknown"


def run_job(output, manifest, name, eval_seed):
    job = next((j for j in manifest["jobs"] if j["name"] == name), None)
    if job is None:
        raise ValueError(f"No job named {name} in {output}")
    cfg = T.TrainConfig(**job["config"])
    run_dir = output / name
    if manifest["smoke_test"]:
        torch.set_num_threads(1)
    original_init = T.init_wandb

    def init_wandb(config, save_dir):
        # Trainer's own W&B run (project/group/name/tags/full config) plus the comparison metadata.
        # Every trainer logs with step=env_steps, so W&B's Step axis is environment steps for all modes.
        run = original_init(config, save_dir)
        if run is not None:
            run.config.update(dict(algorithm=job["mode"], stage=manifest.get("stage", "single"), map=job["map"],
                                   seed=job["seed"], home_ratio=manifest["home_ratio"], plan=str(output),
                                   initialization=manifest["initialization"],
                                   budget_env_steps=job["effective_timesteps"],
                                   transfer_warmup_updates=job["transfer_warmup_updates"],
                                   env_kwargs=json.loads(config.env_kwargs_json)), allow_val_change=True)
            job_status(run_dir, status="running", wandb_url=run.url)
        return run
    T.init_wandb = init_wandb
    try:
        with experiment_logging(cfg, run_dir, eval_seed):
            job_status(run_dir, status="running")
            if job["mode"] in B.ALGORITHMS:
                with B.install(cfg, job["mode"], run_dir):
                    T.train(cfg)
            else:
                with matched_transfer(cfg, run_dir, job["mode"], bank_path=job["canonical_bank"],
                                      warmup_updates=job["transfer_warmup_updates"]):
                    T.train(cfg)
        if not (run_dir / "final.pt").is_file():
            raise RuntimeError("Training did not produce final.pt")
        job_status(run_dir, status="complete",
                   transfer=transfer_summary(run_dir) if (run_dir / "transfer.jsonl").exists() else None)
    except BaseException as exc:
        if run_dir.exists():
            job_status(run_dir, status="failed", error=repr(exc), traceback=traceback.format_exc())
        raise
    finally:
        T.init_wandb = original_init


def compare(output):
    manifest = json.loads((output / "experiment.json").read_text(encoding="utf-8"))
    rows = []
    for job in manifest["jobs"]:
        run_dir = output / job["name"]
        status = read_status(run_dir)
        row = dict(name=job["name"], map=job["map"], mode=job["mode"], seed=job["seed"], status=status,
                   **C.learning_summary(run_dir))
        steps, metrics = C.evaluation_curve(run_dir)
        for level in THRESHOLDS:
            row[f"first_step_delivery_ge_{level}"] = next(
                (s for s, m in zip(steps, metrics) if m["deliveries"] >= level), None)
        hash_path = run_dir / "initial_weights_sha256.txt"
        row["initial_weights_sha256"] = hash_path.read_text(encoding="utf-8").strip() if hash_path.exists() else None
        if (run_dir / "transfer.jsonl").exists():
            transfer = transfer_summary(run_dir)
            row.update(same_team_arc_updates=transfer["same_team_arc_updates"],
                       cross_team_arc_updates=transfer["cross_team_arc_updates"])
        rows.append(row)
    # Matched starts: the critic-sharing modes of a (map, seed) share one architecture and must begin from
    # identical weights. MAPPO/SePS/HetDPS have different architectures, so they are not compared.
    for key in {(r["map"], r["seed"]) for r in rows}:
        hashes = {r["initial_weights_sha256"] for r in rows if (r["map"], r["seed"]) == key
                  and r["mode"] in SHARING_MODES and r["initial_weights_sha256"]}
        for r in rows:
            if (r["map"], r["seed"]) == key:
                r["initial_weights_match_other_modes"] = (len(hashes) <= 1) if r["mode"] in SHARING_MODES else "n/a"
    groups = {}
    for r in rows:
        groups.setdefault((r["map"], r["mode"]), []).append(r)
    summary = []
    for (map_name, mode), members in sorted(groups.items()):
        auc = [m["delivery_auc_per_step"] for m in members if m.get("delivery_auc_per_step") is not None]
        last = [m["last10_deliveries"] for m in members if m.get("last10_deliveries") is not None]
        summary.append(dict(map=map_name, mode=mode, seeds=len(members), with_curves=len(auc),
                            auc_mean=float(np.mean(auc)) if auc else None,
                            auc_std=float(np.std(auc, ddof=1)) if len(auc) > 1 else None,
                            last10_mean=float(np.mean(last)) if last else None,
                            last10_std=float(np.std(last, ddof=1)) if len(last) > 1 else None))
    (output / "comparison.json").write_text(json.dumps(dict(runs=rows, by_mode=summary), indent=2), encoding="utf-8")
    fmt = lambda v, d=3: "—" if v is None else (f"{v:.{d}f}" if isinstance(v, float) else str(v))
    lines = ["# From-scratch comparison", "",
             "Deterministic masked evaluation, 20 fixed reset seeds, 500 steps. AUC = trapezoid over logged "
             "evaluations / covered steps (no step-0 score). Std uses training seeds (ddof=1).", "",
             "| Map | Mode | Seeds | AUC mean | AUC std | Last-10 mean | Last-10 std |", "|---|---|---:|---:|---:|---:|---:|"]
    for s in summary:
        lines.append(f"| {s['map']} | {s['mode']} | {s['with_curves']}/{s['seeds']} | {fmt(s['auc_mean'])} | "
                     f"{fmt(s['auc_std'])} | {fmt(s['last10_mean'])} | {fmt(s['last10_std'])} |")
    lines += ["", "| Run | Status | Last eval step | AUC | Last-10 | " +
              " | ".join(f"≥{t} at" for t in THRESHOLDS) + " | Same/cross arc updates | Same init |",
              "|---|---|---:|---:|---:|" + "---:|" * len(THRESHOLDS) + "---|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['status']} | {fmt(r.get('last_eval_step'))} | "
                     f"{fmt(r.get('delivery_auc_per_step'))} | {fmt(r.get('last10_deliveries'))} | " +
                     " | ".join(fmt(r[f'first_step_delivery_ge_{t}']) for t in THRESHOLDS) +
                     f" | {r.get('same_team_arc_updates', '—')}/{r.get('cross_team_arc_updates', '—')} | "
                     f"{r['initial_weights_match_other_modes']} |")
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--maps", nargs="+", choices=list(MAPS), default=["e1"])
    parser.add_argument("--env-variant", choices=list(P2.ENV_VARIANTS), default="e1",
                        help="e1f: E1 map with team goals at the two bottom corners (requires --maps e1).")
    parser.add_argument("--probe-bank", choices=["canonical", "v2"], default="canonical",
                        help="v2: validated bank with separate gate (team) and critic-distillation probes.")
    parser.add_argument("--team-reward", choices=["individual", "team"], default="individual",
                        help="team: delivery/return rewards go to every member of the delivering team (shaping stays individual).")
    parser.add_argument("--modes", nargs="+", choices=MODES, default=["ippo", "pgct", "oracle", "all"])
    parser.add_argument("--seeds", type=int, nargs="+", default=[1])
    parser.add_argument("--timesteps", type=int, default=10000000)
    parser.add_argument("--home-ratio", type=float, default=.5)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--entropy-coef", type=float, default=.05)
    parser.add_argument("--save-interval", type=int, default=250, help="Updates between checkpoints.")
    parser.add_argument("--eval-seed", type=int, default=5000001)
    parser.add_argument("--reference-experiment", type=Path, default=C.REFERENCE_EXPERIMENT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--plan-only", action="store_true", help="Create the plan and banks; run nothing.")
    parser.add_argument("--run-job", help="Run one planned job from --plan (used for parallel launches).")
    parser.add_argument("--plan", type=Path, help="Existing plan folder for --run-job / --compare-only.")
    parser.add_argument("--compare-only", action="store_true")
    parser.add_argument("--track", action="store_true", help="Log every run to W&B (step = environment steps).")
    parser.add_argument("--wandb-project", default="rware-from-scratch")
    parser.add_argument("--wandb-mode", choices=["online", "offline"], default="online")
    parser.add_argument("--stage-label", default="single", help="Recorded in W&B tags/config and the plan.")
    parser.add_argument("--save-video", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    os.environ.setdefault("WANDB_DISABLE_GIT", "true")
    if args.run_job or args.compare_only:
        if not args.plan:
            parser.error("--run-job and --compare-only need --plan")
        output = args.plan.resolve()
        manifest = json.loads((output / "experiment.json").read_text(encoding="utf-8"))
        if args.run_job:
            run_job(output, manifest, args.run_job, manifest["eval_seed"])
        try:
            compare(output)
        except Exception as exc:  # a sibling job may be mid-write; training itself is already saved
            print(f"Comparison skipped ({exc!r}); rerun with --compare-only.", flush=True)
            return
        print(f"Comparison: {output / 'comparison.md'}", flush=True)
        return
    if len(set(args.modes)) != len(args.modes) or len(set(args.seeds)) != len(args.seeds):
        parser.error("Modes and seeds must be unique.")
    if args.env_variant != "e1" and args.maps != ["e1"]:
        parser.error("--env-variant e1f applies to the E1 map only.")
    if not .5 <= args.home_ratio <= 1 or args.timesteps <= 0 or args.save_interval < 0:
        parser.error("Home ratio must be in [.5, 1]; timesteps positive; save interval nonnegative.")
    try:
        output, manifest = plan(args)
    except ValueError as exc:
        parser.error(str(exc))
    for job in manifest["jobs"]:
        print(f"{job['name']}: graph_mode={job['config']['graph_mode']} {job['effective_timesteps']} steps", flush=True)
    print(f"Plan: {output / 'experiment.json'}", flush=True)
    if args.plan_only:
        return
    for job in manifest["jobs"]:
        run_job(output, manifest, job["name"], manifest["eval_seed"])
        compare(output)
    print(f"Comparison: {output / 'comparison.md'}", flush=True)


if __name__ == "__main__":
    main()
