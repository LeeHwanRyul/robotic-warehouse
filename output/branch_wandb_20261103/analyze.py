"""Pre-set comparison of the finished branch jobs (D96/D98): laggards a0, a1, a4 and leaders a2, a3, a5 (0-index),
evaluation deliveries per episode, same seed only. Reads eval.csv / update.csv / runs.json from fetch_wandb.py.

    python output/branch_wandb_20261103/analyze.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
LAG, LEAD = (0, 1, 4), (2, 3, 5)
EPISODES = 20  # periodic evaluation: per-agent counts are sums over 20 episodes


def per_agent(row):
    # W&B agent_k is 1-indexed
    return [float(row[f"eval/agent_{k + 1}_delivery_count"] or 0) / EPISODES for k in range(6)]


def main():
    meta = {m["name"]: m for m in json.loads((OUT / "runs.json").read_text(encoding="utf-8"))}
    evals = defaultdict(list)
    with (OUT / "eval.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            evals[r["name"]].append(r)
    result = {}
    for name, rows in sorted(evals.items()):
        if meta[name]["state"] != "finished":
            continue
        rows.sort(key=lambda r: int(r["step"]))
        pts = [(int(r["step"]), float(r["eval/deliveries"]), per_agent(r)) for r in rows]
        last3 = pts[-3:]
        agents = [sum(p[2][k] for p in last3) / 3 for k in range(6)]
        curve = [dict(step=s, team=d, laggards=sum(a[k] for k in LAG), leaders=sum(a[k] for k in LEAD),
                      agents=a) for s, d, a in pts]
        first_lag = {k: next((s for s, _, a in pts if a[k] >= 0.25), None) for k in LAG}
        result[name] = dict(mode=meta[name]["mode"], seed=meta[name]["seed"], points=len(pts),
                            last3_steps=[p[0] for p in last3],
                            team_last3=sum(p[1] for p in last3) / 3,
                            laggards_last3=sum(agents[k] for k in LAG), leaders_last3=sum(agents[k] for k in LEAD),
                            agents_last3=agents, first_step_laggard_ge_0_25=first_lag, curve=curve,
                            team_mean_all=sum(p[1] for p in pts) / len(pts))
    upd = defaultdict(list)
    with (OUT / "update.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            upd[r["name"]].append(r)
    for name, rows in upd.items():
        if name not in result:
            continue
        f = lambda k: [float(r[k]) for r in rows if r[k] not in ("", "None")]
        donors, same, cross = f("update/max_gae_donor_arcs"), f("update/max_gae_same_team_arcs"), f("update/max_gae_cross_team_arcs")
        res = dict(updates=len(rows), donor_arcs_total=sum(donors), same_team_arcs=sum(same), cross_team_arcs=sum(cross),
                   updates_with_donor=sum(d > 0 for d in donors))
        mature = f("update/max_gae_reward_mature_agents")
        if mature:
            res.update(mature_first=mature[0], mature_last=mature[-1],
                       approved_cross_max=max(f("update/max_gae_approved_cross_team_arcs") or [0]),
                       approved_same_last=f("update/max_gae_approved_same_team_arcs")[-1],
                       mature_agents_last={k: f(f"update/max_gae_reward_mature_agent_{k}")[-1] for k in range(6)})
        result[name]["max_gae"] = res
    (OUT / "summary.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"{'run':38s} {'team':>5s} {'lag':>5s} {'lead':>5s}  a0    a1    a2    a3    a4    a5   | donors same cross")
    for name, r in sorted(result.items(), key=lambda kv: (kv[1]["seed"], kv[1]["mode"])):
        a = " ".join(f"{x:5.2f}" for x in r["agents_last3"])
        m = r.get("max_gae", {})
        extra = (f"| {m.get('donor_arcs_total', 0):6.0f} {m.get('same_team_arcs', 0):5.0f} {m.get('cross_team_arcs', 0):5.0f}"
                 + (f" mature {m['mature_first']:.0f}->{m['mature_last']:.0f} apprX {m['approved_cross_max']:.0f}"
                    if "mature_first" in m else "")) if m else ""
        print(f"{r['mode'] + '_s' + str(r['seed']):38s} {r['team_last3']:5.2f} {r['laggards_last3']:5.2f} "
              f"{r['leaders_last3']:5.2f} {a} {extra}")
    print("\nlaggard first step with >= .25 deliveries/episode:")
    for name, r in sorted(result.items(), key=lambda kv: (kv[1]["seed"], kv[1]["mode"])):
        print(f"  {r['mode']}_s{r['seed']}: {r['first_step_laggard_ge_0_25']}")


if __name__ == "__main__":
    main()
