param(
  [int] $TotalTimesteps = 5000000,
  [string] $Python = "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe"
)

& $Python examples\train_recurrent_ippo_consensus.py `
  --env-id rware-multiteam-tiny-4ag-2teams-v0 `
  --agent-count 1 `
  --team-count 1 `
  --sensor-range 3 `
  --env-kwargs-json "@examples/env_kwargs_stage1_delivery_lowshape.json" `
  --observation-format semantic `
  --obs-encoder cnn `
  --graph-mode none `
  --probe-interval 0 `
  --critic-consensus-tau 0 `
  --consensus-interval 0 `
  --total-timesteps $TotalTimesteps `
  --rollout-steps 1024 `
  --sequence-length 64 `
  --learning-rate 2e-4 `
  --entropy-coef 0.02 `
  --eval-interval 50 `
  --eval-episodes 20 `
  --eval-horizon 500 `
  --save-interval 100 `
  --track `
  --wandb-project rware-curriculum `
  --wandb-group semantic_cnn_curriculum `
  --wandb-name stage1_semantic_cnn_sr3 `
  --wandb-log-eval-video `
  --wandb-video-interval 5 `
  --exp-name stage1_semantic_cnn_sr3

