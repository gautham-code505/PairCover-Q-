"""
QAOA benchmark on PairCover-Q epoch QUBOs (Round 2, item 2).

For every frozen instance and penalty strength, runs noiseless QAOA at depth p = 1, 2, 3:
- one deterministic "ramp" chain (linear-ramp start at p=1, INTERP warm start for p+1);
- 20 random-start runs per depth as a control for initialisation luck (at the tight
  penalty only; the penalty sweep uses the deterministic ramp chain).
Every number is compared with uniform random sampling over all 2^n bitstrings and over
feasible bitstrings. Ground truth is exact enumeration of the QUBO, cross-checked with the
exact assignment solver.

Usage:
    python scripts/run_qaoa_benchmark.py            # full run
    python scripts/run_qaoa_benchmark.py --quick    # 2 instances per size, 3 random starts
"""

import argparse
import json
import os
import sys
import time

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "src"))

import numpy as np

from qrescue.quantum.qaoa_fast import bit_matrix, interp, ising_scale, linear_ramp, optimize, qubo_energies
from qrescue.simulation.instances import harvest_operational, model_from_dict, surge_instances
from qrescue.simulation.paircover import epoch_qubo, objective, solve_exact
from qrescue.simulation.region import default_region

OUT = os.path.join(_ROOT, "reports", "qaoa_benchmark")
SHOTS = 1024


def freeze_instances(path, args):
    if os.path.exists(path) and not args.rebuild:
        return json.load(open(path, encoding="utf-8"))
    rng = np.random.default_rng(args.seed)
    region = default_region()
    inst = harvest_operational(region, 4.0, args.lam, range(args.seed, args.seed + 6), [4, 5, 6, 7], 2, rng)
    inst += surge_instances(region, 5.0, args.lam, [8, 10, 12], args.per_size, rng)
    for i, d in enumerate(inst):
        d["id"] = f"{d['family'][:4]}-{d['qubits']}q-{i}"
    json.dump(inst, open(path, "w", encoding="utf-8"), indent=1)
    return inst


def feasible_mask(variables, n):
    x = bit_matrix(n).astype(int)
    units = sorted({u for u, _ in variables})
    calls = sorted({j for _, j in variables})
    by_unit = np.array([[1 if v[0] == u else 0 for u in units] for v in variables])
    by_call = np.array([[1 if v[1] == j else 0 for j in calls] for v in variables])
    return ((x @ by_unit) <= 1).all(1) & ((x @ by_call) <= 1).all(1)


def score(probs, opt_mask, feas_mask, shots=SHOTS):
    p_opt = float(probs[opt_mask].sum())
    return {"p_opt": p_opt, "p_feasible": float(probs[feas_mask].sum()),
            "argmax_is_optimal": bool(opt_mask[int(np.argmax(probs))]),
            "p_hit_in_shots": float(1 - (1 - p_opt) ** shots)}


def run_instance(d, args, rng):
    model = model_from_dict(d)
    rows = []
    for factor in args.penalties:
        variables, h, J, const, p0 = epoch_qubo(model)
        penalty = factor * p0
        variables, h, J, const, _ = epoch_qubo(model, penalty)
        n = len(variables)
        energies = qubo_energies(h, J, n)
        scale = ising_scale(h, J, n)
        feas = feasible_mask(variables, n)
        e_min = energies.min()
        opt = np.isclose(energies, e_min)
        # ground-truth checks: the QUBO minimiser is feasible and equals the exact assignment optimum
        _, exact = solve_exact(model, allow_deferral=True)
        assert feas[opt].all() and abs(e_min + const - exact) < 1e-6, d["id"]
        no_cov = model_from_dict({**d, "lam": 0.0})
        a_cov, _ = solve_exact(model, True)
        a_nocov, _ = solve_exact(no_cov, True)
        base = {"id": d["id"], "family": d["family"], "qubits": n, "penalty_factor": factor, "penalty": penalty,
                "n_feasible": int(feas.sum()), "n_optimal": int(opt.sum()),
                "random_p_opt": float(opt.sum() / 2 ** n), "random_p_feasible": float(feas.mean()),
                "random_feasible_p_opt": float(opt.sum() / feas.sum()),
                "random_p_hit_in_shots": float(1 - (1 - opt.sum() / 2 ** n) ** SHOTS),
                "coverage_changes_answer": sorted(a_cov) != sorted(a_nocov),
                "couplings": len(J)}
        prev = None
        for p in (1, 2, 3):
            x0 = linear_ramp(p) if prev is None else interp(prev)
            r = optimize(energies, scale, p, x0, maxiter=args.maxiter)
            prev = r["params"]
            rows.append(base | {"p": p, "init": "ramp", "seed": -1, "nfev": r["nfev"], "seconds": r["seconds"],
                                "expectation": r["expectation"] + const, "params": r["params"].tolist()}
                        | score(r["probs"], opt, feas))
            # random-start control only at the standard (tight) penalty
            for s in range(args.random_starts if factor == args.penalties[0] else 0):
                x0 = np.concatenate([rng.uniform(0, np.pi, p), rng.uniform(0, 2 * np.pi, p)])
                r = optimize(energies, scale, p, x0, maxiter=args.maxiter)
                rows.append(base | {"p": p, "init": "random", "seed": s, "nfev": r["nfev"], "seconds": r["seconds"],
                                    "expectation": r["expectation"] + const}
                            | score(r["probs"], opt, feas))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lam", type=float, default=5.0)
    ap.add_argument("--per-size", type=int, default=5)
    ap.add_argument("--penalties", type=float, nargs="+", default=[1.0, 2.0, 4.0])
    ap.add_argument("--random-starts", type=int, default=20)
    ap.add_argument("--maxiter", type=int, default=500)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--rebuild", action="store_true", help="rebuild the frozen instance set")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    inst = freeze_instances(os.path.join(OUT, "instances.json"), args)
    if args.quick:
        args.random_starts = 3
        seen, keep = {}, []
        for d in inst:
            if seen.get(d["qubits"], 0) < 2:
                keep.append(d); seen[d["qubits"]] = seen.get(d["qubits"], 0) + 1
        inst = keep
    rng = np.random.default_rng(args.seed)
    rows, t0 = [], time.time()
    for d in inst:
        rows += run_instance(d, args, rng)
        print(f"{d['id']}: done ({time.time() - t0:.0f}s)", flush=True)
    out = os.path.join(OUT, "results_quick.json" if args.quick else "results.json")
    json.dump({"config": vars(args), "shots": SHOTS, "rows": rows}, open(out, "w", encoding="utf-8"))
    print("wrote", out)


if __name__ == "__main__":
    main()
