param(
  [ValidateSet(4, 8, 16)] [int[]] $AgentCounts = @(4, 8, 16),
  [double[]] $ShelfHomeRatios = @(1.0, 0.875, 0.75, 0.5),
  [ValidateSet("none", "oracle", "policy-complete", "policy-physical", "wrong", "unrestricted")]
  [string] $Run = "none",
  [int] $TotalTimestepsPerStage = 5000000,
  [int] $Seed = 1,
  [switch] $NoTrack,
  [string] $Python = "C:\Users\95101\anaconda3\envs\RWARE_MARL\python.exe"
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($ShelfHomeRatios.Count -eq 0 -or $ShelfHomeRatios[0] -ne 1.0) {
  throw "The first stage must use ShelfHomeRatio=1.0."
}
for ($i = 0; $i -lt $ShelfHomeRatios.Count; $i++) {
  if ($ShelfHomeRatios[$i] -lt 0.5 -or $ShelfHomeRatios[$i] -gt 1.0) {
    throw "ShelfHomeRatios must lie between 0.5 and 1.0."
  }
  if ($i -gt 0 -and $ShelfHomeRatios[$i] -gt $ShelfHomeRatios[$i - 1]) {
    throw "ShelfHomeRatios must be non-increasing."
  }
}
$Names = @{
  "none" = "semantic_cnn_none_from_scratch"
  "oracle" = "semantic_cnn_oracle_from_scratch"
  "policy-complete" = "semantic_cnn_policy_complete_from_scratch"
  "policy-physical" = "semantic_cnn_policy_physical_from_scratch"
  "wrong" = "semantic_cnn_wrong_from_scratch"
  "unrestricted" = "semantic_cnn_unrestricted_from_scratch"
}
$Session = "curriculum_" + [guid]::NewGuid().ToString("N").Substring(0, 8)
foreach ($Count in $AgentCounts) {
  $Checkpoint = ""
  for ($Stage = 0; $Stage -lt $ShelfHomeRatios.Count; $Stage++) {
    $Ratio = $ShelfHomeRatios[$Stage]
    $Suffix = "${Session}_stage${Stage}"
    & "$PSScriptRoot/run_semantic_cnn_marl_pgct_from_scratch.ps1" `
      -Run $Run -AgentCount $Count -SensorRange 5 -ShelfHomeRatio $Ratio `
      -TotalTimesteps $TotalTimestepsPerStage -Seed $Seed -InitCheckpoint $Checkpoint `
      -RunNameSuffix $Suffix -NoTrack:$NoTrack -Python $Python
    $Label = $Ratio.ToString("0.00", [Globalization.CultureInfo]::InvariantCulture)
    $Name = "ex5_$($Names[$Run])_${Count}ag_sr5_square_home${Label}_seed${Seed}_${Suffix}"
    $Checkpoint = Join-Path "runs/recurrent_ippo_consensus" "$Name/final.pt"
    if (-not (Test-Path -LiteralPath $Checkpoint)) {
      throw "Stage did not produce its checkpoint: $Checkpoint"
    }
  }
}
