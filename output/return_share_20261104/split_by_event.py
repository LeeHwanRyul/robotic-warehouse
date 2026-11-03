"""Direct test of the 'return events fill the probes' hypothesis on saved v2 states (read-only; no training).

For each checkpoint, rebuild every agent's reward predictor and its saved own-event buffer, build the common
probes of each agent pair as the run did (32 most recent own events of each agent, plus mirrors if the run used
them), split them into deliveries and shelf returns, and compute the response distance on all probes, on
delivery probes only and on return probes only. Team labels are used only to label pairs in the report.

Return = TOGGLE_LOAD while carrying that leaves the agent not carrying; every other event is a delivery
(events are own rewards >= 0.5; in this task only deliveries and returns reach that).

    python output/return_share_20261104/split_by_event.py --run runs/acv2_s1_20261029_084340/b6_corner_indiv_pen005_acv2_pgct_s1
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "latent_team"))
import reward_probe_ac_v2 as AC2  # noqa: E402

TEAMS = [0, 1, 0, 1, 0, 1]  # 0-index 0,2,4 = team 0 (report labels only)
CARRY, TOGGLE = 0, 4        # public ego index of 'carrying'; TOGGLE_LOAD action


def load(path):
    ck = torch.load(path, map_location="cpu", weights_only=False)
    state = ck["reward_probe_ac_v2"]
    config = AC2.ACV2Config(**state["config"])
    agents = []
    for s in state["predictors"]:
        p = AC2.RewardPredictor(config, 0)
        p.net.load_state_dict(s["net"])
        p.version, p.events_seen = s["version"], s["events_seen"]
        agents.append(dict(pred=p, before=np.asarray(s["event_before"]), action=np.asarray(s["event_action"]),
                           after=np.asarray(s["event_after"])))
    return config, agents


def kinds(before, action, after):
    return np.where((action == TOGGLE) & (before[:, CARRY] == 1) & (after[:, CARRY] == 0), "return", "delivery")


def mature(config, agent):
    p = agent["pred"]
    n = config.probes_per_agent
    if p.events_seen < config.min_events or p.version == 0 or len(agent["before"]) == 0:
        return False
    return bool(p.predict(agent["before"][:n], agent["action"][:n], agent["after"][:n]).mean()
                >= config.min_event_response)


def pair(config, ai, aj):
    n = config.probes_per_agent  # buffers are saved most-recent first
    b = np.concatenate([ai["before"][:n], aj["before"][:n]])
    a = np.concatenate([ai["action"][:n], aj["action"][:n]])
    f = np.concatenate([ai["after"][:n], aj["after"][:n]])
    k = kinds(b, a, f)
    if config.mirror and len(b):
        r = config.radius
        b, a, f = (np.concatenate([b, AC2.mirror_view(b, r)]), np.concatenate([a, AC2.mirror_action(a)]),
                   np.concatenate([f, AC2.mirror_view(f, r)]))
        k = np.concatenate([k, k])
    if len(b) < config.min_probes:
        return None
    p, q = ai["pred"].predict(b, a, f), aj["pred"].predict(b, a, f)
    out = dict(probes=int(len(b)), return_share=float(np.mean(k == "return")),
               distance_all=AC2.response_distance(p, q))
    for kind in ("delivery", "return"):
        m = k == kind
        out[f"distance_{kind}"] = AC2.response_distance(p[m], q[m]) if m.any() else None
        out[f"mean_answer_{kind}"] = [float(p[m].mean()), float(q[m].mean())] if m.any() else None
    return out


def summarize(rows, relation):
    sel = [r for r in rows if r["relation"] == relation and r["both_mature"]]
    out = dict(pairs=len(sel))
    for key in ("return_share", "distance_all", "distance_delivery", "distance_return"):
        vals = [r[key] for r in sel if r[key] is not None]
        out[key] = float(np.mean(vals)) if vals else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True, help="job folder holding checkpoint_*.pt")
    ap.add_argument("--checkpoints", nargs="+", default=["checkpoint_01000.pt", "checkpoint_03000.pt",
                                                           "checkpoint_04750.pt", "final.pt"])
    ap.add_argument("--rollout-steps", type=int, default=1024)
    args = ap.parse_args()
    report = {}
    for name in args.checkpoints:
        path = args.run / name
        if not path.is_file():
            print(f"skip {name}: not found")
            continue
        config, agents = load(path)
        ok = [mature(config, a) for a in agents]
        rows = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                res = pair(config, agents[i], agents[j])
                if res is None:
                    continue
                rows.append(dict(i=i, j=j, relation="same" if TEAMS[i] == TEAMS[j] else "cross",
                                 both_mature=ok[i] and ok[j], **res))
        m = re.search(r"(\d+)", name)
        steps = int(m.group(1)) * args.rollout_steps if m else None
        report[name] = dict(env_steps=steps, mirror=config.mirror, mature=ok, pairs=rows,
                            same=summarize(rows, "same"), cross=summarize(rows, "cross"))
        s, c = report[name]["same"], report[name]["cross"]
        fmt = lambda v: "  -  " if v is None else f"{v:.2f}"
        print(f"{name} ({steps} steps), mature {sum(ok)}/6, mirror {config.mirror}")
        for label, x in (("same ", s), ("cross", c)):
            print(f"  {label} pairs {x['pairs']:2d}  return share {fmt(x['return_share'])}  distance all "
                  f"{fmt(x['distance_all'])}  delivery-only {fmt(x['distance_delivery'])}  "
                  f"return-only {fmt(x['distance_return'])}")
    out = Path(__file__).resolve().parent / f"split_{args.run.name}.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
