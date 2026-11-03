"""Slide figures from the exported branch logs (fetch_wandb.py). Finished jobs only.

team_identification.(pdf|png): PGCT-D2 (pgct_max) online discovery after the branch, seeds 1 and 3:
    (a) agents with a mature reward predictor, (b) approved same-team vs cross-team directed arcs.
learning_seed1.(pdf|png): seed-1 evaluation deliveries per episode (team total, and laggards a0+a1+a4), all modes.
    Preliminary: one seed per mode; stage 1 seeds 3 and 5 and pgct_max seed 5 are still running.

    python output/branch_wandb_20261103/plot_slides.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parent
BLUE, ORANGE, GREEN, GREY = "#1F4E9A", "#C0504D", "#2E7D4F", "#6B6B6B"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})


def load(fname):
    rows = defaultdict(list)
    with (OUT / fname).open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[(r["mode"], int(r["seed"]))].append(r)
    for v in rows.values():
        v.sort(key=lambda r: int(r["step"]))
    return rows


def num(r, k):
    return float(r[k]) if r[k] not in ("", "None") else None


def team_identification(upd, finished):
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 2.3))
    for seed, ls in ((1, "-"), (3, "--")):
        rs = upd[("pgct_max", seed)]
        if ("pgct_max", seed) not in finished:
            continue
        x = [int(r["step"]) / 1e3 for r in rs]
        a.plot(x, [num(r, "update/max_gae_reward_mature_agents") for r in rs], color=BLUE, ls=ls, lw=1.4,
               label=f"seed {seed}")
        b.plot(x, [num(r, "update/max_gae_approved_same_team_arcs") for r in rs], color=BLUE, ls=ls, lw=1.4,
               label=f"same team, seed {seed}")
        b.plot(x, [num(r, "update/max_gae_approved_cross_team_arcs") for r in rs], color=ORANGE, ls=ls, lw=1.4,
               label=f"other team, seed {seed}")
    a.set_ylim(0, 6.3)
    a.set_ylabel("agents")
    a.set_title("(a) mature reward predictors", fontsize=8)
    b.axhline(12, color=GREY, lw=.8, ls=":")
    b.text(500, 11.5, "all same-team arcs (12)", ha="right", va="top", fontsize=7, color=GREY)
    b.set_ylim(-0.5, 13)
    b.set_ylabel("approved directed arcs")
    b.set_title("(b) approvals", fontsize=8)
    for ax in (a, b):
        ax.set_xlim(0, 500)
        ax.set_xlabel("steps after branch (k)")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    a.legend(frameon=False, fontsize=7, loc="lower right")
    b.legend(frameon=False, fontsize=6.5, loc="center right")
    fig.tight_layout(pad=0.3)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"team_identification.{ext}", dpi=200)
    plt.close(fig)


def learning_seed1(ev, finished):
    styles = {"ippo": (GREY, "-", "IPPO (continue)"), "oracle_max": (BLUE, "-", "true team, D2"),
              "oracle_maxd1": (BLUE, ":", "true team, D1"), "allk_max": (ORANGE, ":", "random donors (count-matched)"),
              "oracle_mature_max": (GREEN, "--", "true team, mature only"), "pgct_max": (GREEN, "-", "PGCT")}
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 2.75))
    for mode, (c, ls, label) in styles.items():
        if (mode, 1) not in finished:
            continue
        rs = ev[(mode, 1)]
        x = [int(r["step"]) / 1e3 for r in rs]
        a.plot(x, [num(r, "eval/deliveries") for r in rs], color=c, ls=ls, lw=1.3, label=label)
        lag = [sum((num(r, f"eval/agent_{k + 1}_delivery_count") or 0) for k in (0, 1, 4)) / 20 for r in rs]
        b.plot(x, lag, color=c, ls=ls, lw=1.3)
    a.set_title("(a) team deliveries / episode", fontsize=8)
    b.set_title("(b) laggards a0+a1+a4 deliveries / episode", fontsize=8)
    for ax in (a, b):
        ax.set_xlim(0, 500)
        ax.set_xlabel("steps after branch (k)")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.legend(*a.get_legend_handles_labels(), frameon=False, fontsize=6.5, loc="lower center", ncol=3)
    fig.tight_layout(pad=0.3, rect=(0, 0.17, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"learning_seed1.{ext}", dpi=200)
    plt.close(fig)


def main():
    meta = json.loads((OUT / "runs.json").read_text(encoding="utf-8"))
    finished = {(m["mode"], m["seed"]) for m in meta if m["state"] == "finished"}
    team_identification(load("update.csv"), finished)
    learning_seed1(load("eval.csv"), finished)
    print(sorted(finished))


if __name__ == "__main__":
    main()
