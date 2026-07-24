import os
import sys

import gymnasium as gym
import numpy as np
import pytest


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

from rware.multi_team_grid import GridAction, MultiTeamGrid
from rware.multi_team_warehouse import MultiTeamWarehouse, TeamRewardMode
from rware.warehouse import Action, Direction, RewardType


def test_multiteam_rware_hides_team_info_by_default():
    env = MultiTeamWarehouse(
        shelf_columns=3,
        column_height=8,
        shelf_rows=3,
        n_agents=4,
        msg_bits=0,
        sensor_range=1,
        request_queue_size=4,
        request_queue_size_per_team=2,
        max_inactivity_steps=None,
        max_steps=50,
        reward_type=RewardType.INDIVIDUAL,
        n_teams=2,
        team_assignments=[0, 1, 0, 1],
    )
    obs, info = env.reset(seed=7)

    assert env.observation_space.contains(obs)
    assert "agent_team_ids" not in info
    assert env.get_oracle_team_assignments().tolist() == [0, 1, 0, 1]
    assert len(env.request_queue) == 4
    for team_id, team_queue in enumerate(env.team_request_queues):
        assert len(team_queue) == 2
        assert all(env.shelf_team_ids[shelf.id] == team_id for shelf in team_queue)


def test_multiteam_rware_rewards_only_latent_shelf_team():
    env = MultiTeamWarehouse(
        shelf_columns=3,
        column_height=8,
        shelf_rows=3,
        n_agents=2,
        msg_bits=0,
        sensor_range=1,
        request_queue_size=2,
        request_queue_size_per_team=1,
        max_inactivity_steps=None,
        max_steps=50,
        reward_type=RewardType.INDIVIDUAL,
        n_teams=2,
        team_assignments=[0, 1],
        team_reward_mode=TeamRewardMode.TEAM,
    )
    env.reset(seed=11)

    goal_x, goal_y = env.goals[0]
    shelf = env.shelfs[0]
    env.shelf_team_ids[shelf.id] = 0
    env.shelfs_by_team[0] = [shelf]
    env.team_request_queues = [[shelf], [env.shelfs[1]]]
    env._sync_global_request_queue()

    env.agents[0].x = shelf.x = goal_x
    env.agents[0].y = shelf.y = goal_y - 1
    env.agents[0].dir = Direction.DOWN
    env.agents[0].carrying_shelf = shelf
    env.agents[1].x = 0
    env.agents[1].y = 0
    env.agents[1].dir = Direction.RIGHT
    env._recalc_grid()

    _, rewards, _, _, info = env.step([Action.FORWARD, Action.NOOP])

    assert rewards[0] == pytest.approx(1.0)
    assert rewards[1] == pytest.approx(0.0)
    assert info["deliveries"] == 1


def test_multiteam_rware_reward_shaping_tracks_local_task_progress():
    env = MultiTeamWarehouse(
        shelf_columns=3,
        column_height=1,
        shelf_rows=1,
        n_agents=1,
        msg_bits=0,
        sensor_range=1,
        request_queue_size=1,
        request_queue_size_per_team=1,
        max_inactivity_steps=None,
        max_steps=20,
        reward_type=RewardType.INDIVIDUAL,
        layout=".....\n.x.g.\n.....",
        n_teams=1,
        team_assignments=[0],
        team_reward_mode=TeamRewardMode.INDIVIDUAL,
        requested_shelf_pickup_reward=0.2,
        requested_shelf_progress_reward=0.05,
        goal_progress_reward=0.1,
        premature_drop_penalty=0.15,
        reveal_team_info=True,
    )
    env.reset(seed=13)

    shelf = env.shelfs[0]
    shelf.x = 1
    shelf.y = 1
    env.shelf_team_ids = {shelf.id: 0}
    env.shelfs_by_team = [[shelf]]
    env.team_request_queues = [[shelf]]
    env._sync_global_request_queue()
    env.goals = [(3, 1)]
    env.goals_by_team = [[(3, 1)]]
    env.goal_team_ids = {(3, 1): 0}

    env.agents[0].x = 0
    env.agents[0].y = 1
    env.agents[0].dir = Direction.RIGHT
    env.agents[0].carrying_shelf = None
    env.agents[0].has_delivered = False
    env._recalc_grid()

    _, rewards, _, _, info = env.step([Action.FORWARD])
    assert rewards[0] == pytest.approx(0.05)
    assert info["reward_shaping"][0] == pytest.approx(0.05)

    _, rewards, _, _, _ = env.step([Action.TOGGLE_LOAD])
    assert rewards[0] == pytest.approx(0.2)

    _, rewards, _, _, _ = env.step([Action.TOGGLE_LOAD])
    assert rewards[0] == pytest.approx(-0.15)

    _, rewards, _, _, _ = env.step([Action.TOGGLE_LOAD])
    assert rewards[0] == pytest.approx(0.0)

    _, rewards, _, _, _ = env.step([Action.FORWARD])
    assert rewards[0] == pytest.approx(0.1)

    _, rewards, _, _, info = env.step([Action.FORWARD])
    assert rewards[0] == pytest.approx(1.1)
    assert info["deliveries"] == 1
    assert env.agents[0].has_delivered

    _, rewards, _, _, info = env.step([Action.NOOP])
    assert rewards[0] == pytest.approx(0.0)
    assert info["deliveries"] == 0


def test_multiteam_rware_movement_shaping_discourages_idle_actions():
    env = MultiTeamWarehouse(
        shelf_columns=3,
        column_height=1,
        shelf_rows=1,
        n_agents=1,
        msg_bits=0,
        sensor_range=1,
        request_queue_size=1,
        request_queue_size_per_team=1,
        max_inactivity_steps=None,
        max_steps=20,
        reward_type=RewardType.INDIVIDUAL,
        layout=".....\n.x.g.\n.....",
        n_teams=1,
        team_assignments=[0],
        team_reward_mode=TeamRewardMode.INDIVIDUAL,
        forward_movement_reward=0.03,
        stationary_action_penalty=0.04,
        reveal_team_info=True,
    )
    env.reset(seed=17)

    shelf = env.shelfs[0]
    shelf.x = 3
    shelf.y = 1
    env.shelf_team_ids = {shelf.id: 0}
    env.shelfs_by_team = [[shelf]]
    env.team_request_queues = [[shelf]]
    env._sync_global_request_queue()

    env.agents[0].x = 1
    env.agents[0].y = 1
    env.agents[0].dir = Direction.RIGHT
    env.agents[0].carrying_shelf = None
    env._recalc_grid()

    _, rewards, _, _, info = env.step([Action.LEFT])
    assert rewards[0] == pytest.approx(-0.04)
    assert info["reward_shaping"][0] == pytest.approx(-0.04)

    _, rewards, _, _, info = env.step([Action.FORWARD])
    assert rewards[0] == pytest.approx(0.03)
    assert info["reward_shaping"][0] == pytest.approx(0.03)


def test_multiteam_grid_collection_and_hidden_oracle():
    env = MultiTeamGrid(
        grid_size=(6, 6),
        n_agents=2,
        n_teams=2,
        sensor_range=1,
        max_steps=10,
        team_assignments=[0, 1],
        targets_per_team=1,
        obstacle_density=0.0,
        team_reward_mode=TeamRewardMode.TEAM,
    )
    obs, info = env.reset(seed=3)

    assert env.observation_space.contains(obs)
    assert "agent_team_ids" not in info
    assert env.get_oracle_team_assignments().tolist() == [0, 1]

    env.agent_positions = np.asarray([[1, 1], [4, 4]], dtype=np.int32)
    env.target_positions = {(2, 1): 0}

    obs, rewards, done, truncated, info = env.step([GridAction.DOWN, GridAction.NOOP])

    assert env.observation_space.contains(obs)
    assert rewards == pytest.approx([1.0, 0.0])
    assert not done
    assert not truncated
    assert info["collections"] == 1
    assert len(env.target_positions) == 1


def test_registered_multiteam_envs_can_step():
    import rware  # noqa: F401

    for env_id in [
        "rware-multiteam-tiny-4ag-2teams-v0",
        "mtgrid-small-4ag-2teams-v0",
    ]:
        env = gym.make(env_id)
        obs, info = env.reset(seed=5)
        assert env.observation_space.contains(obs)
        assert "agent_team_ids" not in info
        obs, rewards, done, truncated, info = env.step(env.action_space.sample())
        assert env.observation_space.contains(obs)
        assert len(rewards) == env.unwrapped.n_agents
