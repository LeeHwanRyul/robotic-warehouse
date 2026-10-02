param(
  [ValidateSet("none", "oracle", "policy-complete", "policy-physical", "all")]
  [string] $Run = "policy-complete",
  [int] $TotalTimesteps = 5000000,
  [int] $ProbeInterval = 5,
  [int] $SensorRange = 3,
  [double] $PgctDistanceThreshold = 0.12,
  [double] $PgctPeerLossCoef = 0.01,
  [double] $EntropyCoef = 0.02,
  [string] $EnvKwargsJson = "@examples/env_kwargs_stage2_pgct_success.json",
  [Parameter(Mandatory = $true)]
  [string] $InitCheckpoint,
  [string] $RunNameSuffix = "",
  [string] $Python = "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe"
)

$Common = @(
  "examples\train_recurrent_ippo_consensus.py",
  "--env-id", "rware-multiteam-tiny-4ag-2teams-v0",
  "--agent-count", "4",
  "--team-count", "2",
  "--sensor-range", "$SensorRange",
  "--env-kwargs-json", $EnvKwargsJson,
  "--observation-format", "semantic",
  "--obs-encoder", "cnn",
  "--init-checkpoint", $InitCheckpoint,
  "--transfer-components", "actor",
  "--total-timesteps", "$TotalTimesteps",
  "--rollout-steps", "1024",
  "--sequence-length", "64",
  "--learning-rate", "2e-4",
  "--entropy-coef", "$EntropyCoef",
  "--eval-interval", "50",
  "--eval-episodes", "20",
  "--eval-horizon", "500",
  "--save-interval", "100",
  "--probe-interval", "$ProbeInterval",
  "--track",
  "--wandb-project", "rware-curriculum",
  "--wandb-group", "semantic_cnn_pgct_from_checkpoint",
  "--wandb-log-eval-video",
  "--wandb-video-interval", "5"
)

function Invoke-Experiment {
  param(
    [string] $Name,
    [string[]] $ExtraArgs
  )

  Write-Host ""
  $ExperimentName = $Name
  if (-not [string]::IsNullOrWhiteSpace($RunNameSuffix)) {
    $ExperimentName = "${Name}_${RunNameSuffix}"
  }

  Write-Host "=== Starting $ExperimentName ==="
  & $Python @Common @ExtraArgs --wandb-name $ExperimentName --exp-name $ExperimentName
  if ($LASTEXITCODE -ne 0) {
    throw "$ExperimentName failed with exit code $LASTEXITCODE"
  }
}

$RunNone = @(
  "--graph-mode", "policy",
  "--comm-graph-mode", "complete",
  "--probe-source", "objective",
  "--objective-probe-fraction", "1.0",
  "--policy-probe-team-conditioning", "agent-team",
  "--policy-probe-batch-size", "128",
  "--pgct-probe-sequence-length", "1",
  "--peer-transfer-mode", "none",
  "--critic-consensus-tau", "0",
  "--consensus-interval", "0"
)

$RunOracle = @(
  "--graph-mode", "oracle",
  "--comm-graph-mode", "complete",
  "--probe-source", "objective",
  "--objective-probe-fraction", "1.0",
  "--policy-probe-team-conditioning", "agent-team",
  "--policy-probe-batch-size", "128",
  "--peer-transfer-mode", "pgct",
  "--pgct-probe-sequence-length", "1",
  "--pgct-peer-loss-coef", "$PgctPeerLossCoef",
  "--critic-consensus-tau", "0",
  "--consensus-interval", "0"
)

$RunPolicyComplete = @(
  "--graph-mode", "policy",
  "--comm-graph-mode", "complete",
  "--probe-source", "objective",
  "--objective-probe-fraction", "1.0",
  "--policy-probe-team-conditioning", "agent-team",
  "--policy-probe-batch-size", "128",
  "--peer-transfer-mode", "pgct",
  "--pgct-probe-sequence-length", "1",
  "--pgct-warmup-updates", "100",
  "--pgct-distance-ema-beta", "0.35",
  "--pgct-distance-temperature", "0.25",
  "--pgct-distance-threshold", "$PgctDistanceThreshold",
  "--pgct-peer-loss-coef", "$PgctPeerLossCoef",
  "--critic-consensus-tau", "0",
  "--consensus-interval", "0"
)

$RunPolicyPhysical = @(
  "--graph-mode", "policy",
  "--comm-graph-mode", "physical",
  "--probe-source", "objective",
  "--objective-probe-fraction", "1.0",
  "--policy-probe-team-conditioning", "agent-team",
  "--policy-probe-batch-size", "128",
  "--peer-transfer-mode", "pgct",
  "--pgct-probe-sequence-length", "1",
  "--pgct-warmup-updates", "100",
  "--pgct-distance-ema-beta", "0.35",
  "--pgct-distance-temperature", "0.25",
  "--pgct-distance-threshold", "$PgctDistanceThreshold",
  "--pgct-peer-loss-coef", "$PgctPeerLossCoef",
  "--critic-consensus-tau", "0",
  "--consensus-interval", "0"
)

if ($Run -eq "none" -or $Run -eq "all") {
  Invoke-Experiment "semantic_cnn_none_from_checkpoint" $RunNone
}
if ($Run -eq "oracle" -or $Run -eq "all") {
  Invoke-Experiment "semantic_cnn_oracle_from_checkpoint" $RunOracle
}
if ($Run -eq "policy-complete" -or $Run -eq "all") {
  Invoke-Experiment "semantic_cnn_policy_complete_from_checkpoint" $RunPolicyComplete
}
if ($Run -eq "policy-physical" -or $Run -eq "all") {
  Invoke-Experiment "semantic_cnn_policy_physical_from_checkpoint" $RunPolicyPhysical
}
