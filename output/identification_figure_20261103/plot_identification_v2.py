"""Slide version of the team-identification results: larger type, takeaway titles, direct labels, pairs not arcs.

Same sources as plot_identification.py (read-only):
(a) E59 offline replay (output/ac_offline_20261026/gate_eval.json): v1 vs v2 decisions on 15 agent pairs.
(b) E65 training log (output/pgct_docs_20261102/discovery_bins.csv): mean answer distance of compared pairs.
(c) E73 final PGCT online (output/branch_wandb_20261103/update.csv): approved pairs = directed arcs / 2.
Colours: reference palette slots 1-2 (blue = same team / correct, orange = other team / wrong).
Writes id_results.{pdf,png} (three panels) and id_a_offline / id_b_training / id_c_online.{pdf,png}.

    python output/identification_figure_20261103/plot_identification_v2.py
"""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID, ABSTAIN = "#0b0b0b", "#52514e", "#e4e3df", "#cfcdc6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "axes.titlepad": 10, "legend.frameon": False})


def tidy(ax, grid_axis="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def offline(ax):
    d = json.loads((ROOT / "output/ac_offline_20261026/gate_eval.json").read_text(encoding="utf-8"))
    d = d["corner/indiv A+C IPPO s1, 0.26-5M"]["v2"]
    rows = []
    for key, label in (("v2", "v2  (MLP)"), ("v1", "v1  (lookup table)")):
        r = d[key]
        correct = r["true_accept_same"] + r["reject_cross"]
        wrong = r["reject_same"] + r["false_accept_cross"]
        abstain = r["abstain_same"] + r["abstain_cross"]
        rows.append((label, correct, wrong, abstain))
    for y, (label, c, w, a) in enumerate(rows):
        left = 0
        for n, color, name, text_color in ((c, BLUE, "correct", "white"), (w, ORANGE, "wrong", "white"),
                                           (a, ABSTAIN, "abstain", INK)):
            if n:
                ax.barh(y, n, left=left, height=0.56, color=color, edgecolor="white", linewidth=2,
                        label=name if y == 1 else None)
                ax.text(left + n / 2, y, f"{n}", ha="center", va="center", color=text_color,
                        fontsize=12, fontweight="bold")
            left += n
        ax.text(15.4, y, f"{c}/{c + w} correct", ha="left", va="center", color=INK2, fontsize=10.5)
    ax.set_yticks([0, 1], [r[0] for r in rows])
    ax.set_xlim(0, 15)
    ax.set_xticks([0, 5, 10, 15])
    ax.set_xlabel("agent pairs judged (15 in total)")
    ax.set_ylim(-0.55, 1.55)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=10, handlelength=1.2,
              columnspacing=1.2, borderaxespad=0.2)
    ax.set_title("(a) Offline: v2 judges every decided pair correctly", pad=30)
    tidy(ax, "x")


def training(ax):
    steps, same, cross = [], [], []
    with (ROOT / "output/pgct_docs_20261102/discovery_bins.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["same_ema"] and r["cross_ema"]:
                steps.append(float(r["step_million"]))
                same.append(float(r["same_ema"]))
                cross.append(float(r["cross_ema"]))
    ax.axvspan(4.28, 5.0, color=ORANGE, alpha=0.08, lw=0)
    ax.text(4.64, 0.97, "some other-team\npairs approved", ha="center", va="top", fontsize=9, color=INK2)
    ax.axhline(0.5, color=INK2, lw=1.0, ls=(0, (4, 3)))
    ax.text(0.08, 0.515, "approve below 0.5", fontsize=9.5, color=INK2, va="bottom")
    ax.plot(steps, cross, color=ORANGE, lw=2.2, label="other-team pairs")
    ax.plot(steps, same, color=BLUE, lw=2.2, label="teammate pairs")
    ax.text(0.12, 0.93, "other team", color=INK, fontsize=10.5, ha="left", va="top")
    ax.text(1.0, same[8] + 0.05, "teammates", color=INK, fontsize=10.5, ha="left", va="bottom")
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("training steps (M)")
    ax.set_ylabel("answer distance  (0 = same answers)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=10, handlelength=1.6,
              borderaxespad=0.2)
    ax.set_title("(b) Training: teammates give similar answers", pad=30)
    tidy(ax)


def online(ax):
    rows = {}
    with (ROOT / "output/branch_wandb_20261103/update.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["mode"] == "pgct_max" and r["seed"] in ("1", "3"):
                rows.setdefault(r["seed"], []).append(r)
    cross_max = 0.0
    for seed, ls in (("1", "-"), ("3", (0, (5, 2)))):
        rs = sorted(rows[seed], key=lambda r: int(r["step"]))
        x = [int(r["step"]) / 1e3 for r in rs]
        same = [float(r["update/max_gae_approved_same_team_arcs"]) / 2 for r in rs]
        cross = [float(r["update/max_gae_approved_cross_team_arcs"]) / 2 for r in rs]
        cross_max = max(cross_max, max(cross))
        ax.step(x, same, where="post", color=BLUE, lw=2.2, ls=ls, label=f"teammate pairs, seed {seed}")
        if seed == "1":
            ax.step(x, cross, where="post", color=ORANGE, lw=2.2, label="other-team pairs (both seeds)")
    ax.text(255, 3.12, "seed 1", color=INK, fontsize=10, ha="left", va="bottom")
    ax.text(405, 2.0, "seed 3", color=INK, fontsize=10, ha="left", va="center")
    ax.text(60, 0.15, f"other team: {cross_max:.0f} approved", color=INK, fontsize=10, ha="left", va="bottom")
    ax.axhline(6, color=INK2, lw=1.0, ls=(0, (4, 3)))
    ax.text(495, 6.08, "all 6 teammate pairs", fontsize=9.5, color=INK2, ha="right", va="bottom")
    ax.text(495, 3.6, "3 = every pair whose agents\nhad their own reward events", fontsize=9, color=INK2,
            ha="right", va="bottom")
    ax.set_xlim(0, 500)
    ax.set_ylim(-0.2, 6.7)
    ax.set_yticks(range(0, 7))
    ax.set_xlabel("steps after branch (k)")
    ax.set_ylabel("approved pairs")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88), ncol=1, fontsize=9, handlelength=1.8,
              borderaxespad=0.2)
    ax.set_title("(c) Final PGCT online: only teammates approved", pad=30)
    tidy(ax)


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6), gridspec_kw=dict(width_ratios=[1.0, 1.1, 1.1]))
    offline(axes[0])
    training(axes[1])
    online(axes[2])
    fig.tight_layout(w_pad=3.0)
    save(fig, "id_results")
    for name, draw, size in (("id_a_offline", offline, (6.2, 3.6)), ("id_b_training", training, (6.2, 4.2)),
                             ("id_c_online", online, (6.2, 4.4))):
        fig, ax = plt.subplots(figsize=size)
        draw(ax)
        fig.tight_layout()
        save(fig, name)


if __name__ == "__main__":
    main()
