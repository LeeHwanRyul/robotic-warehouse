import itertools
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from latent_team import common as C
from latent_team.exp_a_team_identifiability import evidence_score, record_evidence, visible
from latent_team.exp_b_oracle_consensus import allowed_donors, build_matched_jobs, check_allocation

TEAMS = np.array([0, 1, 0, 1])


def brute_auroc(scores, positive):
    pos, neg = scores[positive], scores[~positive]
    wins = [1.0 if p > n else .5 if p == n else 0.0 for p, n in itertools.product(pos, neg)]
    return float(np.mean(wins))


def test_auroc_matches_pairwise_definition_with_ties():
    rng = np.random.default_rng(0)
    scores = rng.integers(0, 4, size=40).astype(float)
    positive = rng.random(40) < .4
    assert C.auroc(scores, positive) == pytest.approx(brute_auroc(scores, positive))
    assert C.auroc([3, 2, 1, 0], [True, True, False, False]) == 1.0
    assert C.auroc([0, 0, 0], [True, False, False]) == .5
    assert C.auroc([1, 2], [True, True]) is None


def test_pair_order_and_teammate_recovery():
    assert C.same_team_mask(TEAMS).tolist() == [True, True, False, False, False, False]
    assert C.teammate_recovery(np.array([1, 1, 0, 0, 0, 0]), TEAMS) == 1.0
    assert C.teammate_recovery(np.array([0, 0, 1, 1, 1, 1]), TEAMS) == 0.0
    # All partners tied: one third of the credit per agent.
    assert C.teammate_recovery(np.zeros(6), TEAMS) == pytest.approx(1 / 3)


def test_local_evidence_uses_observer_view_and_sensor_window():
    seen = visible([(0, 0), (2, 0), (9, 9), (1, 1)], radius=5)
    assert seen[0, 1] and seen[1, 0] and not seen[0, 2] and not seen[0, 0]
    evidence = np.zeros((4, 4, 2))
    info = dict(pickup_events=[dict(agent_id=2, shelf_id=7, return_phase=False),
                               dict(agent_id=2, shelf_id=8, return_phase=True)],
                delivery_events=[dict(carrier_id=4, goal=(4, 10)), dict(carrier_id=0, goal=(4, 10))])
    requested = [{7}, {9}]  # shelf 7 is requested for team 0 only
    goals = [{(4, 10)}, {(5, 10)}]
    record_evidence(evidence, info, seen, TEAMS, requested, goals)
    # Agent 1 (team 0) sees agent 2 lift a team-0 shelf; agent 4 (team 1) sees a non-team-1 shelf.
    assert evidence[0, 1].tolist() == [1, 0] and evidence[3, 1].tolist() == [0, 1]
    # Agent 4 delivers at the team-0 goal: consistent with team 0 (observer 1), not team 1 (observer 2).
    assert evidence[0, 3].tolist() == [1, 0] and evidence[1, 3].tolist() == [0, 1]
    assert evidence[2].sum() == 0  # agent 3 is outside every window
    assert evidence_score([0, 3], [0, 0]).tolist() == [0.0, pytest.approx(.3)]


def test_experiment_b_donor_sets_and_audit():
    neighbors = np.ones((4, 4), dtype=bool)
    np.fill_diagonal(neighbors, False)
    neighbors[0, 2] = neighbors[2, 0] = False
    oracle = allowed_donors("oracle", TEAMS, neighbors)
    assert oracle.tolist() == [[False] * 4, [False, False, False, True], [False] * 4, [False, True, False, False]]
    assert (allowed_donors("all", TEAMS, neighbors) == neighbors).all()
    assert not (allowed_donors("wrong", TEAMS, neighbors) & (TEAMS[:, None] == TEAMS[None, :])).any()
    allocation = np.zeros((4, 4))
    allocation[1, 3] = 1
    check_allocation("oracle", allocation, TEAMS, neighbors)
    with pytest.raises(RuntimeError):
        check_allocation("wrong", allocation, TEAMS, neighbors)
    allocation[0, 2] = 1  # same team but outside physical range
    with pytest.raises(RuntimeError):
        check_allocation("oracle", allocation, TEAMS, neighbors)


@pytest.mark.skipif(not (C.REFERENCE_EXPERIMENT / "experiment.json").exists() or not C.STAGE03.exists(),
                    reason="Local reference experiment is not available.")
def test_experiment_b_jobs_differ_from_reference_pgct_only_in_graph_mode(tmp_path):
    args = SimpleNamespace(init_checkpoint=C.STAGE03, reference_experiment=C.REFERENCE_EXPERIMENT, maps=["e1"],
                           modes=["oracle", "all", "wrong"], seeds=[1], timesteps=4000000, track=False,
                           save_video=False, smoke_test=False, transfer_warmup_updates=None)
    jobs = build_matched_jobs(args, tmp_path / "plan")
    assert [j["config"]["graph_mode"] for j in jobs] == ["oracle", "unrestricted", "wrong"]
    assert all(j["transfer_warmup_updates"] == 100 and j["effective_timesteps"] == 4000768 for j in jobs)
    assert all(Path(j["canonical_bank"]).name == "canonical_probes.pt" for j in jobs)
    assert not (tmp_path / "plan").exists()


@pytest.mark.skipif(not (C.REFERENCE_EXPERIMENT / "e1_pgct_s1/metrics.jsonl").exists(),
                    reason="Local reference experiment is not available.")
def test_learning_summary_reproduces_recorded_e1_auc():
    pgct = C.learning_summary(C.REFERENCE_EXPERIMENT / "e1_pgct_s1")
    ippo = C.learning_summary(C.REFERENCE_EXPERIMENT / "e1_ippo_s1")
    assert pgct["delivery_auc_per_step"] == pytest.approx(45.8559, abs=1e-4)
    assert ippo["delivery_auc_per_step"] == pytest.approx(44.5734, abs=1e-4)


@pytest.mark.skipif(not (C.REFERENCE_EXPERIMENT / "e1_ippo_s1/metrics.jsonl").exists() or not C.STAGE03.exists(),
                    reason="Local reference experiment is not available.")
def test_short_budget_is_a_matched_prefix_of_the_reference(tmp_path):
    args = SimpleNamespace(init_checkpoint=C.STAGE03, reference_experiment=C.REFERENCE_EXPERIMENT, maps=["e1"],
                           modes=["oracle"], seeds=[1], timesteps=1024000, track=False,
                           save_video=False, smoke_test=False, transfer_warmup_updates=None)
    jobs = build_matched_jobs(args, tmp_path / "plan")
    assert jobs[0]["effective_timesteps"] == 1024000
    short = C.learning_summary(C.REFERENCE_EXPERIMENT / "e1_ippo_s1", max_step=1024000)
    assert short["last_eval_step"] == 1024000 and short["eval_count"] == 20
    assert short["delivery_auc_per_step"] == pytest.approx(43.828, abs=1e-3)


@pytest.mark.skipif(not (C.REFERENCE_EXPERIMENT / "experiment.json").exists(),
                    reason="Local reference experiment is not available.")
def test_from_scratch_plan_is_random_init_and_differs_only_in_sharing(tmp_path):
    from latent_team.train_from_scratch import plan
    args = SimpleNamespace(reference_experiment=C.REFERENCE_EXPERIMENT, output_dir=tmp_path / "plan", maps=["e1"],
                           seeds=[3], modes=["ippo", "pgct", "oracle", "all", "wrong"], timesteps=10000000,
                           home_ratio=.5, learning_rate=2e-4, entropy_coef=.05, save_interval=250,
                           track=False, save_video=False, smoke_test=False, eval_seed=5000001,
                           stage_label="test", wandb_project="rware-from-scratch", wandb_mode="online")
    output, manifest = plan(args)
    configs = {j["mode"]: j["config"] for j in manifest["jobs"]}
    assert all(c["init_checkpoint"] == "" and c["seed"] == 3 and c["total_timesteps"] == 10000000
               and c["learning_rate"] == 2e-4 and c["entropy_coef"] == .05 for c in configs.values())
    assert [configs[m]["graph_mode"] for m in ("pgct", "oracle", "all", "wrong")] == \
        ["policy", "oracle", "unrestricted", "wrong"]
    ignore = {"graph_mode", "exp_name", "wandb_name", "wandb_tags"}
    for mode in ("oracle", "all", "wrong"):
        assert {k for k in configs[mode] if configs[mode][k] != configs["pgct"][k]} <= ignore
    ippo = configs["ippo"]
    assert not ippo["communication_enabled"] and ippo["peer_transfer_mode"] == "none" and ippo["pgct_peer_loss_coef"] == 0
    assert '"shelf_soft_zone_ratio": 0.5' in ippo["env_kwargs_json"]
    banks = {j["canonical_bank"] for j in manifest["jobs"] if j["mode"] != "ippo"}
    assert len(banks) == 1 and Path(banks.pop()).exists()


def test_baseline_clustering_utilities_match_reference_behaviour():
    from latent_team import marl_baselines as B
    x = np.array([[0., 0], [0, .1], [5, 5], [5, 5.1]])
    labels = B.kmeans(x, 2, seed=0)
    assert labels[0] == labels[1] != labels[2] == labels[3]
    assert B.davies_bouldin(x, labels) < B.davies_bouldin(x, np.array([0, 1, 0, 1]))
    sim = -np.linalg.norm(x[:, None] - x[None], axis=-1)
    ap = B.affinity_propagation(sim, seed=0)
    assert ap[0] == ap[1] != ap[2] == ap[3]
    assert B.max_overlap_assignment(np.array([[0., 2], [3, 0]])) == [(0, 1), (1, 0)]


def test_hetdps_dynamic_sharing_split_and_merge_copy_parameters():
    from latent_team import marl_baselines as B
    copies = []
    far = np.array([[0, 1, 9, 9], [1, 0, 9, 9], [9, 9, 0, 1], [9, 9, 1, 0]], dtype=float)
    first, nets = B.dynamic_parameter_sharing(far, None, None, lambda s, d: copies.append((s, d)), 4, 0)
    assert list(nets) == list(first) and copies == []            # first measurement: network = cluster label
    one_cluster = np.zeros((4, 4))
    _, merged = B.dynamic_parameter_sharing(one_cluster + 1e-3 * (1 - np.eye(4)), first, nets,
                                            lambda s, d: copies.append((s, d)), 4, 0)
    assert len(set(merged)) == 1 and merged[0] == 0               # merge renumbers to network 0


def test_value_norm_and_wasserstein_formulas():
    import torch
    from latent_team import marl_baselines as B
    norm = B.ValueNorm(beta=.5)
    for _ in range(50):
        norm.update(torch.tensor([1., 3.]))
    mean, var = norm.stats()
    assert float(mean) == pytest.approx(2.0, abs=1e-4) and float(var) == pytest.approx(1.0, abs=1e-3)
    mus = torch.tensor([[[0., 0], [3, 4]]]); log_vars = torch.zeros(1, 2, 2)
    assert float(B.gaussian_w2(mus, log_vars)[0, 0, 1]) == pytest.approx(5.0)


@pytest.mark.skipif(not (C.REFERENCE_EXPERIMENT / "experiment.json").exists(),
                    reason="Local reference experiment is not available.")
def test_probe_bank_v2_and_far_goal_variant(tmp_path):
    import json as _json
    from examples import train_recurrent_ippo_consensus as T
    from latent_team import probes_v2 as P2
    from rware.utils.semantic_observation import SEMANTIC_SPATIAL_CHANNELS
    from rware.warehouse import Direction
    job = next(j for j in _json.loads((C.REFERENCE_EXPERIMENT / "experiment.json").read_text(encoding="utf-8"))["jobs"]
               if j["mode"] == "pgct" and j["map"] == "e1")
    kwargs = _json.loads(job["config"]["env_kwargs_json"])
    kwargs.update(P2.ENV_VARIANTS["e1f"])
    bank, summary = P2.build_bank(job["config"]["env_id"], kwargs, seed=1)
    gate, transfer = bank["gate"]["sequences"][:, 0].numpy(), bank["transfer"]["sequences"][:, 0].numpy()
    for seqs in (gate, transfer):
        assert len(np.unique(seqs, axis=0)) == len(seqs)            # no hidden duplicate weights
    goal = SEMANTIC_SPATIAL_CHANNELS.index("goal")
    spatial = gate[:, 20:].reshape(len(gate), len(SEMANTIC_SPATIAL_CHANNELS), 11, 11)
    assert not spatial[:, goal].any()                               # no goal of any team visible at gate probes
    assert {s["phase"] for s in bank["transfer"]["scenarios"]} >= {"search", "carry_goal_hidden", "carry_goal_visible", "return"}
    # Far goals are reachable delivery cells: a loaded agent stepping onto its own corner goal delivers.
    with T.make_env(job["config"]["env_id"], kwargs, "semantic") as env:
        env.reset(seed=1)
        u = env.unwrapped
        assert u.goals_by_team == [[(0, 10)], [(9, 10)]]
        agent, team = u.agents[0], int(u.agent_team_ids[0])
        gx, gy = u.goals_by_team[team][0]
        shelf = u.team_request_queues[team][0]
        for a in u.agents[1:]:
            a.x, a.y = (4 + a.id, 0)
        agent.x, agent.y, agent.dir, agent.carrying_shelf = gx, gy - 1, Direction.DOWN, shelf
        shelf.x, shelf.y = agent.x, agent.y
        u._recalc_grid()
        _, _, _, _, info = env.step([1, 0, 0, 0])  # FORWARD
        assert any(e["goal"] == (gx, gy) for e in info["delivery_events"])


@pytest.mark.skipif(not (C.REFERENCE_EXPERIMENT / "experiment.json").exists(),
                    reason="Local reference experiment is not available.")
def test_e1f_team_reward_plan(tmp_path):
    import json as _json
    from latent_team.train_from_scratch import plan
    common = dict(reference_experiment=C.REFERENCE_EXPERIMENT, maps=["e1"], seeds=[1], modes=["ippo", "oracle"],
                  timesteps=5000000, home_ratio=.5, learning_rate=2e-4, entropy_coef=.05, save_interval=250,
                  track=False, save_video=False, smoke_test=False, eval_seed=5000001, stage_label="test",
                  wandb_project="rware-from-scratch", wandb_mode="online", env_variant="e1f", probe_bank="canonical")
    _, team = plan(SimpleNamespace(output_dir=tmp_path / "team", team_reward="team", **common))
    _, indiv = plan(SimpleNamespace(output_dir=tmp_path / "indiv", **common))   # older callers: no team_reward
    assert team["team_reward"] == "team" and indiv["team_reward"] == "individual"
    assert [j["name"] for j in team["jobs"]] == ["e1f_teamrew_ippo_s1", "e1f_teamrew_oracle_s1"]
    for manifest, reward in ((team, "team"), (indiv, "individual")):
        for job in manifest["jobs"]:
            env = _json.loads(job["config"]["env_kwargs_json"])
            assert env["team_reward_mode"] == reward and env["team_goal_positions"] == [[[0, 10]], [[9, 10]]]
    # Apart from the reward mode, names and tags, the two plans are identical.
    for a, b in zip(team["jobs"], indiv["jobs"]):
        ea, eb = _json.loads(a["config"]["env_kwargs_json"]), _json.loads(b["config"]["env_kwargs_json"])
        assert {k for k in ea if ea[k] != eb[k]} == {"team_reward_mode"}
        diff = {k for k in a["config"] if a["config"][k] != b["config"][k]}
        assert diff <= {"env_kwargs_json", "exp_name", "wandb_name", "wandb_tags", "save_dir", "wandb_group"}


@pytest.mark.skipif(not (C.ROOT / "runs/smoke_e1f_v2_20261015/e1f_ippo_s1/final.pt").exists(),
                    reason="Local E1-F smoke model is not available.")
def test_e1f_divergence_rollout_counts_moves():
    import torch as _torch
    from examples import train_recurrent_ippo_consensus as T
    from examples.diagnose_pgct_rollout_compatibility import load_model
    from latent_team import e1f_team_divergence as D
    path = C.ROOT / "runs/smoke_e1f_v2_20261015/e1f_ippo_s1/final.pt"
    agents, meta = load_model(path)
    env_kwargs = dict(T._load_checkpoint(str(path), _torch.device("cpu"))["effective_env_kwargs"])
    out = D.rollouts(agents, meta["config"]["env_id"], env_kwargs, meta["config"], episodes=1, horizon=20, seed=7)
    assert out["team_ids"] == [0, 1, 0, 1] and out["team_goal_x"] == [0.0, 9.0]
    assert len(out["left_share"]) == 4 and all(v >= 0 for v in out["left_moves"] + out["right_moves"])
