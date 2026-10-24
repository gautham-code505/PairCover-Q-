"""
"Create your own emergency": build a dispatch decision from user input and solve it.

The user places calls on the Round 2 synthetic city (src/qrescue/simulation/region.py),
sets their priorities and marks ambulances busy. This module turns that into the same
PairCover-Q objective the rolling simulation uses (src/qrescue/simulation/paircover.py)
and runs the three methods on it. Every result is returned in the schema the dispatch
console already renders (see app/result_adapter.py), so the console can show it unchanged.

Nothing here is real data: the city, its demand and its stations are synthetic.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import replace
from datetime import datetime
from typing import Any, Sequence

import numpy as np

from qrescue.quantum.qaoa_fast import ising_scale, linear_ramp, interp, optimize, qubo_energies
from qrescue.simulation.paircover import (
    build_model, epoch_qubo, model_coverage_loss, objective, solve_exact,
)
from qrescue.simulation.region import PRIORITY_WEIGHTS, default_region

SCENARIO_ID = "custom"
COVER_MINUTES = 12.0      # a unit "covers" a zone it can reach within this time (as in the simulation)
CALLS_PER_HOUR = 4.0      # city-wide demand used to weight coverage (moderate load in the simulation)
TAU = 20.0                # unserved-call cost per unit of priority weight, as in Round 1
DEFAULT_LAMBDA = 5.0      # coverage weight with no significant increase in late arrivals vs closest-idle in the simulation
MAX_CALLS = 4
MAX_QAOA_QUBITS = 12      # 2^12 states keeps the exact simulator fast enough for a click

_COLS = "ABCDEF"


def zone_label(z: int) -> str:
    """Zones form a 6 x 6 grid: columns A-F west to east, rows 1-6 south to north."""
    return f"{_COLS[z % 6]}{z // 6 + 1}"


def zone_area(z: int) -> str:
    region = default_region()
    share = region.demand_share[z]
    hi = np.sort(region.demand_share)
    if share >= hi[-6]:
        return "city centre"
    if share >= np.median(hi):
        return "busy area"
    return "quiet area"


def ambulance_names() -> list[str]:
    return [f"A{i + 1}" for i in range(default_region().n_ambulances)]


def station_of(name: str) -> int:
    return default_region().home_station[ambulance_names().index(name)]


# Ready-made situations. Each is a list of (zone index, priority 1-3) plus busy units.
PRESETS: dict[str, dict[str, Any]] = {
    # Nearest-available sends the town's only ambulance (A4) to B4 and leaves the town uncovered;
    # the cheapest plan sends A1 from the two-ambulance city station instead.
    "Town keeps its only ambulance": {"calls": [(16, 2), (19, 3)], "busy": []},
    "Rush hour: three calls downtown": {"calls": [(15, 1), (20, 2), (21, 3)], "busy": []},
    "Short-staffed night": {"calls": [(16, 1), (19, 3)], "busy": ["A2", "A6"]},
    "Far corner emergency": {"calls": [(5, 1), (27, 2)], "busy": []},
}


def build_scenario(calls: Sequence[tuple[int, int]], busy: Sequence[str] = (), lam: float = DEFAULT_LAMBDA) -> dict[str, Any]:
    """Scenario dict in the console's schema, plus the model needed to solve it.

    calls: (zone index, priority 1-3) per call, in the order the user added them.
    busy: ambulance names that are unavailable.
    """
    if not calls:
        raise ValueError("Add at least one emergency call.")
    if len(calls) > MAX_CALLS:
        raise ValueError(f"At most {MAX_CALLS} calls at once, so every method finishes quickly.")
    region = default_region()
    names = ambulance_names()
    free = [i for i, n in enumerate(names) if n not in set(busy)]
    if not free:
        raise ValueError("Every ambulance is marked busy; free at least one.")
    unit_names = [names[i] for i in free]
    call_names = [f"C{k + 1}" for k in range(len(calls))]
    base = region.base_xy[free]
    call_xy = np.array([region.zones[z] for z, _ in calls])
    travel = np.round(region.travel(base[:, None, :], call_xy[None, :, :]), 1)
    weight = np.array([PRIORITY_WEIGHTS[p] for _, p in calls], dtype=float)
    covers = region.travel(base[:, None, :], region.zones[None, :, :]) <= COVER_MINUTES
    zone_rate = region.demand_share * CALLS_PER_HOUR
    model = build_model(travel, weight, np.zeros(len(calls)), covers, zone_rate, lam, TAU, max_travel=COVER_MINUTES)

    eligible = {(unit_names[u], call_names[j]): float(travel[u, j])
                for u in range(len(free)) for j in range(len(calls)) if model.is_eligible(u, j)}
    single = {unit_names[u]: round(lam * float(model.c[u]), 2) for u in range(len(free)) if model.c[u] > 0}
    pairs = [[unit_names[a], unit_names[b], round(lam * float(v), 2)] for (a, b), v in sorted(model.g.items())]
    positions = {unit_names[u]: [float(base[u, 0]), float(base[u, 1])] for u in range(len(free))}
    for j, c in enumerate(call_names):
        positions[c] = [float(call_xy[j, 0]), float(call_xy[j, 1])]

    # Each distinct situation gets its own id, so runs from an earlier situation are never shown for this one.
    key = repr((list(calls), sorted(busy), round(float(lam), 3)))
    scen = {
        "scenario_id": f"{SCENARIO_ID}-{abs(hash(key)) % 10**8:08d}",
        "name": "Your emergency (synthetic city)",
        "description": "Calls placed by you on the synthetic Round 2 city. Travel times come from straight-line "
                       "distance with a road detour factor; nothing is real data.",
        "ambulances": unit_names,
        "calls": call_names,
        "call_zones": {c: zone_label(z) for c, (z, _) in zip(call_names, calls)},
        "priority_weights": {c: float(w) for c, w in zip(call_names, weight)},
        "travel_times": eligible,
        "unserved_time": TAU,
        "lambda_coverage": lam,
        "coverage": {"single": single, "pairs": pairs},
        "positions": positions,
        "variables": list(eligible),
        "note": f"Units only count as options if they arrive within {COVER_MINUTES:g} minutes or are the nearest unit.",
        "_model": model,
    }
    scen["landscape"] = _landscape(scen)
    return scen


def _to_names(scen, assignment) -> list[tuple[str, str]]:
    return [(scen["ambulances"][u], scen["calls"][j]) for u, j in assignment]


def _costs(scen, assignment) -> tuple[float, float, float]:
    # The cost formula itself does not depend on which pairs count as options.
    m = replace(scen["_model"], eligible=None)
    total = objective(m, assignment)
    cov = m.lam * model_coverage_loss(m, {u for u, _ in assignment})
    # Shown to one decimal; the total is the sum of the shown parts so the numbers on screen add up.
    resp_r, cov_r = round(total - cov, 1), round(cov, 1)
    return resp_r, cov_r, round(resp_r + cov_r, 1)


def _show_pairs(scen, assignment) -> None:
    """Make sure every pair a method used has a travel time on screen (the map, the cards)."""
    m = scen["_model"]
    for u, j in assignment:
        scen["travel_times"].setdefault((scen["ambulances"][u], scen["calls"][j]), float(m.travel[u, j]))


def _required_size(scen) -> int:
    """Calls that must be served: as many as the eligible pairs allow (no call waits beside an idle unit)."""
    best, _ = solve_exact(scen["_model"])
    return len(best)


def _landscape(scen) -> dict[str, Any]:
    """Every valid plan that serves the required number of calls, cheapest first."""
    m = scen["_model"]
    k = _required_size(scen)
    rows = []
    for calls in itertools.combinations(range(m.n_calls), k):
        for units in itertools.permutations(range(m.n_units), k):
            asg = list(zip(units, calls))
            if not all(m.is_eligible(u, j) for u, j in asg):
                continue
            resp, cov, total = _costs(scen, asg)
            rows.append({"assignments": _to_names(scen, asg), "resp": resp, "cov": cov, "obj": total, "qubo": None})
    rows.sort(key=lambda r: (r["obj"], r["resp"]))
    n_vars = len(scen["variables"])
    return {"total_states": 2 ** n_vars, "feasible_count": len(rows), "feasible": rows,
            "feasibility_rate": len(rows) / 2 ** n_vars if n_vars else 0.0,
            "optimum_prob": 1 / 2 ** n_vars if n_vars else 0.0}


def _result(scen, method, assignment, t0, experiment) -> dict[str, Any]:
    resp, cov, total = _costs(scen, assignment)
    names = _to_names(scen, assignment)
    served = {c for _, c in names}
    experiment.setdefault("run_id", f"{method.split()[0].lower()}_{scen['scenario_id']}")  # deterministic per situation
    experiment.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return {
        "scenario_id": scen["scenario_id"], "method": method, "assignments": names,
        "unserved_calls": [c for c in scen["calls"] if c not in served],
        "weighted_response_cost": resp, "coverage_penalty": cov, "objective_value": total,
        "feasible": True, "runtime_seconds": time.perf_counter() - t0, "experiment": experiment,
    }


def run_custom_greedy(scen) -> dict[str, Any]:
    """Most urgent call first (then the order added): the nearest free unit among that call's
    options; if none of its options is free, the nearest free unit of all."""
    t0 = time.perf_counter()
    m = scen["_model"]
    free, asg = set(range(m.n_units)), []
    for j in sorted(range(m.n_calls), key=lambda j: -m.weight[j]):
        if free:
            pool = [u for u in free if m.is_eligible(u, j)] or list(free)
            u = min(pool, key=lambda u: (m.travel[u, j], u))
            asg.append((u, j))
            free.discard(u)
    _show_pairs(scen, asg)
    return _result(scen, "Greedy (Priority Nearest)", asg, t0,
                   {"kind": "classical_heuristic", "algorithm": "greedy_priority_nearest"})


def run_custom_exact(scen) -> dict[str, Any]:
    t0 = time.perf_counter()
    best, _ = solve_exact(scen["_model"])
    _show_pairs(scen, best)
    return _result(scen, "Exact Classical Solver", best, t0,
                   {"kind": "classical_exact", "algorithm": "exhaustive_enumeration",
                    "total_states_evaluated": scen["landscape"]["feasible_count"]})


def qaoa_available(scen) -> tuple[bool, str]:
    n = len(scen["variables"])
    if n < 2:
        return False, "Only one possible pairing, so there is nothing for QAOA to choose."
    if n > MAX_QAOA_QUBITS:
        return False, f"This situation needs {n} qubits; the in-browser simulator is limited to {MAX_QAOA_QUBITS}. Remove a call or mark a unit busy."
    return True, f"{n} qubits"


def run_custom_qaoa(scen, p: int = 1, seed: int = 10, shots: int = 1000) -> dict[str, Any]:
    """QAOA on the epoch QUBO with the exact NumPy simulator, then `shots` samples.

    Reports the cheapest valid sample; if no sample is valid, no plan is returned.
    """
    ok, why = qaoa_available(scen)
    if not ok:
        raise ValueError(why)
    t0 = time.perf_counter()
    m = scen["_model"]
    variables, h, J, _, penalty = epoch_qubo(m)
    n = len(variables)
    energies = qubo_energies(h, J, n)
    scale = ising_scale(h, J, n)
    params, r = None, None
    for depth in range(1, p + 1):
        r = optimize(energies, scale, depth, linear_ramp(depth) if params is None else interp(params), maxiter=200)
        params = r["params"]
    probs = r["probs"] / r["probs"].sum()
    rng = np.random.default_rng(seed)
    samples = rng.choice(2 ** n, size=shots, p=probs)
    exact_plan, exact_obj = solve_exact(m)   # unrounded, so equality tests below are exact
    k_req = len(exact_plan)

    def plan(idx: int):
        return [variables[k] for k in range(n) if (idx >> k) & 1]

    def valid(asg) -> bool:
        return (len(asg) == k_req and len({u for u, _ in asg}) == len(asg) and len({j for _, j in asg}) == len(asg))

    counts: dict[int, int] = {}
    for s in samples:
        counts[int(s)] = counts.get(int(s), 0) + 1
    best, best_cost, best_idx = None, float("inf"), None
    valid_shots = opt_hits = 0
    for idx, c in counts.items():
        asg = plan(idx)
        if not valid(asg):
            continue
        valid_shots += c
        cost = objective(m, asg)
        if abs(cost - exact_obj) < 1e-6:
            opt_hits += c
        if cost < best_cost - 1e-9:
            best, best_cost, best_idx = asg, cost, idx
    is_opt = np.array([valid(plan(i)) and abs(objective(m, plan(i)) - exact_obj) < 1e-6 for i in range(2 ** n)])
    is_valid = np.array([valid(plan(i)) for i in range(2 ** n)])
    exp = {
        "kind": "qaoa_sampled", "p": p, "depth_p": p, "seed": seed, "shots": shots,
        "backend": "Exact NumPy statevector (noiseless)", "optimizer": "COBYLA (rhobeg=0.5)",
        "nfev": r["nfev"], "maxiter": 200, "success": r["success"],
        "message": "converged" if r["success"] else "COBYLA stopped at its iteration limit",
        "qubits": n, "penalty": penalty,
        "final_qubo_energy": r["expectation"], "energy_history": [float(v) for v in r["trace"]],
        "feasibility_rate": valid_shots / shots, "sv_feas_rate": float(probs[is_valid].sum()),
        "sampled_opt_prob": opt_hits / shots, "sv_opt_prob": float(probs[is_opt].sum()),
        "optimum_hits": opt_hits,
        "best_sample_hits": counts.get(best_idx, 0) if best is not None else 0,
        "random_feasibility_rate": float(is_valid.mean()), "random_opt_prob": float(is_opt.mean()),
    }
    method = f"QAOA (p={p}, Seed={seed})"
    if best is None:
        return {"scenario_id": scen["scenario_id"], "method": method, "assignments": [], "unserved_calls": list(scen["calls"]),
                "weighted_response_cost": None, "coverage_penalty": None, "objective_value": None, "feasible": False,
                "runtime_seconds": time.perf_counter() - t0,
                "experiment": exp | {"run_id": f"qaoa_{scen['scenario_id']}_p{p}_s{seed}_sh{shots}",
                                     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
    return _result(scen, method, best, t0, exp | {"run_id": f"qaoa_{scen['scenario_id']}_p{p}_s{seed}_sh{shots}"})


def run_custom(method: str, scen, params: dict[str, Any] | None = None) -> dict[str, Any]:
    m = method.lower()
    if "nearest" in m or "greedy" in m:
        return run_custom_greedy(scen)
    if "exact" in m:
        return run_custom_exact(scen)
    if "qaoa" in m:
        params = params or {}
        return run_custom_qaoa(scen, p=int(params.get("p", 1)), seed=int(params.get("seed", 10)),
                               shots=int(params.get("shots", 1000)))
    raise ValueError(f"Unknown method: {method}")
