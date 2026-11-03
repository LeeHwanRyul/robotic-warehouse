"""Team-identification results of the v2 reward probe in one figure (read-only; all numbers from saved files).

(a) E59 offline replay, A+C IPPO seed 1, 0.26-5M experience, 15 pairs: decisions of v1 and v2
    (output/ac_offline_20261026/gate_eval.json, key 'v2').
(b) E65 training log, v2 gate + critic distillation, seed 1, 5M: mean response-distance EMA of compared
    same-team / cross-team pairs per 100k steps (output/pgct_docs_20261102/discovery_bins.csv).
(c) E73 final algorithm (pgct_max), branch from 1.024M, seeds 1 and 3: approved directed arcs
    (output/branch_wandb_20261103/update.csv, exported from W&B).

    python output/identification_figure_20261103/plot_identification.py
"""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BLUE, ORANGE, GREY, LIGHT = "#1F4E9A", "#C0504D", "#6B6B6B", "#BFBFBF"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})


def offline(ax):
    d = json.loads((ROOT / "output/ac_offline_20261026/gate_eval.json").read_text(encoding="utf-8"))
    d = d["corner/indiv A+C IPPO s1, 0.26-5M"]["v2"]
    rows = []
    for name in ("v1", "v2"):
        r = d[name]
        rows.append((name, r["true_accept_same"] + r["reject_cross"], r["reject_same"] + r["false_accept_cross"],
                     r["abstain_same"] + r["abstain_cross"], r["false_accept_cross"]))
    x = range(len(rows))
    correct = [r[1] for r in rows]
    wrong = [r[2] for r in rows]
    abstain = [r[3] for r in rows]
    ax.bar(x, correct, color=BLUE, width=.55, label="correct")
    ax.bar(x, wrong, bottom=correct, color=ORANGE, width=.55, label="wrong")
    ax.bar(x, abstain, bottom=[c + w for c, w in zip(correct, wrong)], color=LIGHT, width=.55, label="abstain")
    for i, (name, c, w, a, fx) in enumerate(rows):
        acc = c / (c + w) if c + w else float("nan")
        ax.text(i, 15.4, f"acc {acc:.2f}\ncross approved {fx}", ha="center", va="bottom", fontsize=6.5)
    ax.set_xticks(list(x), ["v1 (lookup)", "v2 (MLP)"])
    ax.set_ylim(0, 19)
    ax.set_yticks([0, 5, 10, 15])
    ax.set_ylabel("agent pairs (15)")
    ax.set_title("(a) offline replay, 5M experience", fontsize=8)
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3,
              handlelength=1, columnspacing=.8)


def training_log(ax):
    steps, same, cross = [], [], []
    with (ROOT / "output/pgct_docs_20261102/discovery_bins.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["same_ema"] and r["cross_ema"]:
                steps.append(float(r["step_million"]))
                same.append(float(r["same_ema"]))
                cross.append(float(r["cross_ema"]))
    ax.axvspan(4.28, 5.0, color=ORANGE, alpha=.08, lw=0)
    ax.text(4.64, 0.22, "cross-team\napprovals\nafter 4.28M", ha="center", va="bottom", fontsize=6, color=ORANGE)
    ax.plot(steps, cross, color=ORANGE, lw=1.5, label="other team")
    ax.plot(steps, same, color=BLUE, lw=1.5, label="same team")
    ax.axhline(.5, color=GREY, lw=.9, ls="--")
    ax.text(0.1, .52, "approval threshold 0.5", fontsize=6.5, color=GREY, va="bottom")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("env steps (M)")
    ax.set_ylabel("response-distance EMA")
    ax.set_title("(b) during training, seed 1", fontsize=8)
    ax.legend(frameon=False, fontsize=6.5, loc="center left", bbox_to_anchor=(0, .72))


def final_algorithm(ax):
    rows = {}
    with (ROOT / "output/branch_wandb_20261103/update.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["mode"] == "pgct_max" and r["seed"] in ("1", "3"):
                rows.setdefault(r["seed"], []).append(r)
    for seed, ls in (("1", "-"), ("3", "--")):
        rs = sorted(rows[seed], key=lambda r: int(r["step"]))
        x = [int(r["step"]) / 1e3 for r in rs]
        ax.plot(x, [float(r["update/max_gae_approved_same_team_arcs"]) for r in rs], color=BLUE, ls=ls, lw=1.5,
                label=f"same team, seed {seed}")
        ax.plot(x, [float(r["update/max_gae_approved_cross_team_arcs"]) for r in rs], color=ORANGE, ls=ls, lw=1.5,
                label=f"other team, seed {seed}")
    ax.axhline(6, color=GREY, lw=.8, ls=":")
    ax.text(495, 6.2, "all mature same-team arcs (6)", ha="right", va="bottom", fontsize=6, color=GREY)
    ax.set_xlim(0, 500)
    ax.set_ylim(-0.4, 8)
    ax.set_xlabel("steps after branch (k)")
    ax.set_ylabel("approved directed arcs")
    ax.set_title("(c) final PGCT online, seeds 1 & 3", fontsize=8)
    ax.legend(frameon=False, fontsize=6, loc="center right", bbox_to_anchor=(1, .45))


def main():
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 2.7), gridspec_kw=dict(width_ratios=[0.8, 1.1, 1.1]))
    offline(axes[0])
    training_log(axes[1])
    final_algorithm(axes[2])
    for ax in axes:
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout(pad=0.4, w_pad=1.2)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"team_identification_results.{ext}", dpi=220)


if __name__ == "__main__":
    main()
