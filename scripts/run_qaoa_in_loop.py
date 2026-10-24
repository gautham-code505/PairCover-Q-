"""
QAOA in the loop: PairCover-Q with a QAOA solver inside the rolling simulation, compared
with the same policy using the exact solver on identical call streams (Round 2, item 2).

Usage:
    python scripts/run_qaoa_in_loop.py
"""

import argparse
import json
import os
import sys
import time

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "src"))

import numpy as np

from qrescue.quantum.loop_solver import QAOASolver
from qrescue.simulation.engine import simulate, summarize
from qrescue.simulation.policies import PairCover
from qrescue.simulation.region import default_region, generate_calls

OUT = os.path.join(_ROOT, "reports", "qaoa_benchmark")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loads", type=float, nargs="+", default=[4.0, 5.0])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--lam", type=float, default=5.0)
    ap.add_argument("--p", type=int, default=2)
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=7000)
    args = ap.parse_args()
    region = default_region()
    out = {"config": vars(args), "loads": {}}
    for rate in args.loads:
        reps = []
        for rep in range(args.reps):
            calls = generate_calls(region, rate, args.days * 24, seed=args.seed + rep)
            t0 = time.time()
            solver = QAOASolver(p=args.p, shots=args.shots, seed=args.seed + rep)
            q = summarize(simulate(region, calls, PairCover(args.lam, solver=solver), rate, horizon_hours=args.days * 24))
            e = summarize(simulate(region, calls, PairCover(args.lam), rate, horizon_hours=args.days * 24))
            st = solver.stats
            reps.append({"qaoa": q, "exact": e, "seconds": time.time() - t0,
                         "stats": {k: v for k, v in st.__dict__.items() if not isinstance(v, list)},
                         "qubits_hist": np.bincount(st.qubits).tolist() if st.qubits else [],
                         "mean_p_opt": float(np.mean(st.p_opt)) if st.p_opt else None,
                         "mean_random_p_opt": float(np.mean(st.random_p_opt)) if st.random_p_opt else None})
            print(f"load {rate} rep {rep}: {reps[-1]['stats']} ({reps[-1]['seconds']:.0f}s)", flush=True)
        out["loads"][str(rate)] = reps
    json.dump(out, open(os.path.join(OUT, "in_loop_results.json"), "w", encoding="utf-8"), indent=1)
    print("wrote in_loop_results.json")


if __name__ == "__main__":
    main()
