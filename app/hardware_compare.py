"""
Classical vs quantum on one dispatch problem: live classical solvers and the noiseless QAOA
simulator, next to the stored results of the same circuit on IBM backends.

The problems are the frozen QAOA-benchmark instances (reports/qaoa_benchmark/instances.json)
that scripts/run_ibm_hardware.py sent to the hardware; hardware results are read from
reports/ibm_hardware/*.json, never re-run from the app.
"""

from __future__ import annotations

import glob
import json
import os
import time
from typing import Any

import numpy as np

from qrescue.quantum.qaoa_fast import ising_scale, qaoa_state, qubo_energies
from qrescue.simulation.instances import model_from_dict
from qrescue.simulation.paircover import epoch_qubo, objective

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BENCH = os.path.join(ROOT, "reports", "qaoa_benchmark", "instances.json")
HW_DIR = os.path.join(ROOT, "reports", "ibm_hardware")

# The scaling jobs run the strongest benchmark problem at each size at this depth.
SCALING_DEPTH = 3

# Real-device rows: (key, name suffix, mitigated job?, readout-corrected numbers?)
HW_GROUPS = [
    ("raw", "", False, False),
    ("ro", " + readout fix", False, True),
    ("mit", " + DD + twirling", True, False),
    ("all", " + DD + twirling + readout fix", True, True),
]

DESCRIPTIONS = {
    "oper-4q-1": "1 call, 4 eligible ambulances",
    "oper-6q-5": "2 calls, 6 eligible ambulance–call pairs",
}


def load_hardware_runs() -> list[dict[str, Any]]:
    """Scored hardware result files, real devices first."""
    runs = []
    for path in glob.glob(os.path.join(HW_DIR, "*.json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("status") == "done":
            runs.append(d)
    return sorted(runs, key=lambda d: (d["kind"] != "real", d["backend"]))


def problem_choices(runs: list[dict[str, Any]]) -> list[tuple[str, int]]:
    """(instance, depth) pairs of the first real-device job, in run order."""
    real = min((r for r in runs if r["kind"] == "real"), key=lambda r: r.get("completed_utc", ""), default=None)
    return [(c["id"], c["p"]) for c in real["circuits"]] if real else []


def scaling_curve(runs: list[dict[str, Any]], p: int = SCALING_DEPTH, backend: str = "ibm_fez") -> list[dict[str, Any]]:
    """Per problem size at depth p on one device: noiseless and real P(optimum) as a multiple of guessing among valid plans."""
    by_id: dict[str, list[dict[str, Any]]] = {}
    for r in runs:
        if r["kind"] != "real" or r["backend"] != backend or r.get("mitigation", "none") != "none":
            continue
        for c in r["circuits"]:
            if c["p"] == p:
                by_id.setdefault(c["id"], []).append(c)
    out = []
    for iid, cs in by_id.items():
        c0, guess = cs[0], cs[0]["random_feasible_p_opt"]
        hw = [c["p_opt"] for c in cs]
        out.append({"id": iid, "qubits": c0["qubits"], "two_qubit": c0["isa_2q"], "depth": c0["isa_depth"], "n_runs": len(cs),
                    "guess": guess, "noiseless": c0["ideal_p_opt"], "hw": float(np.mean(hw)), "hw_lo": min(hw), "hw_hi": max(hw),
                    "top_optimal_runs": sum(c["most_frequent_is_optimal"] for c in cs),
                    "noiseless_x": c0["ideal_p_opt"] / guess, "hw_x": float(np.mean(hw)) / guess,
                    "hw_x_lo": min(hw) / guess, "hw_x_hi": max(hw) / guess})
    return sorted(out, key=lambda d: d["qubits"])


def _circuit(run: dict[str, Any], iid: str, p: int) -> dict[str, Any] | None:
    return next((c for c in run["circuits"] if c["id"] == iid and c["p"] == p), None)


def decode(index: int, variables) -> list[tuple[int, int]]:
    """Bitstring index -> (unit, call) pairs; bit k is qubit k (Qiskit order)."""
    return [(u, j) for k, (u, j) in enumerate(variables) if (index >> k) & 1]


def label(pairs) -> str:
    return ", ".join(f"A{u + 1} → C{j + 1}" for u, j in pairs) or "no ambulance sent"


def _nearest_available(model) -> list[tuple[int, int]]:
    """Each call in turn gets the closest free eligible ambulance, ignoring coverage."""
    free, out = set(range(model.n_units)), []
    for j in range(model.n_calls):
        cands = [u for u in free if model.is_eligible(u, j)]
        if cands:
            u = min(cands, key=lambda u: (model.travel[u, j], u))
            out.append((u, j))
            free.discard(u)
    return out


def _bitstring_answer(model, variables, bits: str) -> dict[str, Any]:
    pairs = decode(int(bits.replace(" ", ""), 2), variables)
    cost = objective(model, pairs)
    return {"pairs": pairs, "cost": cost, "valid": np.isfinite(cost)}


def compare(iid: str, p: int, runs: list[dict[str, Any]], shots: int = 4096, seed: int = 7) -> dict[str, Any]:
    """Run the classical methods and the noiseless simulator live; attach stored backend runs."""
    with open(BENCH, encoding="utf-8") as f:
        inst = next(d for d in json.load(f) if d["id"] == iid)
    model = model_from_dict(inst)
    variables, h, J, _, _ = epoch_qubo(model)
    n = len(variables)

    t0 = time.perf_counter()
    greedy = _nearest_available(model)
    greedy_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    energies = qubo_energies(h, J, n)
    best = int(np.argmin(energies))
    exact_s = time.perf_counter() - t0
    opt_mask = np.isclose(energies, energies.min())
    exact_pairs = decode(best, variables)
    exact_cost = objective(model, exact_pairs)

    ref = next((_circuit(r, iid, p) for r in runs if _circuit(r, iid, p)), None)
    t0 = time.perf_counter()
    probs = np.abs(qaoa_state(energies / ising_scale(h, J, n), ref["params"])) ** 2
    probs /= probs.sum()
    samples = np.random.default_rng(seed).choice(len(probs), size=shots, p=probs)
    sim_s = time.perf_counter() - t0
    counts = np.bincount(samples, minlength=len(probs))
    top = int(np.argmax(counts))
    valid_mask = np.array([np.isfinite(objective(model, decode(i, variables))) for i in range(len(probs))])

    rows = [
        {"key": "greedy", "name": "Nearest-available", "kind": "classical", "where": "CPU",
         "pairs": greedy, "cost": objective(model, greedy), "seconds": greedy_s},
        {"key": "exact", "name": "Exact classical", "kind": "classical", "where": "CPU, every option checked",
         "pairs": exact_pairs, "cost": exact_cost, "seconds": exact_s},
        {"key": "sim", "name": "QAOA · noiseless simulator", "kind": "simulator", "where": "CPU, exact maths",
         "seconds": sim_s, "p_opt": float(probs[opt_mask].sum()), "p_valid": float(probs[valid_mask].sum()),
         "two_qubit": None, "depth": None, "shots": shots}
        | _answer(model, variables, format(top, f"0{n}b"), exact_cost),
    ]
    real_runs = [r for r in runs if r["kind"] == "real"]
    # The device of the first job keeps the plain row keys the page reads; other devices get their own rows.
    first = min(real_runs, key=lambda r: r.get("completed_utc", ""), default=None)
    backends = sorted({r["backend"] for r in real_runs}, key=lambda b: b != (first or {}).get("backend"))
    for backend, (key, suffix, mitigated, readout) in ((b, g) for b in backends for g in HW_GROUPS):
        group = []
        for r in real_runs:
            c = _circuit(r, iid, p) if r["backend"] == backend else None
            if not c or (r.get("mitigation", "none") != "none") != mitigated:
                continue
            if readout:
                if "readout_corrected" not in c:
                    continue
                c = c | c["readout_corrected"] | {"p_opt_before_readout": c["p_opt"]}
            group.append((r, c))
        if group:
            row = _hardware_row(key, suffix, group, model, variables, exact_cost)
            if backend != backends[0]:
                row["key"] = f"hw_{backend}_{key}"
            rows.append(row)
    devices = {r["backend"].removeprefix("ibm_") for r in real_runs}
    for r in runs:
        c = _circuit(r, iid, p)
        if r["kind"] != "fake" or not c or r["backend"].removeprefix("fake_") not in devices:
            continue
        rows.append({"key": f"fake_{r['backend']}", "name": f"QAOA · Fake{r['backend'].removeprefix('fake_').title()}",
                     "kind": "fake", "where": f"CPU, IBM {r['backend'].removeprefix('fake_')} noise copy",
                     "p_opt": c["p_opt"], "p_valid": c["p_feasible"], "two_qubit": c["isa_2q"], "depth": c["isa_depth"],
                     "shots": c["shots"], "seconds": None}
                    | _answer(model, variables, c["most_frequent"], exact_cost))
    return {"id": iid, "p": p, "qubits": n, "description": DESCRIPTIONS.get(iid, ""),
            "uniform_p_opt": float(opt_mask.sum() / 2 ** n),
            "uniform_valid_p_opt": float(opt_mask.sum() / valid_mask.sum()),
            "exact_cost": exact_cost, "rows": rows}


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def _hardware_row(key, suffix, group, model, variables, exact_cost) -> dict[str, Any]:
    """One row for several jobs of the same circuit: mean and range over jobs, majority answer."""
    r0, c0 = group[0]
    p_opts = [c["p_opt"] for _, c in group]
    answers = [c["most_frequent"] for _, c in group]
    majority = max(set(answers), key=answers.count)
    timing = [r.get("timing", {}) for r, _ in group]
    queue = [t.get("queue_seconds") for t in timing]
    run = [t.get("run_seconds") for t in timing]
    return ({"key": f"hw_{key}", "name": f"QAOA · {r0['backend']}{suffix}", "kind": "hardware",
             "mitigated": key != "raw", "where": f"Real IBM chip ({r0['backend_qubits']} qubits)",
             "n_runs": len(group), "p_opt": float(np.mean(p_opts)), "p_opt_lo": min(p_opts), "p_opt_hi": max(p_opts),
             "p_valid": _mean([c["p_feasible"] for _, c in group]),
             "p_opt_before_readout": _mean([c.get("p_opt_before_readout") for _, c in group]),
             "p_opt_by_run": [(r.get("completed_utc", ""), c["p_opt"]) for r, c in group],
             "two_qubit": c0["isa_2q"], "depth": c0["isa_depth"], "shots": c0["shots"],
             "optimal_runs": sum(c["most_frequent_is_optimal"] for _, c in group),
             "queue_seconds": _mean(queue), "run_seconds": _mean(run),
             "seconds": _mean([(q or 0) + (s or 0) for q, s in zip(queue, run) if q is not None or s is not None]),
             "chip_seconds": _mean([t.get("circuit_execution_seconds") for t in timing]),
             "job_ids": [r["job_id"] for r, _ in group],
             "completed_utc": max(r.get("completed_utc", "") for r, _ in group)}
            | _answer(model, variables, majority, exact_cost))


def _answer(model, variables, bits: str, exact_cost: float) -> dict[str, Any]:
    a = _bitstring_answer(model, variables, bits)
    return {"pairs": a["pairs"], "cost": a["cost"], "valid": bool(a["valid"]),
            "optimal": bool(a["valid"] and np.isclose(a["cost"], exact_cost))}
