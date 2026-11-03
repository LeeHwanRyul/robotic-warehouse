"""Read-only export of the two 1M-checkpoint branch experiments from W&B (project rware-from-scratch).

Groups: maxgae_br1M_20261102_165216 (stage 1: ippo / oracle_max / oracle_maxd1 / allk_max) and
pgctd2_br1M_20261102_180212 (stage 2: oracle_mature_max / pgct_max), seeds 1, 3, 5, 0.5M steps each, branched
from the A+C IPPO seed-1 checkpoint at 1,024,000 steps. The local run folders are on the training PC.
Writes runs.json, eval.csv (periodic + final evaluation) and update.csv (Max-GAE / v2 audit per update).

    python output/branch_wandb_20261103/fetch_wandb.py
"""
import csv
import json
from pathlib import Path

import wandb

OUT = Path(__file__).resolve().parent
PROJECT = "t98339-hanyang-university/rware-from-scratch"
GROUPS = ["maxgae_br1M_20261102_165216", "pgctd2_br1M_20261102_180212"]
AGENTS = range(1, 7)  # W&B eval keys are 1-indexed: agent_k = 0-index k-1
EVAL = ["eval/deliveries", "eval/returns_home"] + [f"eval/agent_{k}_delivery_count" for k in AGENTS]
UPDATE = ["update/max_gae_donor_arcs", "update/max_gae_same_team_arcs", "update/max_gae_cross_team_arcs",
          "update/max_gae_receivers", "update/max_gae_adv_shift", "update/max_gae_eta_eff",
          "update/max_gae_select_frac", "update/max_gae_mean_b", "update/max_gae_reward_mature_agents",
          "update/max_gae_approved_same_team_arcs", "update/max_gae_approved_cross_team_arcs"]
UPDATE += [f"update/max_gae_reward_mature_agent_{k}" for k in range(6)]  # these are 0-indexed


def main():
    api = wandb.Api(timeout=120)
    runs = api.runs(PROJECT, filters={"$or": [{"group": g} for g in GROUPS]})
    meta, eval_rows, update_rows = [], [], []
    for r in runs:
        name = r.name
        mode = name.split("br01000_")[1].rsplit("_s", 1)[0]
        seed = int(name.rsplit("_s", 1)[1])
        meta.append(dict(name=name, id=r.id, group=r.group, state=r.state, mode=mode, seed=seed,
                         last_step=r.summary.get("_step"),
                         final_eval={k: r.summary.get(k.replace("eval/", "eval/final_"))
                                     for k in EVAL}))
        for row in r.scan_history(page_size=1000):  # full rows; keep only the logged eval / Max-GAE values
            base = dict(name=name, mode=mode, seed=seed, step=row.get("_step"))
            if row.get("eval/deliveries") is not None:
                eval_rows.append(dict(base, **{k: row.get(k) for k in EVAL}))
            if row.get("update/max_gae_donor_arcs") is not None:
                update_rows.append(dict(base, **{k: row.get(k) for k in UPDATE}))
        print(name, r.state, len([e for e in eval_rows if e["name"] == name]), "eval rows",
              len([u for u in update_rows if u["name"] == name]), "update rows", flush=True)
    (OUT / "runs.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    for fname, rows, keys in (("eval.csv", eval_rows, EVAL), ("update.csv", update_rows, UPDATE)):
        with (OUT / fname).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["name", "mode", "seed", "step"] + keys)
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
