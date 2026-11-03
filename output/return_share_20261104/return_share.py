"""Indirect check of the 'return events fill the probes' hypothesis (T204/T206), from W&B logs only (read-only).

Run: A+C v2 gate + critic distillation, seed 1, 5M (W&B q2u47mml, group acv2_s1_20261029_084340; E65).
Per 250k-step bin: share of shelf returns among the agents' large reward events (deliveries + returns, both +1),
from train/agent_k_{delivery,return}_count, next to the logged same/cross response-distance EMA
(update/ac_v2_audit_distance_*) and the number of cross-team accepted comparisons.
This is a time correlation, not a causal test; the checkpoint analysis (split_by_event.py) is the direct test.

    python output/return_share_20261104/return_share.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import wandb  # noqa: E402

OUT = Path(__file__).resolve().parent
RUN = "t98339-hanyang-university/rware-from-scratch/q2u47mml"
BIN = 250_000
TEAM = {1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1}  # W&B agent_k (1-indexed): 0-index 0,2,4 = team 0
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#52514e"


def main():
    run = wandb.Api(timeout=120).run(RUN)
    bins = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(lambda: defaultdict(int))
    rows = 0
    for row in run.scan_history(page_size=2000):
        step = row.get("_step")
        if step is None:
            continue
        b = int(step // BIN)
        if row.get("train/agent_1_delivery_count") is not None:
            rows += 1
            for k in range(1, 7):
                d = row.get(f"train/agent_{k}_delivery_count") or 0.0
                r = row.get(f"train/agent_{k}_return_count") or 0.0
                bins[b]["deliveries"] += d
                bins[b]["returns"] += r
                bins[b][f"t{TEAM[k]}_deliveries"] += d
                bins[b][f"t{TEAM[k]}_returns"] += r
        for key, name in (("update/ac_v2_audit_distance_cross", "cross"), ("update/ac_v2_audit_distance_same", "same"),
                          ("update/ac_v2_audit_cross_accepted", "cross_accepted"),
                          ("update/ac_v2_audit_same_accepted", "same_accepted")):
            v = row.get(key)
            if v is not None and v == v:
                bins[b][name + "_sum"] += float(v)
                counts[b][name] += 1
    table = []
    for b in sorted(bins):
        x = bins[b]
        events = x["deliveries"] + x["returns"]
        rec = dict(step_million=(b + 0.5) * BIN / 1e6, deliveries=x["deliveries"], returns=x["returns"],
                   return_share=x["returns"] / events if events else None)
        for name in ("cross", "same"):
            rec[name + "_ema"] = x[name + "_sum"] / counts[b][name] if counts[b][name] else None
        for name in ("cross_accepted", "same_accepted"):
            rec[name] = x[name + "_sum"]
        table.append(rec)
    with (OUT / "return_share.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    pairs = [(t["return_share"], t["cross_ema"]) for t in table if t["return_share"] is not None and t["cross_ema"] is not None]
    n = len(pairs)
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    cov = sum((p[0] - mx) * (p[1] - my) for p in pairs)
    corr = cov / (sum((p[0] - mx) ** 2 for p in pairs) * sum((p[1] - my) ** 2 for p in pairs)) ** 0.5
    summary = dict(run=RUN, train_rows=rows, bins=len(table), corr_return_share_vs_cross_ema=corr)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    xs = [t["step_million"] for t in table]
    ax.plot(xs, [t["return_share"] for t in table], color=GREY, lw=2, label="share of returns among reward events")
    ax.plot(xs, [t["cross_ema"] for t in table], color=ORANGE, lw=2, label="other-team answer distance")
    ax.plot(xs, [t["same_ema"] for t in table], color=BLUE, lw=2, label="teammate answer distance")
    ax.axhline(0.5, color=GREY, lw=0.8, ls=(0, (4, 3)))
    ax.axvline(4.28, color=ORANGE, lw=0.8, ls=":")
    ax.text(4.25, 0.22, "first cross-team\napproval", ha="right", va="bottom", fontsize=8, color=GREY)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("training steps (M)")
    ax.set_title(f"Return share vs. other-team distance (seed 1; r = {corr:.2f})", loc="left", fontsize=11)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e4e3df", lw=0.8)
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "return_share.png", dpi=200)
    print(json.dumps(summary, indent=1))
    for t in table:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in t.items()})


if __name__ == "__main__":
    main()
