# Recurrent IPPO Consensus Example

This folder contains training code for latent-team RWARE experiments.

## Algorithm

`train_recurrent_ippo_consensus.py` implements:

- fully decentralized recurrent actors and critics,
- IPPO clipped policy/value updates,
- sparse counterfactual probing to estimate latent inter-agent influence,
- uncertainty-aware team graph construction from probe variance and critic TD error,
- clustered critic consensus by soft-averaging critic parameters inside inferred graph clusters.

Actors and critics only consume each agent's local observation. The graph is used only for
training-time critic consensus and can be inspected through the environment's training graph hooks.

## Install

```sh
pip install -e ".[rl]"
```

## Run

```sh
python examples/train_recurrent_ippo_consensus.py \
  --env-id rware-multiteam-tiny-4ag-2teams-v0 \
  --total-timesteps 200000
```

## Wandb and eval rendering

Log training, graph, probe, and eval metrics to Weights & Biases:

```sh
python examples/train_recurrent_ippo_consensus.py \
  --track \
  --wandb-project rware-recurrent-ippo \
  --eval-interval 10
```

Render one episode whenever eval runs:

```sh
python examples/train_recurrent_ippo_consensus.py \
  --eval-interval 10 \
  --render-eval \
  --eval-render-episodes 1
```

Log one eval episode as a wandb video:

```sh
python examples/train_recurrent_ippo_consensus.py \
  --track \
  --eval-interval 10 \
  --wandb-log-eval-video
```

Useful debugging variants:

```sh
# No graph and no critic sharing.
python examples/train_recurrent_ippo_consensus.py --graph-mode none

# Oracle team clusters for an upper-bound/debug baseline.
python examples/train_recurrent_ippo_consensus.py --graph-mode oracle
```
