"""
Rolling dispatch simulation: PairCover-Q vs closest-idle and a classical coverage-aware rule.

Every policy sees the identical synthetic call stream in each replication (common random
numbers), so differences are reported as paired differences against closest-idle with
95% t-intervals across replications.

Usage:
    python scripts/run_rolling_simulation.py            # full run (30 reps x 7 days)
    python scripts/run_rolling_simulation.py --quick    # 5 reps x 2 days, for a smoke check
"""

import argparse
import json
import os
import sys
import time

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "src"))

import numpy as np
from scipy import stats

from qrescue.simulation.engine import simulate, summarize
from qrescue.simulation.policies import ClosestIdle, CoverageSingle, PairCover
from qrescue.simulation.region import default_region, describe_region, generate_calls

METRICS = ["mean_response", "p90_response", "late_share", "p1_mean_response", "p1_late_share",
           "p2_mean_response", "p3_mean_response", "mean_queue_wait", "uncovered_demand"]


def policy_factories(lambdas):
    out = {"closest-idle": ClosestIdle, "coverage-single": CoverageSingle, "batch-no-coverage": lambda: PairCover(0.0)}
    for lam in lambdas:
        out[f"paircover-q (lam={lam:g})"] = (lambda lam=lam: PairCover(lam))
    return out


def paired(diffs):
    d = np.asarray(diffs, dtype=float)
    mean = float(d.mean())
    half = float(stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else float("nan")
    return {"mean": mean, "lo": mean - half, "hi": mean + half}


def run(args):
    region = default_region()
    factories = policy_factories(args.lambdas)
    results = {"config": vars(args) | {"policies": list(factories)}, "loads": {}}
    desc = describe_region(region, args.cover)
    results["region"] = {"ambulances": region.n_ambulances, "stations": len(region.stations), "zones": len(region.zones),
                         "demand_share_by_cover_count": desc.demand_by_cover_count}
    for rate in args.loads:
        per = {name: [] for name in factories}
        epoch_stats = {name: {"decisions": 0, "multi_call": 0, "differs_from_greedy": 0, "model_loss_mismatch": 0,
                              "eligibility_fallback": 0, "truncated": 0, "qubits": []} for name in factories}
        t0 = time.time()
        for rep in range(args.reps):
            calls = generate_calls(region, rate, args.days * 24, seed=args.seed + rep)
            for name, make in factories.items():
                policy = make()
                res = simulate(region, calls, policy, rate, epoch=args.epoch, cover_minutes=args.cover,
                               horizon_hours=args.days * 24)
                per[name].append(summarize(res, target=args.cover))
                if hasattr(policy.stats, "decisions"):
                    es = epoch_stats[name]
                    for k in es:
                        es[k] += getattr(policy.stats, k) if k != "qubits" else list(policy.stats.qubits)
        load = {"seconds": round(time.time() - t0, 1), "policies": {}}
        base, batch = per["closest-idle"], per["batch-no-coverage"]
        for name, runs in per.items():
            entry = {"mean": {m: float(np.mean([r[m] for r in runs])) for m in METRICS + ["calls", "deferrals"]},
                     "per_rep": {m: [r[m] for r in runs] for m in METRICS}}
            if name != "closest-idle":
                entry["diff_vs_closest"] = {m: paired([r[m] - b[m] for r, b in zip(runs, base)]) for m in METRICS}
            if name.startswith("paircover-q"):
                # what the coverage term adds on top of batch assignment alone
                entry["diff_vs_batch"] = {m: paired([r[m] - b[m] for r, b in zip(runs, batch)]) for m in METRICS}
            es = epoch_stats[name]
            if es["decisions"]:
                q = np.array(es.pop("qubits"))
                entry["epochs"] = es | {"qubits_mean": float(q.mean()), "qubits_p95": float(np.percentile(q, 95)),
                                        "qubits_max": int(q.max())}
            load["policies"][name] = entry
        results["loads"][str(rate)] = load
        print(f"load {rate}/h done in {load['seconds']}s")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loads", type=float, nargs="+", default=[2.0, 3.0, 4.0, 5.0])
    ap.add_argument("--lambdas", type=float, nargs="+", default=[5.0, 10.0, 20.0, 40.0])
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--epoch", type=float, default=2.0)
    ap.add_argument("--cover", type=float, default=12.0, help="coverage threshold and late-arrival target, minutes")
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--out", default=os.path.join(_ROOT, "reports", "rolling_simulation", "results.json"))
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    if args.quick:
        args.reps, args.days = 5, 2.0
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    res = run(args)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
