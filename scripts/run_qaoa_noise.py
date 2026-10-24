"""
Noise and hardware-routing study for the QAOA benchmark (Round 2, item 2).

Takes the noiseless ramp-chain angles found by run_qaoa_benchmark.py (tight penalty) and
1. transpiles each circuit for an all-to-all device and for a heavy-hex lattice (IBM's
   layout), counting two-qubit gates and depth after routing;
2. samples the all-to-all circuit under a depolarising + readout noise model at several
   error rates with Qiskit Aer, and scores the samples exactly like the noiseless benchmark
   (probability of the exact optimum, feasible share);
3. repeats (2) with a "heavy-hex equivalent" two-qubit error e2' = 1 - (1 - e2)^r, where
   r = (2q gates after heavy-hex routing) / (2q gates all-to-all). This matches the total
   two-qubit error of the routed circuit but not its structure, so it is an approximation;
   simulating the routed circuit itself (~20 physical qubits) is not feasible here.

The noise model is generic, not a calibration of any specific IBM device.

Usage:
    python scripts/run_qaoa_noise.py
"""

import argparse
import json
import os
import sys
import time

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import numpy as np
from qiskit import transpile
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

from qrescue.quantum.ising import qubo_to_ising
from qrescue.quantum.qaoa_fast import ising_scale, qubo_energies
from qrescue.simulation.instances import model_from_dict
from qrescue.simulation.paircover import epoch_qubo
from run_qaoa_benchmark import feasible_mask

OUT = os.path.join(_ROOT, "reports", "qaoa_benchmark")
BASIS = ["cz", "rz", "sx", "x"]
# (two-qubit error, one-qubit error, readout error); 0 = ideal reference through the same pipeline
LEVELS = [(0.0, 0.0, 0.0), (0.002, 0.0002, 0.01), (0.005, 0.0005, 0.015), (0.01, 0.001, 0.02)]


def cost_operator(h, J, n):
    h_z, j_z, _ = qubo_to_ising(h, J, n)
    scale = ising_scale(h, J, n)
    labels, coeffs = [], []
    for i, c in enumerate(h_z):
        if abs(c) > 1e-12:
            s = ["I"] * n; s[i] = "Z"; labels.append("".join(reversed(s))); coeffs.append(c / scale)
    for (i, j), c in j_z.items():
        if abs(c) > 1e-12:
            s = ["I"] * n; s[i] = "Z"; s[j] = "Z"; labels.append("".join(reversed(s))); coeffs.append(c / scale)
    return SparsePauliOp(labels, coeffs)


def noise_model(e2, e1, ro):
    nm = NoiseModel(basis_gates=BASIS)
    if e1:
        nm.add_all_qubit_quantum_error(depolarizing_error(e1, 1), ["sx", "x"])
    if e2:
        nm.add_all_qubit_quantum_error(depolarizing_error(e2, 2), ["cz"])
    if ro:
        nm.add_all_qubit_readout_error(ReadoutError([[1 - ro, ro], [ro, 1 - ro]]))
    return nm


def two_qubit_count(circ):
    return sum(1 for inst in circ.data if inst.operation.num_qubits == 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--depths", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--per-size", type=int, default=2, help="instances per qubit count")
    args = ap.parse_args()
    inst = {d["id"]: d for d in json.load(open(os.path.join(OUT, "instances.json"), encoding="utf-8"))}
    rows = json.load(open(os.path.join(OUT, "results.json"), encoding="utf-8"))["rows"]
    ramp = {(r["id"], r["p"]): r for r in rows if r["init"] == "ramp" and r["penalty_factor"] == 1.0}
    chosen, seen = [], {}
    for iid, d in inst.items():
        if seen.get(d["qubits"], 0) < args.per_size:
            chosen.append(iid); seen[d["qubits"]] = seen.get(d["qubits"], 0) + 1
    heavy_hex = CouplingMap.from_heavy_hex(5)          # 57 qubits, enough room for routing
    out, t0 = [], time.time()
    for iid in chosen:
        model = model_from_dict(inst[iid])
        variables, h, J, const, _ = epoch_qubo(model)
        n = len(variables)
        energies = qubo_energies(h, J, n)
        opt = np.isclose(energies, energies.min())
        feas = feasible_mask(variables, n)
        op = cost_operator(h, J, n)
        for p in args.depths:
            r = ramp[(iid, p)]
            circ = QAOAAnsatz(op, reps=p).assign_parameters(r["params"])
            circ.measure_all()
            full = transpile(circ, basis_gates=BASIS, optimization_level=3, seed_transpiler=7)
            hh = transpile(circ, basis_gates=BASIS, coupling_map=heavy_hex, optimization_level=3, seed_transpiler=7)
            row = {"id": iid, "family": inst[iid]["family"], "qubits": n, "p": p, "couplings": len(J),
                   "ideal_p_opt": r["p_opt"], "ideal_p_feasible": r["p_feasible"],
                   "random_p_opt": r["random_p_opt"], "random_feasible_p_opt": r["random_feasible_p_opt"],
                   "random_p_feasible": r["random_p_feasible"],
                   "all_to_all_2q": two_qubit_count(full), "all_to_all_depth": full.depth(),
                   "heavy_hex_2q": two_qubit_count(hh), "heavy_hex_depth": hh.depth(), "noisy": []}
            ratio = row["heavy_hex_2q"] / max(row["all_to_all_2q"], 1)
            row["routing_ratio"] = ratio
            row["noisy_heavy_hex_equiv"] = []
            for e2, e1, ro in LEVELS:
                for key, e2_used in (("noisy", e2), ("noisy_heavy_hex_equiv", 1 - (1 - e2) ** ratio)):
                    sim = AerSimulator(noise_model=noise_model(e2_used, e1, ro), seed_simulator=11)
                    counts = sim.run(full, shots=args.shots).result().get_counts()
                    hits = sum(c for k, c in counts.items() if opt[int(k.replace(" ", ""), 2)])
                    ok = sum(c for k, c in counts.items() if feas[int(k.replace(" ", ""), 2)])
                    row[key].append({"e2": e2, "e2_used": e2_used, "e1": e1, "readout": ro,
                                     "p_opt": hits / args.shots, "p_feasible": ok / args.shots})
            out.append(row)
            print(f"{iid} p={p}: 2q all-to-all {row['all_to_all_2q']}, heavy-hex {row['heavy_hex_2q']}; "
                  f"p_opt ideal {row['ideal_p_opt']:.3f} -> " +
                  ", ".join(f"{x['p_opt']:.3f}" for x in row["noisy"]) + " | hh-equiv " +
                  ", ".join(f"{x['p_opt']:.3f}" for x in row["noisy_heavy_hex_equiv"]) + f"  ({time.time() - t0:.0f}s)", flush=True)
    json.dump({"config": vars(args) | {"levels": LEVELS, "basis": BASIS, "coupling": "heavy-hex d=5 (57 qubits), gate counts only"},
               "rows": out}, open(os.path.join(OUT, "noise_results.json"), "w", encoding="utf-8"), indent=1)
    print("wrote noise_results.json")


if __name__ == "__main__":
    main()
