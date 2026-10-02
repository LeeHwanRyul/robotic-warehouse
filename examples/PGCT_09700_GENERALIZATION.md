# PGCT 09700: agent-count and shelf-mixing evaluation

Run from PowerShell:

```powershell
Set-Location C:\RWARE\MARL_RWARE\third_party\robotic-warehouse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\examples\run_pgct_09700_generalization.ps1
```

The default checkpoint is the ex5 policy-complete, 4-agent, sensor-range-5,
seed-1 run's `checkpoint_09700.pt`. This is **zero-shot evaluation**, with no
training or parameter updates. The four policies are copied round-robin:

| Target agents | Source policies (one-based) |
| --- | --- |
| 6 | 1, 2, 3, 4, 1, 2 |
| 8 | 1, 2, 3, 4, 1, 2, 3, 4 |

Team IDs alternate 0/1, preserving the policy's team. The warehouse size and
sensor range remain as in the checkpoint. The request queue grows to one
request per agent, evenly divided between the two teams, as in ex5 training.

Shelf mixing changes **team ownership**, keeping shelf positions and per-team
shelf totals fixed. `HomeRatios` specifies the proportion belonging to the
local zone's team: 1.0 means separated, 0.75 means 25% mixed, and 0.5 means
50% mixed. Counts are rounded to whole shelves by the environment.

By default each of the six scenarios runs 20 deterministic evaluation episodes
of at most 500 steps, using seeds 12345 through 12364. Each scenario saves its
first episode as an RGB-rendered MP4 at 8 FPS. A 500-step episode produces
501 frames, including the initial state (about 62.6 seconds).

Results go to a new timestamped directory under `runs/`:

- `videos/*.mp4`: warehouse and per-agent observation views.
- `metrics.json`: episode-averaged metrics plus checkpoint and evaluation settings.
- `summary.csv`: selected metrics for comparison.

Delivery and return counts are totals across agents, averaged across episodes.
`eval_full_cycle_success_rate` is the fraction of episodes with at least one
delivery and at least one return, not a per-agent completion percentage.
The saved video represents one episode, not the average result.

PGCT is used during training. Evaluation restores the checkpoint's distance
statistics and gate settings, then expands the gate using the same source-policy
mapping as the actors. Distinct copies of an identical policy have distance zero;
self-links remain disabled. This does not use true team labels to create edges.
The environment applies its spatial eligibility to the gate each step. Green
lines show these transferred PGCT connections. No policy update or new probe
estimation takes place. `--communication-graph none` disables this visualization
in the Python evaluator. The saved JSON records the transferred gate matrix.

## Map-size videos with unmixed shelves

```powershell
.\examples\run_pgct_09700_map_variants.ps1
```

This runs 6 and 8 agents on tiny (width 10, height 11), small (10 by 20),
and medium (16 by 20) maps, always with `HomeRatio=1.0`. Each scenario records
one 500-step episode by default, with PGCT connections displayed. The sensor
range remains 5 and the request queue remains one request per agent. Map growth
also adds shelf storage; the JSON includes map dimensions and shelf count.
Use `-Episodes 20` for multi-episode statistics. A single video's metrics should
not be interpreted as a statistical performance comparison.

Examples:

```powershell
# A quick video for each of the six scenarios.
.\examples\run_pgct_09700_generalization.ps1 -Episodes 1 -ShowVideos

# Only mixed shelves, for 6 and 8 agents.
.\examples\run_pgct_09700_generalization.ps1 -AgentCounts 6,8 -HomeRatios 0.75,0.5

# Include a 4-agent baseline and choose the output directory.
.\examples\run_pgct_09700_generalization.ps1 -AgentCounts 4,6,8 -OutputDir runs/pgct_09700_comparison
```

`-ShowVideos` opens the output video folder after evaluation. Rendering happens
offscreen while recording. `-Device cpu` is the default for small single-agent
inference batches; `-Device cuda` and `-Device auto` are also supported.
