"""Curriculum 2: continue from delivery policy and learn shelf return."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = THIS_DIR.parent
PROJECT_ROOT = EXAMPLES_DIR.parent
TRAIN_SCRIPT = EXAMPLES_DIR / "train_recurrent_ippo_consensus.py"
ENV_KWARGS = THIS_DIR / "env_kwargs.json"
DEFAULT_STAGE1_CHECKPOINT = (
    PROJECT_ROOT
    / "runs"
    / "recurrent_ippo_consensus"
    / "curriculum1_1ag_delivery_sr2"
    / "final.pt"
)


DEFAULT_ARGS = [
    "--env-id",
    "rware-multiteam-tiny-4ag-2teams-v0",
    "--agent-count",
    "1",
    "--team-count",
    "1",
    "--sensor-range",
    "2",
    "--env-kwargs-json",
    f"@{ENV_KWARGS}",
    "--init-checkpoint",
    str(DEFAULT_STAGE1_CHECKPOINT),
    "--transfer-components",
    "actor",
    "--total-timesteps",
    "5000000",
    "--rollout-steps",
    "2048",
    "--sequence-length",
    "128",
    "--learning-rate",
    "1e-4",
    "--entropy-coef",
    "0.01",
    "--eval-interval",
    "50",
    "--eval-episodes",
    "20",
    "--eval-horizon",
    "500",
    "--save-interval",
    "100",
    "--exp-name",
    "curriculum2_1ag_return_sr2",
    "--track",
    "--wandb-project",
    "rware-curriculum",
    "--wandb-group",
    "1ag_sr2_curriculum",
    "--wandb-name",
    "curriculum2_1ag_return_sr2",
    "--wandb-log-eval-video",
    "--wandb-video-interval",
    "5",
]


def main() -> None:
    sys.argv = [str(TRAIN_SCRIPT), *DEFAULT_ARGS, *sys.argv[1:]]
    runpy.run_path(str(TRAIN_SCRIPT), run_name="__main__")


if __name__ == "__main__":
    main()
