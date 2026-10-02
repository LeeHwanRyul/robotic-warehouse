param(
  [string] $Checkpoint = "runs/recurrent_ippo_consensus/ex5_semantic_cnn_policy_complete_from_scratch_4ag_sr5_square_home1.00_seed1/checkpoint_09700.pt",
  [int[]] $AgentCounts = @(6, 8),
  [double[]] $HomeRatios = @(1.0, 0.75, 0.5),
  [ValidateSet("checkpoint", "tiny", "small", "medium")]
  [string[]] $MapSizes = @("checkpoint"),
  [ValidateRange(1, 10000)]
  [int] $Episodes = 20,
  [ValidateRange(1, 100000)]
  [int] $Horizon = 500,
  [int] $Seed = 12345,
  [ValidateRange(1, 120)]
  [int] $VideoFps = 8,
  [ValidateSet("auto", "cpu", "cuda")]
  [string] $Device = "cpu",
  [string] $OutputDir = "",
  [switch] $ShowVideos,
  [string] $Python = "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe"
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path -LiteralPath $Checkpoint)) { throw "Checkpoint not found: $Checkpoint" }
if (-not $OutputDir) {
  $OutputDir = "runs/pgct_09700_generalization_$(Get-Date -Format 'yyyyMMdd_HHmmss_fff')"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$VideoDir = Join-Path $OutputDir "videos"
$MetricsPath = Join-Path $OutputDir "metrics.json"
# Frozen policies are copied round-robin, preserving the two teams.
# home=1.0: separated; home=0.75: 25% mixed; home=0.5: 50% mixed.
# Each scenario records its first evaluation episode as an RGB-rendered MP4.
$EvalArgs = @(
  "examples/eval_checkpoint_generalization.py",
  "--checkpoint", $Checkpoint,
  "--agent-counts"
)
$EvalArgs += @($AgentCounts | ForEach-Object { "$_" })
$EvalArgs += "--home-ratios"
$EvalArgs += @($HomeRatios | ForEach-Object { $_.ToString([Globalization.CultureInfo]::InvariantCulture) })
$EvalArgs += "--map-sizes"
$EvalArgs += $MapSizes
$EvalArgs += @(
  "--episodes", "$Episodes", "--horizon", "$Horizon", "--seed", "$Seed",
  "--video-fps", "$VideoFps", "--device", $Device,
  "--out", $MetricsPath, "--video-dir", $VideoDir
)
Write-Host "Evaluating frozen checkpoint: $Checkpoint"
Write-Host "Output: $OutputDir"
& $Python @EvalArgs
if ($LASTEXITCODE -ne 0) { throw "Evaluation failed with exit code $LASTEXITCODE" }
$Results = Get-Content -LiteralPath $MetricsPath -Raw | ConvertFrom-Json
$Results | Select-Object n_agents, map_size, home_ratio, shelf_count, eval_deliveries, eval_returns_home, deliveries_per_agent,
  eval_full_cycle_success_rate, eval_failed_forward_rate |
  Export-Csv -LiteralPath (Join-Path $OutputDir "summary.csv") -NoTypeInformation -Encoding UTF8
Write-Host "Saved metrics.json, summary.csv and videos to $OutputDir"
if ($ShowVideos) { Invoke-Item -LiteralPath $VideoDir }
