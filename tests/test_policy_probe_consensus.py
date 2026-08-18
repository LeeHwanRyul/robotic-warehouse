import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest
import gymnasium as gym


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

torch = pytest.importorskip("torch")

from examples.train_recurrent_ippo_consensus import (  # noqa: E402
    RecurrentActorCritic,
    TeamGraphEstimator,
    _objective_visibility_scores,
    adjusted_rand_index,
    apply_agent_overrides,
    apply_confidence_weighted_critic_consensus,
    build_objective_probe_bank,
    critic_parameter_groups,
    normalized_mutual_info,
    parse_curriculum_stages,
    parse_transfer_components,
    policy_distance_similarity_matrices,
    recurrent_critic_probe_values,
    resolve_agent_count,
    transfer_checkpoint_to_agents,
)
from rware.multi_team_grid import MultiTeamGrid  # noqa: E402
from rware.utils.probe_maps import RwareObjectiveProbeMapBuilder  # noqa: E402


def test_policy_similarity_graph_respects_neighbor_adjacency():
    estimator = TeamGraphEstimator(
        n_agents=3,
        edge_threshold=0.05,
        min_probe_count=1,
        uncertainty_scale=0.0,
        value_uncertainty_decay=0.95,
    )
    similarity = np.eye(3, dtype=np.float32)
    similarity[0, 1] = similarity[1, 0] = 0.9
    similarity[1, 2] = similarity[2, 1] = 0.9
    neighbor_adjacency = np.zeros((3, 3), dtype=np.float32)
    neighbor_adjacency[0, 1] = neighbor_adjacency[1, 0] = 1.0

    updates = estimator.update_from_policy_similarity(
        similarity,
        neighbor_adjacency,
    )
    weights = estimator.weight_matrix()

    assert updates == 1
    assert weights[0, 1] > 0.0
    assert weights[1, 2] == pytest.approx(0.0)


def test_policy_probe_sequences_produce_distance_and_similarity():
    agents = [
        RecurrentActorCritic(obs_dim=3, action_dim=2, mlp_hidden_dim=4, recurrent_hidden_dim=4),
        RecurrentActorCritic(obs_dim=3, action_dim=2, mlp_hidden_dim=4, recurrent_hidden_dim=4),
    ]
    agents[1].load_state_dict(agents[0].state_dict())
    probe_sequences = torch.randn(5, 3, 3)

    distance, similarity = policy_distance_similarity_matrices(
        agents,
        probe_sequences,
        device=torch.device("cpu"),
        temperature=0.25,
    )
    assert distance[0, 1] == pytest.approx(0.0, abs=1e-7)
    assert similarity[0, 1] == pytest.approx(1.0)

    with torch.no_grad():
        agents[1].actor_head.bias[0] += 5.0
    distance, similarity = policy_distance_similarity_matrices(
        agents,
        probe_sequences,
        device=torch.device("cpu"),
        temperature=0.25,
    )
    assert distance[0, 1] > 0.0
    assert 0.0 <= similarity[0, 1] < 1.0


def test_pgct_distance_gate_and_receiver_allocation():
    estimator = TeamGraphEstimator(
        n_agents=3,
        edge_threshold=0.2,
        min_probe_count=1,
        uncertainty_scale=0.0,
        value_uncertainty_decay=0.95,
    )
    distance = np.asarray(
        [
            [0.0, 0.05, 0.4],
            [0.05, 0.0, 0.5],
            [0.4, 0.5, 0.0],
        ],
        dtype=np.float32,
    )
    neighbor_adjacency = np.ones((3, 3), dtype=np.float32)
    np.fill_diagonal(neighbor_adjacency, 0.0)

    updates = estimator.update_from_policy_distance(
        distance,
        neighbor_adjacency,
        beta=0.5,
    )
    gate = estimator.pgct_gate_matrix(
        warmup_complete=True,
        distance_threshold=0.2,
        distance_temperature=0.25,
        gate_power=1.0,
    )
    allocation = estimator.pgct_allocation_matrix(
        warmup_complete=True,
        distance_threshold=0.2,
        distance_temperature=0.25,
        gate_power=1.0,
        alpha_epsilon=1e-8,
    )

    assert updates == 3
    assert gate[0, 1] > 0.0
    assert gate[1, 0] == pytest.approx(gate[0, 1])
    assert gate[0, 2] == pytest.approx(0.0)
    assert allocation[0, 1] == pytest.approx(1.0)
    assert allocation[2].sum() == pytest.approx(0.0)


def test_pgct_peer_loss_backpropagates_only_through_receiver_critic():
    receiver = RecurrentActorCritic(
        obs_dim=3,
        action_dim=2,
        mlp_hidden_dim=4,
        recurrent_hidden_dim=4,
    )
    donor = RecurrentActorCritic(
        obs_dim=3,
        action_dim=2,
        mlp_hidden_dim=4,
        recurrent_hidden_dim=4,
    )
    probe_sequences = torch.randn(4, 2, 3)

    receiver_values = recurrent_critic_probe_values(
        receiver,
        probe_sequences,
        torch.device("cpu"),
    )
    donor_values = recurrent_critic_probe_values(
        donor,
        probe_sequences,
        torch.device("cpu"),
    ).detach()
    loss = (receiver_values - donor_values).pow(2).mean()
    loss.backward()

    assert all(param.grad is None for param in receiver.actor_parameters())
    assert any(
        param.grad is not None and torch.any(param.grad != 0.0)
        for param in receiver.critic_parameters()
    )
    assert all(param.grad is None for param in donor.parameters())


def test_objective_probe_bank_exposes_grid_targets():
    env = MultiTeamGrid(
        grid_size=(6, 6),
        n_agents=2,
        n_teams=2,
        sensor_range=1,
        obstacle_density=0.0,
        targets_per_team=1,
    )
    env.reset(seed=3)
    obs_dim = env.observation_space[0].shape[0]

    probes = build_objective_probe_bank(
        env,
        obs_dim=obs_dim,
        batch_size=9,
        rng=np.random.default_rng(0),
    )
    scores = _objective_visibility_scores(env, probes)

    assert probes.shape == (9, obs_dim)
    assert np.count_nonzero(scores > 0.0) >= 6


def test_rware_objective_probe_bank_exposes_team_goal_and_return_scenarios():
    env = gym.make(
        "rware-multiteam-tiny-4ag-2teams-v0",
        sensor_range=3,
        request_queue_size=2,
        request_queue_size_per_team=1,
        require_delivered_shelf_return=True,
        reveal_team_info=True,
    )
    env.reset(seed=11)
    obs_dim = env.observation_space[0].shape[0]
    builder = RwareObjectiveProbeMapBuilder(
        env,
        obs_dim=obs_dim,
        rng=np.random.default_rng(0),
    )
    unwrapped = builder.probe_unwrapped

    probes = builder.build(batch_size=48)
    scores = _objective_visibility_scores(env, probes)
    probe_np = probes.numpy()
    carrying = probe_np[:, 2] > 0.5
    positions = [
        (int(round(float(probe[0]))), int(round(float(probe[1]))))
        for probe in probe_np
    ]
    self_bits = int(unwrapped._obs_bits_for_self)
    per_agent = int(unwrapped._obs_bits_per_agent)
    per_shelf = int(unwrapped._obs_bits_per_shelf)
    cell_stride = per_agent + per_shelf
    sensor_locations = (1 + 2 * int(unwrapped.sensor_range)) ** 2

    requested_shelf_counts = []
    for probe in probe_np:
        requested_count = 0
        for loc in range(sensor_locations):
            base = self_bits + loc * cell_stride + per_agent
            if probe[base] > 0.5 and probe[base + 1] > 0.5:
                requested_count += 1
        requested_shelf_counts.append(requested_count)

    for team_id, team_goals in enumerate(unwrapped.goals_by_team):
        assert any(
            carrying[idx]
            and any(
                abs(x - int(goal[0])) + abs(y - int(goal[1])) <= 1
                for goal in team_goals
            )
            for idx, (x, y) in enumerate(positions)
        ), f"missing carrying probe around team {team_id} goal"

        team_homes = {
            tuple(map(int, unwrapped._shelf_home_positions[shelf.id]))
            for shelf in unwrapped.shelfs_by_team[team_id]
        }
        assert any(
            carrying[idx] and (x, y) in team_homes
            for idx, (x, y) in enumerate(positions)
        ), f"missing return-at-home probe for team {team_id}"

    dual_requested_probe_count = sum(
        count >= 2 for count in requested_shelf_counts
    )

    assert probes.shape == (48, obs_dim)
    assert np.count_nonzero(scores > 0.0) >= 36
    assert max(requested_shelf_counts) >= 2
    assert dual_requested_probe_count >= 24
    env.close()


def test_rware_probe_map_builder_saves_visual_manifest(tmp_path):
    pytest.importorskip("PIL")
    env = gym.make(
        "rware-multiteam-tiny-4ag-2teams-v0",
        sensor_range=3,
        request_queue_size=2,
        request_queue_size_per_team=1,
        require_delivered_shelf_return=True,
        reveal_team_info=True,
    )
    try:
        env.reset(seed=11)
        obs_dim = env.observation_space[0].shape[0]
        builder = RwareObjectiveProbeMapBuilder(
            env,
            obs_dim=obs_dim,
            rng=np.random.default_rng(0),
        )
        summary = builder.save_probe_map_images(
            tmp_path,
            batch_size=32,
            save_individual=False,
            save_contact_sheet=True,
        )

        manifest_path = Path(summary["manifest"])
        contact_sheet_path = Path(summary["contact_sheet"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert len(builder.scenario_cycle) == 48
        assert len(manifest) == 32
        assert contact_sheet_path.exists()
        assert any(row["requested_shelf_count"] >= 2 for row in manifest)
    finally:
        env.close()


def test_graph_hysteresis_requires_dwell_before_edge_change():
    estimator = TeamGraphEstimator(
        n_agents=2,
        edge_threshold=0.5,
        min_probe_count=1,
        uncertainty_scale=0.0,
        value_uncertainty_decay=0.95,
        join_threshold=0.6,
        leave_threshold=0.4,
        dwell_updates=2,
    )

    estimator.update_pair_score(0, 1, 1.0)
    assert estimator.update_stable_adjacency()[0, 1] == pytest.approx(0.0)
    estimator.update_pair_score(0, 1, 1.0)
    assert estimator.update_stable_adjacency()[0, 1] == pytest.approx(1.0)

    estimator.count[0, 1] = 1.0
    estimator.mean[0, 1] = 0.0
    estimator.m2[0, 1] = 0.0
    assert estimator.update_stable_adjacency()[0, 1] == pytest.approx(1.0)
    assert estimator.update_stable_adjacency()[0, 1] == pytest.approx(0.0)


def test_confidence_weighted_critic_consensus_uses_edge_weights():
    agents = [
        RecurrentActorCritic(obs_dim=2, action_dim=2, mlp_hidden_dim=4, recurrent_hidden_dim=4),
        RecurrentActorCritic(obs_dim=2, action_dim=2, mlp_hidden_dim=4, recurrent_hidden_dim=4),
    ]
    for param in critic_parameter_groups(agents[0]):
        param.data.zero_()
    for param in critic_parameter_groups(agents[1]):
        param.data.fill_(1.0)

    weights = np.asarray([[0.0, 0.5], [0.5, 0.0]], dtype=np.float32)
    updates = apply_confidence_weighted_critic_consensus(
        agents,
        weights,
        tau=0.1,
        min_weight=0.2,
    )

    assert updates == 1
    for param in critic_parameter_groups(agents[0]):
        assert torch.allclose(param.data, torch.full_like(param.data, 0.05))
    for param in critic_parameter_groups(agents[1]):
        assert torch.allclose(param.data, torch.full_like(param.data, 0.95))


def test_clustering_scores_are_perfect_for_same_partition():
    true_labels = np.asarray([0, 1, 0, 1], dtype=np.int32)
    pred_labels = np.asarray([0, 1, 0, 1], dtype=np.int32)

    assert adjusted_rand_index(true_labels, pred_labels) == pytest.approx(1.0)
    assert normalized_mutual_info(true_labels, pred_labels) == pytest.approx(1.0)


def test_curriculum_stage_selects_agent_count_and_env_override():
    stages = parse_curriculum_stages("4->8->12")

    assert stages == [4, 8, 12]
    assert resolve_agent_count(0, stages, 2) == 8
    assert resolve_agent_count(6, stages, 0) == 6

    env_kwargs = apply_agent_overrides(
        "rware-multiteam-tiny-4ag-2teams-v0",
        {"sensor_range": 2},
        agent_count=8,
        team_count=2,
    )

    assert env_kwargs["n_agents"] == 8
    assert env_kwargs["n_teams"] == 2
    assert env_kwargs["sensor_range"] == 2
    assert env_kwargs["request_queue_size_per_team"] == 4
    assert env_kwargs["request_queue_size"] == 8

    first_stage_kwargs = apply_agent_overrides(
        "rware-multiteam-tiny-4ag-2teams-v0",
        {"sensor_range": 2},
        agent_count=2,
        team_count=2,
    )

    assert first_stage_kwargs["request_queue_size_per_team"] == 1
    assert first_stage_kwargs["request_queue_size"] == 2

    explicit_queue_kwargs = apply_agent_overrides(
        "rware-multiteam-tiny-4ag-2teams-v0",
        {"request_queue_size_per_team": 3},
        agent_count=2,
        team_count=2,
    )

    assert explicit_queue_kwargs["request_queue_size_per_team"] == 3
    assert explicit_queue_kwargs["request_queue_size"] == 6

    low_queue_kwargs = apply_agent_overrides(
        "rware-multiteam-tiny-4ag-2teams-v0",
        {"request_queue_size": 1, "request_queue_size_per_team": 1},
        agent_count=4,
        team_count=2,
    )

    assert low_queue_kwargs["request_queue_size_per_team"] == 2
    assert low_queue_kwargs["request_queue_size"] == 4

    preserved_low_queue_kwargs = apply_agent_overrides(
        "rware-multiteam-tiny-4ag-2teams-v0",
        {"request_queue_size": 1, "request_queue_size_per_team": 1},
        agent_count=4,
        team_count=2,
        auto_scale_request_queue=False,
    )

    assert preserved_low_queue_kwargs["request_queue_size_per_team"] == 1
    assert preserved_low_queue_kwargs["request_queue_size"] == 1


def test_curriculum_transfer_copies_actor_round_robin_and_resets_critic(tmp_path):
    source_agents = [
        RecurrentActorCritic(obs_dim=3, action_dim=2, mlp_hidden_dim=4, recurrent_hidden_dim=4),
        RecurrentActorCritic(obs_dim=3, action_dim=2, mlp_hidden_dim=4, recurrent_hidden_dim=4),
    ]
    for value, agent in zip([0.25, 0.5], source_agents):
        for param in agent.actor_parameters():
            param.data.fill_(value)
        for param in agent.critic_parameters():
            param.data.fill_(0.75)

    checkpoint_path = tmp_path / "stage1.pt"
    torch.save({"agents": [agent.state_dict() for agent in source_agents]}, checkpoint_path)

    target_agents = [
        RecurrentActorCritic(obs_dim=3, action_dim=2, mlp_hidden_dim=4, recurrent_hidden_dim=4)
        for _ in range(5)
    ]
    critic_before = [
        [param.detach().clone() for param in agent.critic_parameters()]
        for agent in target_agents
    ]

    report = transfer_checkpoint_to_agents(
        str(checkpoint_path),
        target_agents,
        parse_transfer_components("actor"),
        torch.device("cpu"),
    )

    assert report["mapping"] == [0, 1, 0, 1, 0]
    assert report["copied_tensors"] > 0
    for agent_id, agent in enumerate(target_agents):
        expected = 0.25 if agent_id % 2 == 0 else 0.5
        for param in agent.actor_parameters():
            assert torch.allclose(param, torch.full_like(param, expected))
        for before, param in zip(critic_before[agent_id], agent.critic_parameters()):
            assert torch.allclose(param, before)

def test_curriculum_transfer_actor_body_leaves_policy_head_fresh(tmp_path):
    source_agent = RecurrentActorCritic(
        obs_dim=3,
        action_dim=2,
        mlp_hidden_dim=4,
        recurrent_hidden_dim=4,
    )
    for name, param in source_agent.named_parameters():
        if name.startswith("actor_"):
            param.data.fill_(0.5)
        if name.startswith("critic_"):
            param.data.fill_(0.75)

    checkpoint_path = tmp_path / "stage1.pt"
    torch.save({"agents": [source_agent.state_dict()]}, checkpoint_path)

    target_agent = RecurrentActorCritic(
        obs_dim=3,
        action_dim=2,
        mlp_hidden_dim=4,
        recurrent_hidden_dim=4,
    )
    head_before = {
        name: param.detach().clone()
        for name, param in target_agent.named_parameters()
        if name.startswith("actor_head.")
    }
    critic_before = {
        name: param.detach().clone()
        for name, param in target_agent.named_parameters()
        if name.startswith("critic_")
    }

    report = transfer_checkpoint_to_agents(
        str(checkpoint_path),
        [target_agent],
        parse_transfer_components("actor_body"),
        torch.device("cpu"),
    )

    assert report["components"] == ["actor_body"]
    assert report["copied_tensors"] > 0
    for name, param in target_agent.named_parameters():
        if name.startswith(("actor_encoder.", "actor_rnn.")):
            assert torch.allclose(param, torch.full_like(param, 0.5))
        elif name.startswith("actor_head."):
            assert torch.allclose(param, head_before[name])
        elif name.startswith("critic_"):
            assert torch.allclose(param, critic_before[name])
