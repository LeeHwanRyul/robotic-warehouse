"""Recurrent IPPO with sparse probing and clustered critic consensus.

This script is meant for the RWARE multi-team environments in this repository.
It implements:

- fully decentralized recurrent actors and critics,
- IPPO-style clipped policy/value updates,
- sparse counterfactual probing for latent team influence discovery,
- uncertainty-aware graph construction from probe and critic-error statistics,
- clustered critic consensus by soft parameter averaging inside inferred teams.

Example:
    python examples/train_recurrent_ippo_consensus.py \
        --env-id rware-multiteam-tiny-4ag-2teams-v0 \
        --total-timesteps 200000
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import gymnasium as gym
import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import rware  # noqa: F401 - registers Gymnasium environments


TensorPair = Tuple[torch.Tensor, torch.Tensor]


def mlp(input_dim: int, hidden_dim: int, output_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(input_dim, hidden_dim),
        nn.Tanh(),
        nn.Linear(hidden_dim, hidden_dim),
        nn.Tanh(),
        nn.Linear(hidden_dim, output_dim),
        nn.Tanh(),
    )


class RecurrentActorCritic(nn.Module):
    """One local recurrent actor-critic used by one agent.

    The actor and critic only receive that agent's local observation. They do not
    receive global state, other agents' actions, or oracle team IDs.
    """

    def __init__(
        self,
        obs_dim: int,
        action_dim: int,
        mlp_hidden_dim: int = 128,
        recurrent_hidden_dim: int = 128,
    ):
        super().__init__()
        self.obs_dim = int(obs_dim)
        self.action_dim = int(action_dim)
        self.recurrent_hidden_dim = int(recurrent_hidden_dim)

        self.actor_encoder = mlp(obs_dim, mlp_hidden_dim, recurrent_hidden_dim)
        self.actor_rnn = nn.GRUCell(recurrent_hidden_dim, recurrent_hidden_dim)
        self.actor_head = nn.Linear(recurrent_hidden_dim, action_dim)

        self.critic_encoder = mlp(obs_dim, mlp_hidden_dim, recurrent_hidden_dim)
        self.critic_rnn = nn.GRUCell(recurrent_hidden_dim, recurrent_hidden_dim)
        self.critic_head = nn.Linear(recurrent_hidden_dim, 1)

        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.orthogonal_(module.weight, gain=math.sqrt(2))
                nn.init.constant_(module.bias, 0.0)
        nn.init.orthogonal_(self.actor_head.weight, gain=0.01)
        nn.init.orthogonal_(self.critic_head.weight, gain=1.0)

    def initial_hidden(self, batch_size: int, device: torch.device) -> TensorPair:
        shape = (batch_size, self.recurrent_hidden_dim)
        return torch.zeros(shape, device=device), torch.zeros(shape, device=device)

    def actor_parameters(self) -> Iterable[nn.Parameter]:
        yield from self.actor_encoder.parameters()
        yield from self.actor_rnn.parameters()
        yield from self.actor_head.parameters()

    def critic_parameters(self) -> Iterable[nn.Parameter]:
        yield from self.critic_encoder.parameters()
        yield from self.critic_rnn.parameters()
        yield from self.critic_head.parameters()

    def _actor_step(
        self,
        obs: torch.Tensor,
        actor_h: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.actor_encoder(obs)
        next_h = self.actor_rnn(features, actor_h)
        logits = self.actor_head(next_h)
        return logits, next_h

    def _critic_step(
        self,
        obs: torch.Tensor,
        critic_h: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.critic_encoder(obs)
        next_h = self.critic_rnn(features, critic_h)
        value = self.critic_head(next_h).squeeze(-1)
        return value, next_h

    @torch.no_grad()
    def act(
        self,
        obs: torch.Tensor,
        actor_h: torch.Tensor,
        critic_h: torch.Tensor,
        deterministic: bool = False,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if obs.ndim == 1:
            obs = obs.unsqueeze(0)
        if actor_h.ndim == 1:
            actor_h = actor_h.unsqueeze(0)
        if critic_h.ndim == 1:
            critic_h = critic_h.unsqueeze(0)

        logits, next_actor_h = self._actor_step(obs, actor_h)
        value, next_critic_h = self._critic_step(obs, critic_h)
        dist = Categorical(logits=logits)
        if deterministic:
            action = torch.argmax(logits, dim=-1)
        else:
            action = dist.sample()
        log_prob = dist.log_prob(action)
        return action, log_prob, value, next_actor_h, next_critic_h

    def evaluate_actions(
        self,
        obs_seq: torch.Tensor,
        action_seq: torch.Tensor,
        done_seq: torch.Tensor,
        actor_h0: torch.Tensor,
        critic_h0: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Evaluate a time-major recurrent minibatch.

        Args:
            obs_seq: [T, B, obs_dim]
            action_seq: [T, B]
            done_seq: [T, B], terminal flags after each step.
            actor_h0: [B, H], hidden state before obs_seq[0].
            critic_h0: [B, H], hidden state before obs_seq[0].
        """
        actor_h = actor_h0
        critic_h = critic_h0
        log_probs: List[torch.Tensor] = []
        entropies: List[torch.Tensor] = []
        values: List[torch.Tensor] = []

        for obs_t, action_t, done_t in zip(obs_seq, action_seq, done_seq):
            logits, actor_h = self._actor_step(obs_t, actor_h)
            value, critic_h = self._critic_step(obs_t, critic_h)
            dist = Categorical(logits=logits)
            log_probs.append(dist.log_prob(action_t))
            entropies.append(dist.entropy())
            values.append(value)

            keep_hidden = (1.0 - done_t.float()).unsqueeze(-1)
            actor_h = actor_h * keep_hidden
            critic_h = critic_h * keep_hidden

        return (
            torch.stack(log_probs, dim=0),
            torch.stack(entropies, dim=0),
            torch.stack(values, dim=0),
        )


@dataclass
class Rollout:
    obs: torch.Tensor
    actions: torch.Tensor
    old_log_probs: torch.Tensor
    rewards: torch.Tensor
    dones: torch.Tensor
    values: torch.Tensor
    actor_h: torch.Tensor
    critic_h: torch.Tensor
    last_values: torch.Tensor


@dataclass
class RunnerState:
    obs: Sequence[np.ndarray]
    actor_h: torch.Tensor
    critic_h: torch.Tensor
    episode_returns: np.ndarray
    episode_length: int = 0


@dataclass
class TrainConfig:
    env_id: str
    env_kwargs_json: str
    total_timesteps: int
    rollout_steps: int
    sequence_length: int
    minibatch_chunks: int
    ppo_epochs: int
    learning_rate: float
    gamma: float
    gae_lambda: float
    clip_coef: float
    value_clip_coef: float
    value_loss_coef: float
    entropy_coef: float
    max_grad_norm: float
    mlp_hidden_dim: int
    recurrent_hidden_dim: int
    seed: int
    device: str
    graph_mode: str
    probe_interval: int
    probe_episodes: int
    probe_horizon: int
    edge_threshold: float
    min_probe_count: int
    uncertainty_scale: float
    value_uncertainty_decay: float
    critic_consensus_tau: float
    consensus_interval: int
    save_dir: str
    exp_name: str
    save_interval: int
    log_interval: int
    eval_episodes: int
    eval_horizon: int
    eval_interval: int
    render_eval: bool
    eval_render_episodes: int
    eval_render_mode: str
    eval_render_fps: int
    track: bool
    wandb_project: str
    wandb_entity: str
    wandb_group: str
    wandb_name: str
    wandb_mode: str
    wandb_tags: str
    wandb_log_eval_video: bool


class TeamGraphEstimator:
    """Probe-driven latent team graph with uncertainty-aware edge scores."""

    def __init__(
        self,
        n_agents: int,
        edge_threshold: float,
        min_probe_count: int,
        uncertainty_scale: float,
        value_uncertainty_decay: float,
    ):
        self.n_agents = int(n_agents)
        self.edge_threshold = float(edge_threshold)
        self.min_probe_count = int(min_probe_count)
        self.uncertainty_scale = float(uncertainty_scale)
        self.value_uncertainty_decay = float(value_uncertainty_decay)

        shape = (self.n_agents, self.n_agents)
        self.count = np.zeros(shape, dtype=np.float64)
        self.mean = np.zeros(shape, dtype=np.float64)
        self.m2 = np.zeros(shape, dtype=np.float64)
        self.value_uncertainty = np.ones(self.n_agents, dtype=np.float64)

    def update_from_counterfactual(
        self,
        source_agent: int,
        delta_returns: np.ndarray,
    ) -> None:
        source_agent = int(source_agent)
        deltas = np.abs(np.asarray(delta_returns, dtype=np.float64))
        for target_agent, value in enumerate(deltas):
            if target_agent == source_agent:
                continue
            self.count[source_agent, target_agent] += 1.0
            n = self.count[source_agent, target_agent]
            old_mean = self.mean[source_agent, target_agent]
            new_mean = old_mean + (float(value) - old_mean) / n
            self.mean[source_agent, target_agent] = new_mean
            self.m2[source_agent, target_agent] += (float(value) - old_mean) * (
                float(value) - new_mean
            )

    def update_value_uncertainty(self, per_agent_abs_td_error: np.ndarray) -> None:
        errors = np.asarray(per_agent_abs_td_error, dtype=np.float64)
        if errors.shape != (self.n_agents,):
            raise ValueError("per_agent_abs_td_error must have shape (n_agents,)")
        decay = self.value_uncertainty_decay
        self.value_uncertainty = decay * self.value_uncertainty + (1.0 - decay) * errors

    def _directed_std(self, i: int, j: int) -> float:
        n = self.count[i, j]
        if n <= 1.0:
            return 1.0
        return float(math.sqrt(max(self.m2[i, j] / (n - 1.0), 0.0)))

    def pair_score(self, i: int, j: int) -> Tuple[float, float, float]:
        count = self.count[i, j] + self.count[j, i]
        if count <= 0.0:
            return 0.0, 0.0, 1.0

        weighted_influence = (
            self.mean[i, j] * self.count[i, j] + self.mean[j, i] * self.count[j, i]
        ) / max(count, 1.0)
        directed_std = (
            self._directed_std(i, j) * self.count[i, j]
            + self._directed_std(j, i) * self.count[j, i]
        ) / max(count, 1.0)
        standard_error = directed_std / math.sqrt(max(count, 1.0))
        critic_uncertainty = 0.5 * (
            self.value_uncertainty[i] + self.value_uncertainty[j]
        )
        count_confidence = 1.0 - math.exp(-count / max(self.min_probe_count, 1))
        confidence = count_confidence * math.exp(
            -self.uncertainty_scale * (standard_error + critic_uncertainty)
        )
        score = weighted_influence * confidence
        return float(score), float(weighted_influence), float(standard_error)

    def adjacency(self) -> np.ndarray:
        adj = np.zeros((self.n_agents, self.n_agents), dtype=np.float32)
        for i in range(self.n_agents):
            for j in range(i + 1, self.n_agents):
                count = self.count[i, j] + self.count[j, i]
                if count < self.min_probe_count:
                    continue
                score, _, _ = self.pair_score(i, j)
                if score >= self.edge_threshold:
                    adj[i, j] = 1.0
                    adj[j, i] = 1.0
        return adj

    def clusters(self) -> List[List[int]]:
        adj = self.adjacency()
        seen = np.zeros(self.n_agents, dtype=bool)
        clusters: List[List[int]] = []
        for start in range(self.n_agents):
            if seen[start]:
                continue
            stack = [start]
            seen[start] = True
            cluster = []
            while stack:
                node = stack.pop()
                cluster.append(node)
                neighbors = np.flatnonzero(adj[node] > 0.0).tolist()
                for nxt in neighbors:
                    if not seen[nxt]:
                        seen[nxt] = True
                        stack.append(int(nxt))
            clusters.append(sorted(cluster))
        return clusters

    def state_dict(self) -> Dict[str, np.ndarray]:
        return {
            "count": self.count.copy(),
            "mean": self.mean.copy(),
            "m2": self.m2.copy(),
            "value_uncertainty": self.value_uncertainty.copy(),
        }


def parse_env_kwargs(env_kwargs_json: str) -> Dict:
    try:
        value = json.loads(env_kwargs_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid --env-kwargs-json: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("--env-kwargs-json must decode to a JSON object")
    return value


def init_wandb(cfg: TrainConfig, save_dir: Path):
    if not cfg.track:
        return None
    try:
        import wandb
    except ImportError as exc:
        raise ImportError(
            "wandb is required when --track is set. Install with "
            '`pip install -e ".[rl]"` or `pip install wandb`.'
        ) from exc

    tags = [tag.strip() for tag in cfg.wandb_tags.split(",") if tag.strip()]
    return wandb.init(
        project=cfg.wandb_project,
        entity=cfg.wandb_entity or None,
        group=cfg.wandb_group or None,
        name=cfg.wandb_name or (cfg.exp_name or None),
        mode=cfg.wandb_mode,
        tags=tags or None,
        config=asdict(cfg),
        dir=str(save_dir),
        save_code=True,
    )


def make_render_env_kwargs(env_kwargs: Dict, render_mode: str) -> Dict:
    render_kwargs = dict(env_kwargs)
    render_kwargs["render_mode"] = render_mode
    return render_kwargs


def make_env(env_id: str, env_kwargs: Dict) -> gym.Env:
    return gym.make(env_id, **env_kwargs)


def tuple_spaces(space: gym.Space) -> List[gym.Space]:
    if not isinstance(space, gym.spaces.Tuple):
        raise ValueError("Expected a multi-agent Tuple space")
    return list(space.spaces)


def get_flat_obs_dims(env: gym.Env) -> List[int]:
    return [gym.spaces.flatdim(space) for space in tuple_spaces(env.observation_space)]


def get_discrete_action_dims(env: gym.Env) -> List[int]:
    dims = []
    for space in tuple_spaces(env.action_space):
        if not isinstance(space, gym.spaces.Discrete):
            raise ValueError(
                "This implementation expects msg_bits=0 and Discrete actions. "
                f"Got {space!r}."
            )
        dims.append(int(space.n))
    return dims


def flatten_multi_agent_obs(env: gym.Env, obs: Sequence) -> np.ndarray:
    flat_obs = [
        gym.spaces.flatten(space, agent_obs).astype(np.float32)
        for space, agent_obs in zip(tuple_spaces(env.observation_space), obs)
    ]
    return np.stack(flat_obs, axis=0)


def set_global_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def set_env_training_edges(env: gym.Env, adjacency: np.ndarray) -> None:
    unwrapped = env.unwrapped
    if not hasattr(unwrapped, "set_training_comm_edges"):
        return
    edges = []
    for i in range(adjacency.shape[0]):
        for j in range(i + 1, adjacency.shape[1]):
            if adjacency[i, j] > 0.0:
                edges.append((i, j))
    unwrapped.set_training_comm_edges(edges)


def oracle_clusters(env: gym.Env) -> Optional[List[List[int]]]:
    unwrapped = env.unwrapped
    if not hasattr(unwrapped, "get_team_members"):
        return None
    return [list(map(int, members)) for members in unwrapped.get_team_members()]


def collect_rollout(
    env: gym.Env,
    agents: Sequence[RecurrentActorCritic],
    state: RunnerState,
    rollout_steps: int,
    obs_dim: int,
    recurrent_hidden_dim: int,
    device: torch.device,
) -> Tuple[Rollout, RunnerState, Dict[str, float]]:
    n_agents = len(agents)

    obs_buf = torch.zeros((rollout_steps, n_agents, obs_dim), dtype=torch.float32)
    actions_buf = torch.zeros((rollout_steps, n_agents), dtype=torch.long)
    logprob_buf = torch.zeros((rollout_steps, n_agents), dtype=torch.float32)
    rewards_buf = torch.zeros((rollout_steps, n_agents), dtype=torch.float32)
    dones_buf = torch.zeros((rollout_steps,), dtype=torch.float32)
    values_buf = torch.zeros((rollout_steps, n_agents), dtype=torch.float32)
    actor_h_buf = torch.zeros(
        (rollout_steps, n_agents, recurrent_hidden_dim), dtype=torch.float32
    )
    critic_h_buf = torch.zeros_like(actor_h_buf)

    completed_returns: List[float] = []
    completed_lengths: List[int] = []
    completed_team_events: List[float] = []

    for step in range(rollout_steps):
        flat_obs = flatten_multi_agent_obs(env, state.obs)
        obs_tensor = torch.as_tensor(flat_obs, dtype=torch.float32, device=device)
        obs_buf[step] = obs_tensor.cpu()
        actor_h_buf[step] = state.actor_h.cpu()
        critic_h_buf[step] = state.critic_h.cpu()

        actions: List[int] = []
        for agent_id, net in enumerate(agents):
            action, log_prob, value, next_actor_h, next_critic_h = net.act(
                obs_tensor[agent_id],
                state.actor_h[agent_id],
                state.critic_h[agent_id],
                deterministic=False,
            )
            actions.append(int(action.item()))
            actions_buf[step, agent_id] = int(action.item())
            logprob_buf[step, agent_id] = float(log_prob.item())
            values_buf[step, agent_id] = float(value.item())
            state.actor_h[agent_id] = next_actor_h.squeeze(0)
            state.critic_h[agent_id] = next_critic_h.squeeze(0)

        next_obs, rewards, done, truncated, info = env.step(actions)
        terminal = bool(done or truncated)
        rewards_array = np.asarray(rewards, dtype=np.float32)

        rewards_buf[step] = torch.as_tensor(rewards_array, dtype=torch.float32)
        dones_buf[step] = float(terminal)
        state.episode_returns += rewards_array
        state.episode_length += 1

        if terminal:
            completed_returns.append(float(np.mean(state.episode_returns)))
            completed_lengths.append(float(state.episode_length))
            team_events = info.get("deliveries", info.get("collections", 0))
            completed_team_events.append(float(team_events))

            next_obs, _ = env.reset()
            state.actor_h.zero_()
            state.critic_h.zero_()
            state.episode_returns[:] = 0.0
            state.episode_length = 0

        state.obs = next_obs

    flat_last_obs = flatten_multi_agent_obs(env, state.obs)
    last_obs_tensor = torch.as_tensor(flat_last_obs, dtype=torch.float32, device=device)
    last_values = torch.zeros((n_agents,), dtype=torch.float32)
    for agent_id, net in enumerate(agents):
        with torch.no_grad():
            value, _ = net._critic_step(
                last_obs_tensor[agent_id].unsqueeze(0),
                state.critic_h[agent_id].unsqueeze(0),
            )
        last_values[agent_id] = float(value.item())

    rollout = Rollout(
        obs=obs_buf,
        actions=actions_buf,
        old_log_probs=logprob_buf,
        rewards=rewards_buf,
        dones=dones_buf,
        values=values_buf,
        actor_h=actor_h_buf,
        critic_h=critic_h_buf,
        last_values=last_values,
    )
    metrics = {
        "episode_return": float(np.mean(completed_returns))
        if completed_returns
        else float("nan"),
        "episode_length": float(np.mean(completed_lengths))
        if completed_lengths
        else float("nan"),
        "team_events": float(np.mean(completed_team_events))
        if completed_team_events
        else float("nan"),
        "episodes": float(len(completed_returns)),
    }
    return rollout, state, metrics


def compute_gae(
    rewards: torch.Tensor,
    dones: torch.Tensor,
    values: torch.Tensor,
    last_values: torch.Tensor,
    gamma: float,
    gae_lambda: float,
) -> Tuple[torch.Tensor, torch.Tensor]:
    rollout_steps, n_agents = rewards.shape
    advantages = torch.zeros_like(rewards)
    last_gae = torch.zeros((n_agents,), dtype=torch.float32)
    for step in reversed(range(rollout_steps)):
        if step == rollout_steps - 1:
            next_value = last_values
        else:
            next_value = values[step + 1]
        next_nonterminal = 1.0 - dones[step]
        delta = rewards[step] + gamma * next_value * next_nonterminal - values[step]
        last_gae = delta + gamma * gae_lambda * next_nonterminal * last_gae
        advantages[step] = last_gae
    returns = advantages + values
    return advantages, returns


def recurrent_minibatches(
    rollout: Rollout,
    agent_id: int,
    sequence_length: int,
    minibatch_chunks: int,
    rng: np.random.Generator,
):
    rollout_steps = rollout.obs.shape[0]
    starts = np.arange(0, rollout_steps, sequence_length, dtype=np.int64)
    rng.shuffle(starts)
    for offset in range(0, len(starts), minibatch_chunks):
        mb_starts = starts[offset : offset + minibatch_chunks]
        obs_seq = torch.stack(
            [rollout.obs[s : s + sequence_length, agent_id] for s in mb_starts], dim=1
        )
        actions_seq = torch.stack(
            [rollout.actions[s : s + sequence_length, agent_id] for s in mb_starts],
            dim=1,
        )
        old_logprob_seq = torch.stack(
            [
                rollout.old_log_probs[s : s + sequence_length, agent_id]
                for s in mb_starts
            ],
            dim=1,
        )
        old_value_seq = torch.stack(
            [rollout.values[s : s + sequence_length, agent_id] for s in mb_starts],
            dim=1,
        )
        done_seq = torch.stack(
            [rollout.dones[s : s + sequence_length] for s in mb_starts],
            dim=1,
        )
        actor_h0 = rollout.actor_h[mb_starts, agent_id]
        critic_h0 = rollout.critic_h[mb_starts, agent_id]
        yield (
            obs_seq,
            actions_seq,
            old_logprob_seq,
            old_value_seq,
            done_seq,
            actor_h0,
            critic_h0,
            mb_starts,
        )


def update_ippo(
    agents: Sequence[RecurrentActorCritic],
    optimizers: Sequence[torch.optim.Optimizer],
    rollout: Rollout,
    cfg: TrainConfig,
    graph_estimator: TeamGraphEstimator,
    device: torch.device,
    rng: np.random.Generator,
) -> Dict[str, float]:
    advantages, returns = compute_gae(
        rollout.rewards,
        rollout.dones,
        rollout.values,
        rollout.last_values,
        cfg.gamma,
        cfg.gae_lambda,
    )

    n_agents = len(agents)
    mean_abs_td_error = np.zeros((n_agents,), dtype=np.float64)
    metrics = {
        "policy_loss": [],
        "value_loss": [],
        "entropy": [],
        "approx_kl": [],
        "clip_fraction": [],
    }

    for agent_id, (net, optimizer) in enumerate(zip(agents, optimizers)):
        agent_adv = advantages[:, agent_id]
        agent_adv = (agent_adv - agent_adv.mean()) / (
            agent_adv.std(unbiased=False) + 1e-8
        )
        agent_returns = returns[:, agent_id]
        mean_abs_td_error[agent_id] = float(
            torch.mean(torch.abs(agent_returns - rollout.values[:, agent_id])).item()
        )

        for _ in range(cfg.ppo_epochs):
            for (
                obs_seq,
                actions_seq,
                old_logprob_seq,
                old_value_seq,
                done_seq,
                actor_h0,
                critic_h0,
                mb_starts,
            ) in recurrent_minibatches(
                rollout,
                agent_id,
                cfg.sequence_length,
                cfg.minibatch_chunks,
                rng,
            ):
                adv_seq = torch.stack(
                    [
                        agent_adv[s : s + cfg.sequence_length]
                        for s in mb_starts
                    ],
                    dim=1,
                )
                return_seq = torch.stack(
                    [
                        agent_returns[s : s + cfg.sequence_length]
                        for s in mb_starts
                    ],
                    dim=1,
                )

                obs_seq = obs_seq.to(device)
                actions_seq = actions_seq.to(device)
                old_logprob_seq = old_logprob_seq.to(device)
                old_value_seq = old_value_seq.to(device)
                done_seq = done_seq.to(device)
                actor_h0 = actor_h0.to(device)
                critic_h0 = critic_h0.to(device)
                adv_seq = adv_seq.to(device)
                return_seq = return_seq.to(device)

                new_logprob, entropy, value = net.evaluate_actions(
                    obs_seq,
                    actions_seq,
                    done_seq,
                    actor_h0,
                    critic_h0,
                )
                log_ratio = new_logprob - old_logprob_seq
                ratio = log_ratio.exp()
                unclipped_policy_loss = -adv_seq * ratio
                clipped_policy_loss = -adv_seq * torch.clamp(
                    ratio,
                    1.0 - cfg.clip_coef,
                    1.0 + cfg.clip_coef,
                )
                policy_loss = torch.max(
                    unclipped_policy_loss,
                    clipped_policy_loss,
                ).mean()

                value_clipped = old_value_seq + torch.clamp(
                    value - old_value_seq,
                    -cfg.value_clip_coef,
                    cfg.value_clip_coef,
                )
                unclipped_value_loss = (value - return_seq).pow(2)
                clipped_value_loss = (value_clipped - return_seq).pow(2)
                value_loss = 0.5 * torch.max(
                    unclipped_value_loss,
                    clipped_value_loss,
                ).mean()
                entropy_loss = entropy.mean()

                loss = (
                    policy_loss
                    + cfg.value_loss_coef * value_loss
                    - cfg.entropy_coef * entropy_loss
                )

                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                nn.utils.clip_grad_norm_(net.parameters(), cfg.max_grad_norm)
                optimizer.step()

                with torch.no_grad():
                    approx_kl = ((ratio - 1.0) - log_ratio).mean()
                    clip_fraction = (
                        (torch.abs(ratio - 1.0) > cfg.clip_coef)
                        .float()
                        .mean()
                    )
                metrics["policy_loss"].append(float(policy_loss.item()))
                metrics["value_loss"].append(float(value_loss.item()))
                metrics["entropy"].append(float(entropy_loss.item()))
                metrics["approx_kl"].append(float(approx_kl.item()))
                metrics["clip_fraction"].append(float(clip_fraction.item()))

    graph_estimator.update_value_uncertainty(mean_abs_td_error)
    return {
        name: float(np.mean(values)) if values else float("nan")
        for name, values in metrics.items()
    }


def critic_parameter_groups(net: RecurrentActorCritic) -> List[nn.Parameter]:
    return list(net.critic_parameters())


@torch.no_grad()
def apply_clustered_critic_consensus(
    agents: Sequence[RecurrentActorCritic],
    clusters: Sequence[Sequence[int]],
    tau: float,
) -> int:
    if tau <= 0.0:
        return 0
    updates = 0
    for cluster in clusters:
        members = [int(idx) for idx in cluster]
        if len(members) <= 1:
            continue
        per_agent_params = [critic_parameter_groups(agents[idx]) for idx in members]
        for params in zip(*per_agent_params):
            avg = torch.stack([p.data for p in params], dim=0).mean(dim=0)
            for p in params:
                p.data.mul_(1.0 - tau).add_(avg, alpha=tau)
        updates += 1
    return updates


@torch.no_grad()
def run_probe_episode(
    env_id: str,
    env_kwargs: Dict,
    agents: Sequence[RecurrentActorCritic],
    obs_dim: int,
    action_dim: int,
    recurrent_hidden_dim: int,
    device: torch.device,
    seed: int,
    horizon: int,
    gamma: float,
    forced_step: Optional[int] = None,
    forced_agent: Optional[int] = None,
    forced_offset: int = 1,
) -> np.ndarray:
    env = make_env(env_id, env_kwargs)
    obs, _ = env.reset(seed=seed)
    n_agents = len(agents)
    actor_h = torch.zeros((n_agents, recurrent_hidden_dim), device=device)
    critic_h = torch.zeros_like(actor_h)
    discounted_returns = np.zeros((n_agents,), dtype=np.float64)
    discount = 1.0

    for step in range(horizon):
        flat_obs = flatten_multi_agent_obs(env, obs)
        obs_tensor = torch.as_tensor(flat_obs, dtype=torch.float32, device=device)
        actions: List[int] = []
        for agent_id, net in enumerate(agents):
            action, _, _, next_actor_h, next_critic_h = net.act(
                obs_tensor[agent_id],
                actor_h[agent_id],
                critic_h[agent_id],
                deterministic=True,
            )
            act_int = int(action.item())
            if forced_step == step and forced_agent == agent_id:
                act_int = int((act_int + forced_offset) % action_dim)
            actions.append(act_int)
            actor_h[agent_id] = next_actor_h.squeeze(0)
            critic_h[agent_id] = next_critic_h.squeeze(0)

        obs, rewards, done, truncated, _ = env.step(actions)
        discounted_returns += discount * np.asarray(rewards, dtype=np.float64)
        discount *= gamma
        if done or truncated:
            break
    env.close()
    del obs_dim
    return discounted_returns


def run_sparse_counterfactual_probes(
    cfg: TrainConfig,
    env_kwargs: Dict,
    agents: Sequence[RecurrentActorCritic],
    graph_estimator: TeamGraphEstimator,
    obs_dim: int,
    action_dim: int,
    recurrent_hidden_dim: int,
    device: torch.device,
    iteration: int,
    rng: np.random.Generator,
) -> Dict[str, float]:
    if cfg.graph_mode != "probe" or cfg.probe_episodes <= 0:
        return {"probe_delta": float("nan")}

    deltas = []
    for probe_id in range(cfg.probe_episodes):
        source_agent = int(rng.integers(0, len(agents)))
        forced_step = int(rng.integers(0, max(cfg.probe_horizon, 1)))
        forced_offset = int(rng.integers(1, action_dim))
        probe_seed = cfg.seed + 1_000_000 + iteration * 1000 + probe_id

        base_returns = run_probe_episode(
            cfg.env_id,
            env_kwargs,
            agents,
            obs_dim,
            action_dim,
            recurrent_hidden_dim,
            device,
            seed=probe_seed,
            horizon=cfg.probe_horizon,
            gamma=cfg.gamma,
        )
        cf_returns = run_probe_episode(
            cfg.env_id,
            env_kwargs,
            agents,
            obs_dim,
            action_dim,
            recurrent_hidden_dim,
            device,
            seed=probe_seed,
            horizon=cfg.probe_horizon,
            gamma=cfg.gamma,
            forced_step=forced_step,
            forced_agent=source_agent,
            forced_offset=forced_offset,
        )
        delta = cf_returns - base_returns
        graph_estimator.update_from_counterfactual(source_agent, delta)
        deltas.append(float(np.mean(np.abs(delta))))

    return {"probe_delta": float(np.mean(deltas)) if deltas else float("nan")}


@torch.no_grad()
def evaluate(
    env_id: str,
    env_kwargs: Dict,
    agents: Sequence[RecurrentActorCritic],
    episodes: int,
    horizon: int,
    gamma: float,
    obs_dim: int,
    recurrent_hidden_dim: int,
    device: torch.device,
    seed: int,
    render_episodes: int = 0,
    render_mode: str = "human",
    collect_video: bool = False,
) -> Tuple[Dict[str, float], Optional[np.ndarray]]:
    if episodes <= 0:
        return {}, None
    del obs_dim
    returns = []
    lengths = []
    video_frames: List[np.ndarray] = []
    for episode in range(episodes):
        should_render = episode < render_episodes
        should_collect_video = collect_video and episode == 0
        episode_render_mode = "rgb_array" if should_collect_video else render_mode
        eval_env_kwargs = (
            make_render_env_kwargs(env_kwargs, episode_render_mode)
            if should_render or should_collect_video
            else env_kwargs
        )
        env = make_env(env_id, eval_env_kwargs)
        obs, _ = env.reset(seed=seed + episode)
        n_agents = len(agents)
        actor_h = torch.zeros((n_agents, recurrent_hidden_dim), device=device)
        critic_h = torch.zeros_like(actor_h)
        ep_return = np.zeros((n_agents,), dtype=np.float64)
        discount = 1.0
        length = 0
        if should_render or should_collect_video:
            frame = env.render()
            if should_collect_video and frame is not None:
                video_frames.append(np.asarray(frame, dtype=np.uint8))
        for step in range(horizon):
            flat_obs = flatten_multi_agent_obs(env, obs)
            obs_tensor = torch.as_tensor(flat_obs, dtype=torch.float32, device=device)
            actions = []
            for agent_id, net in enumerate(agents):
                action, _, _, next_actor_h, next_critic_h = net.act(
                    obs_tensor[agent_id],
                    actor_h[agent_id],
                    critic_h[agent_id],
                    deterministic=True,
                )
                actions.append(int(action.item()))
                actor_h[agent_id] = next_actor_h.squeeze(0)
                critic_h[agent_id] = next_critic_h.squeeze(0)
            obs, rewards, done, truncated, _ = env.step(actions)
            ep_return += discount * np.asarray(rewards, dtype=np.float64)
            discount *= gamma
            length = step + 1
            if should_render or should_collect_video:
                frame = env.render()
                if should_collect_video and frame is not None:
                    video_frames.append(np.asarray(frame, dtype=np.uint8))
            if done or truncated:
                break
        env.close()
        returns.append(float(np.mean(ep_return)))
        lengths.append(float(length))
    video = None
    if video_frames:
        # wandb.Video expects time-major channels-first video.
        video = np.stack(video_frames, axis=0).transpose(0, 3, 1, 2)
    return {
        "eval_return": float(np.mean(returns)),
        "eval_length": float(np.mean(lengths)),
    }, video


def save_checkpoint(
    path: Path,
    cfg: TrainConfig,
    agents: Sequence[RecurrentActorCritic],
    optimizers: Sequence[torch.optim.Optimizer],
    graph_estimator: TeamGraphEstimator,
    iteration: int,
    env_steps: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "config": asdict(cfg),
            "iteration": iteration,
            "env_steps": env_steps,
            "agents": [agent.state_dict() for agent in agents],
            "optimizers": [optimizer.state_dict() for optimizer in optimizers],
            "graph": graph_estimator.state_dict(),
        },
        path,
    )


def format_clusters(clusters: Sequence[Sequence[int]]) -> str:
    return "[" + ", ".join(str(list(cluster)) for cluster in clusters) + "]"


def graph_metrics(
    graph_estimator: TeamGraphEstimator,
    clusters: Sequence[Sequence[int]],
    adjacency: np.ndarray,
) -> Dict[str, float]:
    cluster_sizes = [len(cluster) for cluster in clusters]
    return {
        "graph/edges": float(np.sum(adjacency) / 2.0),
        "graph/clusters": float(len(clusters)),
        "graph/max_cluster_size": float(max(cluster_sizes) if cluster_sizes else 0),
        "graph/value_uncertainty": float(np.mean(graph_estimator.value_uncertainty)),
    }


def prefixed_metrics(prefix: str, metrics: Dict[str, float]) -> Dict[str, float]:
    return {
        f"{prefix}/{key}": value
        for key, value in metrics.items()
        if isinstance(value, (float, int)) and not math.isnan(float(value))
    }


def log_to_wandb(run, payload: Dict[str, object], step: int) -> None:
    if run is None:
        return
    run.log(payload, step=step)


def make_wandb_video(video: np.ndarray, fps: int):
    import wandb

    return wandb.Video(video, fps=fps, format="mp4")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recurrent IPPO + sparse probing + clustered critic consensus"
    )
    parser.add_argument("--env-id", default="rware-multiteam-tiny-4ag-2teams-v0")
    parser.add_argument("--env-kwargs-json", default="{}")
    parser.add_argument("--total-timesteps", type=int, default=200_000)
    parser.add_argument("--rollout-steps", type=int, default=512)
    parser.add_argument("--sequence-length", type=int, default=32)
    parser.add_argument("--minibatch-chunks", type=int, default=8)
    parser.add_argument("--ppo-epochs", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--gae-lambda", type=float, default=0.95)
    parser.add_argument("--clip-coef", type=float, default=0.2)
    parser.add_argument("--value-clip-coef", type=float, default=0.2)
    parser.add_argument("--value-loss-coef", type=float, default=0.5)
    parser.add_argument("--entropy-coef", type=float, default=0.01)
    parser.add_argument("--max-grad-norm", type=float, default=0.5)
    parser.add_argument("--mlp-hidden-dim", type=int, default=128)
    parser.add_argument("--recurrent-hidden-dim", type=int, default=128)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument(
        "--graph-mode",
        default="probe",
        choices=["probe", "none", "oracle"],
        help="oracle is for debugging/baselines only; probe is the intended mode.",
    )
    parser.add_argument("--probe-interval", type=int, default=10)
    parser.add_argument("--probe-episodes", type=int, default=4)
    parser.add_argument("--probe-horizon", type=int, default=120)
    parser.add_argument("--edge-threshold", type=float, default=0.01)
    parser.add_argument("--min-probe-count", type=int, default=2)
    parser.add_argument("--uncertainty-scale", type=float, default=1.0)
    parser.add_argument("--value-uncertainty-decay", type=float, default=0.95)
    parser.add_argument("--critic-consensus-tau", type=float, default=0.1)
    parser.add_argument("--consensus-interval", type=int, default=1)
    parser.add_argument("--save-dir", default="runs/recurrent_ippo_consensus")
    parser.add_argument("--exp-name", default="")
    parser.add_argument("--save-interval", type=int, default=50)
    parser.add_argument("--log-interval", type=int, default=1)
    parser.add_argument("--eval-episodes", type=int, default=5)
    parser.add_argument("--eval-horizon", type=int, default=500)
    parser.add_argument(
        "--eval-interval",
        type=int,
        default=0,
        help="Run eval every N training iterations. Final eval still runs once.",
    )
    parser.add_argument(
        "--render-eval",
        action="store_true",
        help="Render eval episodes with env.render().",
    )
    parser.add_argument("--eval-render-episodes", type=int, default=1)
    parser.add_argument(
        "--eval-render-mode",
        default="human",
        choices=["human", "rgb_array"],
    )
    parser.add_argument("--eval-render-fps", type=int, default=10)
    parser.add_argument(
        "--track",
        action="store_true",
        help="Log training and eval metrics to Weights & Biases.",
    )
    parser.add_argument("--wandb-project", default="rware-recurrent-ippo")
    parser.add_argument("--wandb-entity", default="")
    parser.add_argument("--wandb-group", default="")
    parser.add_argument("--wandb-name", default="")
    parser.add_argument(
        "--wandb-mode",
        default="online",
        choices=["online", "offline", "disabled"],
    )
    parser.add_argument("--wandb-tags", default="")
    parser.add_argument(
        "--wandb-log-eval-video",
        action="store_true",
        help="Log one rgb_array eval episode as a wandb.Video.",
    )
    return parser


def resolve_device(value: str) -> torch.device:
    if value == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(value)


def main() -> None:
    args = build_arg_parser().parse_args()
    cfg = TrainConfig(**vars(args))
    if cfg.rollout_steps % cfg.sequence_length != 0:
        raise ValueError("--rollout-steps must be divisible by --sequence-length")
    if cfg.minibatch_chunks < 1:
        raise ValueError("--minibatch-chunks must be positive")

    set_global_seeds(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    device = resolve_device(cfg.device)
    env_kwargs = parse_env_kwargs(cfg.env_kwargs_json)

    env = make_env(cfg.env_id, env_kwargs)
    obs, _ = env.reset(seed=cfg.seed)
    n_agents = int(env.unwrapped.n_agents)
    obs_dims = get_flat_obs_dims(env)
    action_dims = get_discrete_action_dims(env)
    if len(set(obs_dims)) != 1:
        raise ValueError(f"Expected identical observation dims, got {obs_dims}")
    if len(set(action_dims)) != 1:
        raise ValueError(f"Expected identical action dims, got {action_dims}")
    obs_dim = int(obs_dims[0])
    action_dim = int(action_dims[0])

    agents = [
        RecurrentActorCritic(
            obs_dim=obs_dim,
            action_dim=action_dim,
            mlp_hidden_dim=cfg.mlp_hidden_dim,
            recurrent_hidden_dim=cfg.recurrent_hidden_dim,
        ).to(device)
        for _ in range(n_agents)
    ]
    optimizers = [
        torch.optim.Adam(agent.parameters(), lr=cfg.learning_rate, eps=1e-5)
        for agent in agents
    ]
    graph_estimator = TeamGraphEstimator(
        n_agents=n_agents,
        edge_threshold=cfg.edge_threshold,
        min_probe_count=cfg.min_probe_count,
        uncertainty_scale=cfg.uncertainty_scale,
        value_uncertainty_decay=cfg.value_uncertainty_decay,
    )

    actor_h = torch.zeros((n_agents, cfg.recurrent_hidden_dim), device=device)
    critic_h = torch.zeros_like(actor_h)
    state = RunnerState(
        obs=obs,
        actor_h=actor_h,
        critic_h=critic_h,
        episode_returns=np.zeros((n_agents,), dtype=np.float64),
    )

    exp_name = cfg.exp_name or f"{cfg.env_id}_{int(time.time())}"
    cfg.exp_name = exp_name
    save_dir = Path(cfg.save_dir) / exp_name
    save_dir.mkdir(parents=True, exist_ok=True)
    wandb_run = init_wandb(cfg, save_dir)

    total_iterations = math.ceil(cfg.total_timesteps / cfg.rollout_steps)
    start_time = time.time()
    print(
        f"env={cfg.env_id} agents={n_agents} obs_dim={obs_dim} "
        f"action_dim={action_dim} device={device}"
    )

    for iteration in range(1, total_iterations + 1):
        if cfg.graph_mode == "oracle":
            clusters = oracle_clusters(env) or [[idx] for idx in range(n_agents)]
            adj = np.zeros((n_agents, n_agents), dtype=np.float32)
            for cluster in clusters:
                for i in cluster:
                    for j in cluster:
                        if i != j:
                            adj[i, j] = 1.0
        elif cfg.graph_mode == "none":
            clusters = [[idx] for idx in range(n_agents)]
            adj = np.zeros((n_agents, n_agents), dtype=np.float32)
        else:
            clusters = graph_estimator.clusters()
            adj = graph_estimator.adjacency()
        set_env_training_edges(env, adj)

        rollout, state, rollout_metrics = collect_rollout(
            env,
            agents,
            state,
            cfg.rollout_steps,
            obs_dim,
            cfg.recurrent_hidden_dim,
            device,
        )

        update_metrics = update_ippo(
            agents,
            optimizers,
            rollout,
            cfg,
            graph_estimator,
            device,
            rng,
        )

        probe_metrics = {"probe_delta": float("nan")}
        if (
            cfg.graph_mode == "probe"
            and cfg.probe_interval > 0
            and iteration % cfg.probe_interval == 0
        ):
            probe_metrics = run_sparse_counterfactual_probes(
                cfg,
                env_kwargs,
                agents,
                graph_estimator,
                obs_dim,
                action_dim,
                cfg.recurrent_hidden_dim,
                device,
                iteration,
                rng,
            )

        if cfg.graph_mode == "oracle":
            consensus_clusters = oracle_clusters(env) or [[idx] for idx in range(n_agents)]
        elif cfg.graph_mode == "none":
            consensus_clusters = [[idx] for idx in range(n_agents)]
        else:
            consensus_clusters = graph_estimator.clusters()

        consensus_updates = 0
        if cfg.consensus_interval > 0 and iteration % cfg.consensus_interval == 0:
            consensus_updates = apply_clustered_critic_consensus(
                agents,
                consensus_clusters,
                tau=cfg.critic_consensus_tau,
            )

        env_steps = iteration * cfg.rollout_steps
        elapsed = max(time.time() - start_time, 1e-6)
        sps = env_steps / elapsed
        log_clusters = (
            oracle_clusters(env)
            if cfg.graph_mode == "oracle"
            else graph_estimator.clusters()
        ) or []
        wandb_payload: Dict[str, object] = {
            "train/env_steps": float(env_steps),
            "train/sps": float(sps),
            "train/consensus_updates": float(consensus_updates),
        }
        wandb_payload.update(prefixed_metrics("train", rollout_metrics))
        wandb_payload.update(prefixed_metrics("update", update_metrics))
        wandb_payload.update(prefixed_metrics("probe", probe_metrics))
        wandb_payload.update(graph_metrics(graph_estimator, log_clusters, adj))
        log_to_wandb(wandb_run, wandb_payload, step=env_steps)

        if iteration % cfg.log_interval == 0:
            print(
                f"iter={iteration:04d} steps={env_steps} sps={sps:.1f} "
                f"return={rollout_metrics['episode_return']:.3f} "
                f"len={rollout_metrics['episode_length']:.1f} "
                f"events={rollout_metrics['team_events']:.2f} "
                f"pi_loss={update_metrics['policy_loss']:.4f} "
                f"v_loss={update_metrics['value_loss']:.4f} "
                f"ent={update_metrics['entropy']:.3f} "
                f"probe_delta={probe_metrics['probe_delta']:.4f} "
                f"consensus={consensus_updates} "
                f"clusters={format_clusters(log_clusters)}"
            )

        if cfg.eval_interval > 0 and iteration % cfg.eval_interval == 0:
            eval_metrics, eval_video = evaluate(
                cfg.env_id,
                env_kwargs,
                agents,
                cfg.eval_episodes,
                cfg.eval_horizon,
                cfg.gamma,
                obs_dim,
                cfg.recurrent_hidden_dim,
                device,
                seed=cfg.seed + 5_000_000 + env_steps,
                render_episodes=cfg.eval_render_episodes if cfg.render_eval else 0,
                render_mode=cfg.eval_render_mode,
                collect_video=cfg.track and cfg.wandb_log_eval_video,
            )
            if eval_metrics:
                print(
                    f"eval iter={iteration:04d} "
                    f"return={eval_metrics['eval_return']:.3f} "
                    f"length={eval_metrics['eval_length']:.1f}"
                )
                eval_payload: Dict[str, object] = {
                    "eval/return": eval_metrics["eval_return"],
                    "eval/length": eval_metrics["eval_length"],
                }
                if eval_video is not None and wandb_run is not None:
                    eval_payload["eval/video"] = make_wandb_video(
                        eval_video,
                        fps=cfg.eval_render_fps,
                    )
                log_to_wandb(wandb_run, eval_payload, step=env_steps)

        if cfg.save_interval > 0 and iteration % cfg.save_interval == 0:
            save_checkpoint(
                save_dir / f"checkpoint_{iteration:05d}.pt",
                cfg,
                agents,
                optimizers,
                graph_estimator,
                iteration,
                env_steps,
            )

    eval_metrics, eval_video = evaluate(
        cfg.env_id,
        env_kwargs,
        agents,
        cfg.eval_episodes,
        cfg.eval_horizon,
        cfg.gamma,
        obs_dim,
        cfg.recurrent_hidden_dim,
        device,
        seed=cfg.seed + 5_000_000,
        render_episodes=cfg.eval_render_episodes if cfg.render_eval else 0,
        render_mode=cfg.eval_render_mode,
        collect_video=cfg.track and cfg.wandb_log_eval_video,
    )
    if eval_metrics:
        print(
            f"eval_return={eval_metrics['eval_return']:.3f} "
            f"eval_length={eval_metrics['eval_length']:.1f}"
        )
        final_eval_payload: Dict[str, object] = {
            "eval/final_return": eval_metrics["eval_return"],
            "eval/final_length": eval_metrics["eval_length"],
        }
        if eval_video is not None and wandb_run is not None:
            final_eval_payload["eval/final_video"] = make_wandb_video(
                eval_video,
                fps=cfg.eval_render_fps,
            )
        log_to_wandb(wandb_run, final_eval_payload, step=total_iterations * cfg.rollout_steps)

    final_path = save_dir / "final.pt"
    save_checkpoint(
        final_path,
        cfg,
        agents,
        optimizers,
        graph_estimator,
        total_iterations,
        total_iterations * cfg.rollout_steps,
    )
    env.close()
    if wandb_run is not None:
        wandb_run.finish()
    print(f"saved={final_path}")


if __name__ == "__main__":
    main()
