# Recurrent IPPO Policy-Probe Consensus Example

This folder contains training code for latent-team RWARE experiments.

## Algorithm

`train_recurrent_ippo_consensus.py` implements:

- fully decentralized recurrent actors and critics,
- IPPO clipped policy/value updates,
- sparse common-probe policy comparisons among communication neighbors,
- uncertainty-aware team confidence weights from policy similarity and critic TD error,
- confidence-weighted intra-team critic consensus.

Actors and critics only consume each agent's local observation. The graph is used only for
training-time critic consensus and can be inspected through the environment's training graph hooks.
The default `--graph-mode policy` matches the project proposal: each update samples a small
common probe set, compares neighboring policies on that same probe set, and shares critic
information only across high-confidence edges. By default, `--probe-source mixed` combines
the original random rollout probes with objective-revealing probes that expose task-relevant
targets or requested shelves. The previous return-influence perturbation variant is still
available as `--graph-mode influence`.

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

Override the number of agents directly:

```sh
python examples/train_recurrent_ippo_consensus.py \
  --env-id rware-multiteam-tiny-4ag-2teams-v0 \
  --agent-count 8 \
  --team-count 2
```

Run an agent-count curriculum one stage at a time. Stage indices are 1-based, so this
starts with 2 agents and then initializes the 4-agent stage from the previous run's
checkpoint. By default only actor parameters are transferred; critics, optimizers, and
the discovered graph statistics start fresh in the new stage. When the agent count is
overridden for multi-team RWARE, the request queue is scaled to the selected agent/team
count unless you explicitly pass `request_queue_size` or `request_queue_size_per_team`.

```sh
python examples/train_recurrent_ippo_consensus.py \
  --curriculum-stages 2,4,8,16 \
  --curriculum-stage 1 \
  --team-count 2 \
  --exp-name curriculum_stage1_2ag

python examples/train_recurrent_ippo_consensus.py \
  --curriculum-stages 2,4,8,16 \
  --curriculum-stage 2 \
  --team-count 2 \
  --init-checkpoint runs/recurrent_ippo_consensus/curriculum_stage1_2ag/final.pt \
  --exp-name curriculum_stage2_4ag
```

Use `--transfer-components actor,critic` only when you explicitly want to copy critic
parameters too. Newly added agents copy source-stage agents round-robin.

For the full 2 -> 4 -> 8 -> 16 wandb/video run, use the helper script:

```powershell
.\examples\run_curriculum_2_4_8_16.ps1 `
  -RunPrefix curriculum_2_4_8_16_scaled `
  -WandbGroup curriculum_2_4_8_16
```

Pass `-Python C:\path\to\python.exe` if `python` is not on your PATH.

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

# Legacy return-influence probing baseline.
python examples/train_recurrent_ippo_consensus.py --graph-mode influence

# Compare every pair instead of only physical communication neighbors.
python examples/train_recurrent_ippo_consensus.py --comm-graph-mode complete

# Original rollout-only policy probing baseline.
python examples/train_recurrent_ippo_consensus.py --probe-source rollout

# Objective probe bank only.
python examples/train_recurrent_ippo_consensus.py --probe-source objective

# Stabilize graph edges with hysteresis and dwell time.
python examples/train_recurrent_ippo_consensus.py \
  --graph-join-threshold 0.7 \
  --graph-leave-threshold 0.5 \
  --graph-dwell-updates 3
```
