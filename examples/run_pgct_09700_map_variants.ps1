param(
  [int[]] $AgentCounts = @(6, 8),
  [ValidateSet("tiny", "small", "medium")]
  [string[]] $MapSizes = @("tiny", "small", "medium"),
  [int] $Episodes = 1,
  [int] $Horizon = 500,
  [int] $Seed = 12345,
  [string] $OutputDir = "",
  [switch] $ShowVideos
)
$ErrorActionPreference = "Stop"
if (-not $OutputDir) {
  $OutputDir = "runs/pgct_09700_map_variants_$(Get-Date -Format 'yyyyMMdd_HHmmss_fff')"
}
# Keep shelf ownership separated. Only agent count and map dimensions vary.
& "$PSScriptRoot/run_pgct_09700_generalization.ps1" -AgentCounts $AgentCounts `
  -HomeRatios @(1.0) -MapSizes $MapSizes -Episodes $Episodes -Horizon $Horizon `
  -Seed $Seed -OutputDir $OutputDir -ShowVideos:$ShowVideos
