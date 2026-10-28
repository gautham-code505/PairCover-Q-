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
    """(instance, depth) pairs that ran on a real device, in run order."""
    real = next((r for r in runs if r["kind"] == "real"), None)
    return [(c["id"], c["p"]) for c in real["circuits"]] if real else []


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
    for r in runs:
        c = _circuit(r, iid, p)
        if not c:
            continue
        t = r.get("timing", {})
        real = r["kind"] == "real"
        rows.append({"key": f"{r['kind']}_{r['backend']}",
                     "name": f"QAOA · {r['backend']}" if real else f"QAOA · Fake{r['backend'].removeprefix('fake_').title()}",
                     "kind": "hardware" if real else "fake",
                     "where": f"Real IBM chip ({r['backend_qubits']} qubits)" if real
                     else f"CPU, IBM {r['backend'].removeprefix('fake_')} noise copy",
                     "p_opt": c["p_opt"], "p_valid": c["p_feasible"], "two_qubit": c["isa_2q"], "depth": c["isa_depth"],
                     "shots": c["shots"], "job_id": r["job_id"] if real else None,
                     "seconds": (t.get("queue_seconds", 0) + t.get("run_seconds", 0)) if real else None,
                     "queue_seconds": t.get("queue_seconds"), "run_seconds": t.get("run_seconds"),
                     "chip_seconds": t.get("circuit_execution_seconds"), "completed_utc": r.get("completed_utc")}
                    | _answer(model, variables, c["most_frequent"], exact_cost))
    return {"id": iid, "p": p, "qubits": n, "description": DESCRIPTIONS.get(iid, ""),
            "uniform_p_opt": float(opt_mask.sum() / 2 ** n),
            "uniform_valid_p_opt": float(opt_mask.sum() / valid_mask.sum()),
            "exact_cost": exact_cost, "rows": rows}


def _answer(model, variables, bits: str, exact_cost: float) -> dict[str, Any]:
    a = _bitstring_answer(model, variables, bits)
    return {"pairs": a["pairs"], "cost": a["cost"], "valid": bool(a["valid"]),
            "optimal": bool(a["valid"] and np.isclose(a["cost"], exact_cost))}
