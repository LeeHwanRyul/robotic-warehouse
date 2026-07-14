import os
import sys

import numpy as np
import pytest


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

torch = pytest.importorskip("torch")

from examples.train_recurrent_ippo_consensus import (  # noqa: E402
    RecurrentActorCritic,
    TeamGraphEstimator,
    _objective_visibility_scores,
    adjusted_rand_index,
    apply_confidence_weighted_critic_consensus,
    build_objective_probe_bank,
    critic_parameter_groups,
    normalized_mutual_info,
)
from rware.multi_team_grid import MultiTeamGrid  # noqa: E402


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
