"""
PairCover-Q Result Adapter.

Adapts outputs from the existing backend (qrescue) to the agreed UI
result schema (docs/ui_ux_spec.md §5 and app/ui_components.py).

Does not implement another QUBO, QAOA, or assignment algorithm;
delegates strictly to existing modules in src/qrescue.

Strictly separates:
- weighted_response_cost (travel times + unserved call penalties)
- coverage_penalty (residual-coverage loss)
- objective_value (sum of above; only finite/valid on feasible solutions)
- qubo_energy (penalized Hamiltonian energy including constraint penalties)
- qaoa_expected_energy (statevector expectation)
- runtime_seconds (measured wall-clock execution time)
- feasibility_rate (fraction of samples that satisfy hard constraints)
- exact_optimum_prob (fraction of samples hitting the exact ground state)
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Mapping, Sequence
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

from qrescue.optimization.scenario import (
    VARIABLES as SCENARIO1_VARS,
    PRIORITY_WEIGHTS as SCENARIO1_WEIGHTS,
    UNSERVED_TIME as SCENARIO1_UNSERVED_TIME,
    TRAVEL_TIMES as SCENARIO1_TRAVEL_TIMES,
    COVERAGE_PARAMS as SCENARIO1_COVERAGE_PARAMS,
    LAMBDA_COVERAGE as SCENARIO1_LAMBDA,
    EXPECTED_OFFSET as SCENARIO1_OFFSET,
    generate_qubo_scenario1
)
from qrescue.optimization.scenario2 import (
    VARIABLES_2 as SCENARIO2_VARS,
    PRIORITY_WEIGHTS_2 as SCENARIO2_WEIGHTS,
    UNSERVED_TIME_2 as SCENARIO2_UNSERVED_TIME,
    TRAVEL_TIMES_2 as SCENARIO2_TRAVEL_TIMES,
    LAMBDA_COVERAGE_2 as SCENARIO2_LAMBDA,
    SHARED_DEMAND_2 as SCENARIO2_SHARED_DEMAND,
    generate_qubo_scenario2,
    calc_raw_objective as calc_raw_objective_scenario2
)
from qrescue.optimization.brute_force import generate_all_bitstrings
from qrescue.optimization.qubo import calculate_qubo_energy
from qrescue.quantum.ising import qubo_to_ising
from qrescue.validation.validator import (
    is_feasible,
    decode_assignment,
    decode_qiskit_bitstring
)

# --------------------------------------------------------------------------- #
# Scenario Definition Exporters
# --------------------------------------------------------------------------- #

def get_scenario_metadata(scenario_id: str = "scenario_2") -> dict[str, Any]:
    """
    Returns base scenario metadata without computed landscape to avoid recursion.
    """
    if scenario_id == "scenario_1":
        ambulances = ["A1", "A2"]
        calls = ["C1", "C2", "C3"]
        return {
            "scenario_id": "scenario_1",
            "name": "Scenario 1: 5-Qubit Mathematical Validation",
            "description": (
                "Synthetic benchmark scenario (2 ambulances, 3 calls). "
                "A2 is ineligible for C1. Used to verify baseline linear savings, "
                "coupling penalties, and QUBO-to-Ising mapping."
            ),
            "ambulances": ambulances,
            "calls": calls,
            "priority_weights": dict(SCENARIO1_WEIGHTS),
            "travel_times": dict(SCENARIO1_TRAVEL_TIMES),
            "variables": list(SCENARIO1_VARS),
            "unserved_time": SCENARIO1_UNSERVED_TIME,
            "lambda_coverage": SCENARIO1_LAMBDA,
            "coverage_params": dict(SCENARIO1_COVERAGE_PARAMS),
            "qubo_offset": SCENARIO1_OFFSET,
            "positions": {
                "A1": [0.0, 0.0],
                "C2": [8.0, 0.0],
                "A2": [6.3095, 3.6252],
                "C3": [-2.5029, 5.453],
                "C1": [1.7101, -4.6985]
            },
            "coverage": {
                "single": {"A1": 5.0, "A2": 4.0},
                "pairs": [["A1", "A2", 10.0]]
            }
        }
    else:
        # Default to Scenario 2 (PairCover-Q demonstration)
        ambulances = ["A1", "A2", "A3"]
        calls = ["C2", "C3"]
        return {
            "scenario_id": "scenario_2",
            "name": "Scenario 2: PairCover-Q Demonstration (6 Qubits)",
            "description": (
                "Synthetic coverage-aware scenario (3 ambulances, 2 calls). "
                "Ambulance A4 is pre-assigned to critical call C1. Ambulances A1 and A2 "
                "mutually cover a shared sector; dispatching both incurs a 10-point coverage penalty."
            ),
            "ambulances": ambulances,
            "calls": calls,
            "priority_weights": dict(SCENARIO2_WEIGHTS),
            "travel_times": dict(SCENARIO2_TRAVEL_TIMES),
            "variables": list(SCENARIO2_VARS),
            "unserved_time": SCENARIO2_UNSERVED_TIME,
            "lambda_coverage": SCENARIO2_LAMBDA,
            "shared_demand": SCENARIO2_SHARED_DEMAND,
            "qubo_offset": 60,
            "positions": {
                "C2": [0.0, 0.0],
                "C3": [8.0, 0.0],
                "A1": [2.75, 2.9047],
                "A2": [4.5625, 2.0454],
                "A3": [11.4375, -3.6309]
            },
            "coverage": {
                "single": {},
                "pairs": [["A1", "A2", 10.0]]
            }
        }

def get_landscape(scenario_id: str = "scenario_2") -> dict[str, Any]:
    """
    Exhaustively evaluates all 2^n states to find all feasible configurations,
    their raw dispatch metrics (response cost, coverage penalty, total objective),
    and their QUBO energies.
    """
    base = get_scenario_metadata(scenario_id)
    vars_list = base["variables"]
    n_vars = len(vars_list)
    all_bitstrings = generate_all_bitstrings(n_vars)
    
    if scenario_id == "scenario_1":
        h, J = generate_qubo_scenario1()
    else:
        h, J = generate_qubo_scenario2()
        
    feasible_items = []
    for b in all_bitstrings:
        if scenario_id == "scenario_1":
            resp, cov, obj, feas = calculate_scenario1_raw_metrics(b)
        else:
            resp, cov, obj, feas = calculate_scenario2_raw_metrics(b)
            
        if feas and obj is not None:
            qe = calculate_qubo_energy(b, h, J)
            asgs = decode_assignment(b, vars_list)
            x_str = "".join(str(bit) for bit in reversed(b))
            feasible_items.append({
                "bitstring": x_str,
                "x_raw": list(b),
                "assignments": asgs,
                "resp": float(resp),
                "cov": float(cov),
                "obj": float(obj),
                "qubo": float(qe)
            })
            
    feasible_items.sort(key=lambda item: (item["obj"], item["resp"]))
    total_states = len(all_bitstrings)
    feas_count = len(feasible_items)
    
    return {
        "total_states": total_states,
        "feasible_count": feas_count,
        "feasibility_rate": feas_count / total_states,
        "optimum_prob": 1.0 / total_states,
        "feasible": feasible_items
    }

def get_scenario(scenario_id: str = "scenario_2") -> dict[str, Any]:
    """
    Returns scenario metadata matching the UI specification, including
    solved layout coordinates, coverage structure, and precomputed landscape.
    """
    scen = get_scenario_metadata(scenario_id)
    scen["layout"] = scen["positions"]
    scen["landscape"] = get_landscape(scenario_id)
    return scen

def get_optimal_measurement_key(scenario_id: str = "scenario_2") -> str:
    """
    Programmatically derives the target bitstring key in Qiskit little-endian
    format corresponding to the exact classical optimum using the declared variable order.
    """
    scen = get_scenario_metadata(scenario_id)
    vars_list = scen["variables"]
    exact_res = run_exact(scenario_id)
    target_x = [0] * len(vars_list)
    for a in exact_res["assignments"]:
        if a in vars_list:
            target_x[vars_list.index(a)] = 1
    return "".join(str(b) for b in reversed(target_x))

# --------------------------------------------------------------------------- #
# Raw Metric Calculation Functions
# --------------------------------------------------------------------------- #

def calculate_scenario1_raw_metrics(x: Sequence[int]) -> tuple[float | None, float | None, float | None, bool]:
    """
    Calculates weighted response cost, coverage penalty, and total objective for Scenario 1.
    Returns (weighted_response_cost, coverage_penalty, total_objective, feasible).
    """
    if not is_feasible(x, SCENARIO1_VARS):
        return None, None, None, False
        
    assignments = decode_assignment(x, SCENARIO1_VARS)
    assigned_calls = {c for a, c in assignments}
    dispatched_ambs = {a for a, c in assignments}
    
    # Weighted response cost: travel time + unserved calls
    resp_cost = 0.0
    for a, c in assignments:
        resp_cost += SCENARIO1_WEIGHTS[c] * SCENARIO1_TRAVEL_TIMES[(a, c)]
    for c in ["C1", "C2", "C3"]:
        if c not in assigned_calls:
            resp_cost += SCENARIO1_WEIGHTS[c] * SCENARIO1_UNSERVED_TIME
            
    # Coverage penalty
    cov_penalty = 0.0
    for a in dispatched_ambs:
        cov_penalty += SCENARIO1_LAMBDA * SCENARIO1_COVERAGE_PARAMS.get(a, 0.0)
    if "A1" in dispatched_ambs and "A2" in dispatched_ambs:
        cov_penalty += SCENARIO1_LAMBDA * SCENARIO1_COVERAGE_PARAMS.get(("A1", "A2"), 1.0)
        
    total_obj = resp_cost + cov_penalty
    return resp_cost, cov_penalty, total_obj, True

def calculate_scenario2_raw_metrics(x: Sequence[int]) -> tuple[float | None, float | None, float | None, bool]:
    """
    Calculates weighted response cost, coverage penalty, and total objective for Scenario 2.
    Returns (weighted_response_cost, coverage_penalty, total_objective, feasible).
    """
    if not is_feasible(x, SCENARIO2_VARS):
        return None, None, None, False
        
    assignments = decode_assignment(x, SCENARIO2_VARS)
    assigned_calls = {c for a, c in assignments}
    dispatched_ambs = {a for a, c in assignments}
    
    # Weighted response cost: travel time + unserved calls
    resp_cost = 0.0
    for a, c in assignments:
        resp_cost += SCENARIO2_WEIGHTS[c] * SCENARIO2_TRAVEL_TIMES[(a, c)]
    for c in ["C2", "C3"]:
        if c not in assigned_calls:
            resp_cost += SCENARIO2_WEIGHTS[c] * SCENARIO2_UNSERVED_TIME
            
    # Coverage penalty: 10 if both A1 and A2 are dispatched
    cov_penalty = 0.0
    if "A1" in dispatched_ambs and "A2" in dispatched_ambs:
        cov_penalty = float(int(SCENARIO2_LAMBDA * SCENARIO2_SHARED_DEMAND))
        
    total_obj = resp_cost + cov_penalty
    return resp_cost, cov_penalty, total_obj, True

# --------------------------------------------------------------------------- #
# Dispatch Method Runners
# --------------------------------------------------------------------------- #

def run_greedy(scenario_id: str = "scenario_2") -> dict[str, Any]:
    """
    Executes deterministic greedy nearest-available dispatch by call priority.
    """
    t0 = time.perf_counter()
    # Metadata only: get_scenario() also enumerates every state, which would be timed as "greedy".
    scen = get_scenario_metadata(scenario_id)
    vars_list = scen["variables"]
    tt = scen["travel_times"]
    pw = scen["priority_weights"]
    calls_sorted = sorted(scen["calls"], key=lambda c: pw.get(c, 0), reverse=True)
    
    assigned_ambs = set()
    assignments = []
    x = [0] * len(vars_list)
    
    for c in calls_sorted:
        # Find eligible ambulances not yet assigned
        eligible = []
        for a in scen["ambulances"]:
            if a not in assigned_ambs and (a, c) in tt:
                eligible.append((a, tt[(a, c)]))
        if eligible:
            # Pick ambulance with minimum travel time
            eligible.sort(key=lambda item: item[1])
            best_amb, best_t = eligible[0]
            assigned_ambs.add(best_amb)
            assignments.append((best_amb, c))
            # Mark bit in x
            idx = vars_list.index((best_amb, c))
            x[idx] = 1
            
    runtime = time.perf_counter() - t0
    
    # Calculate separate metrics
    if scenario_id == "scenario_1":
        resp, cov, total, feas = calculate_scenario1_raw_metrics(x)
        h, J = generate_qubo_scenario1()
    else:
        resp, cov, total, feas = calculate_scenario2_raw_metrics(x)
        h, J = generate_qubo_scenario2()
        
    qubo_e = calculate_qubo_energy(x, h, J)
    served_calls = {c for a, c in assignments}
    unserved = [c for c in scen["calls"] if c not in served_calls]
    
    return {
        "scenario_id": scenario_id,
        "method": "Greedy (Priority Nearest)",
        "assignments": assignments,
        "unserved_calls": unserved,
        "weighted_response_cost": resp,
        "coverage_penalty": cov,
        "objective_value": total,
        "feasible": feas,
        "runtime_seconds": runtime,
        "experiment": {
            "kind": "classical_heuristic",
            "run_id": f"greedy_{scenario_id}_{int(t0*1000)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "qubo_energy": qubo_e,
            "best_cost": total,
            "bitstring": "".join(str(b) for b in x),
            "algorithm": "greedy_priority_nearest",
            "notes": "Greedy heuristic assigning nearest available ambulance in descending call priority order."
        }
    }

def run_exact(scenario_id: str = "scenario_2") -> dict[str, Any]:
    """
    Executes exhaustive classical enumeration finding the exact global optimum.
    """
    t0 = time.perf_counter()
    scen = get_scenario_metadata(scenario_id)
    vars_list = scen["variables"]
    n_vars = len(vars_list)
    all_bitstrings = generate_all_bitstrings(n_vars)

    best_obj = float('inf')
    best_x = None
    best_resp = None
    best_cov = None
    
    for b in all_bitstrings:
        if scenario_id == "scenario_1":
            resp, cov, obj, feas = calculate_scenario1_raw_metrics(b)
        else:
            resp, cov, obj, feas = calculate_scenario2_raw_metrics(b)
            
        if feas and obj is not None and obj < best_obj:
            best_obj = obj
            best_x = b
            best_resp = resp
            best_cov = cov
            
    runtime = time.perf_counter() - t0
    
    assignments = decode_assignment(best_x, vars_list) if best_x else []
    served_calls = {c for a, c in assignments}
    unserved = [c for c in scen["calls"] if c not in served_calls]
    
    if scenario_id == "scenario_1":
        h, J = generate_qubo_scenario1()
    else:
        h, J = generate_qubo_scenario2()
    qubo_e = calculate_qubo_energy(best_x, h, J) if best_x else None
    
    return {
        "scenario_id": scenario_id,
        "method": "Exact Classical Solver",
        "assignments": assignments,
        "unserved_calls": unserved,
        "weighted_response_cost": best_resp,
        "coverage_penalty": best_cov,
        "objective_value": best_obj,
        "feasible": True,
        "runtime_seconds": runtime,
        "experiment": {
            "kind": "classical_exact",
            "run_id": f"exact_{scenario_id}_{int(t0*1000)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "qubo_energy": qubo_e,
            "best_cost": best_obj,
            "bitstring": "".join(str(b) for b in best_x) if best_x else "—",
            "total_states_evaluated": len(all_bitstrings),
            "algorithm": "exhaustive_enumeration",
            "notes": "Global ground truth obtained by exhaustive classical enumeration."
        }
    }

def run_qaoa(
    scenario_id: str = "scenario_2",
    p: int = 1,
    seed: int = 10,
    maxiter: int = 100,
    shots: int = 1000
) -> dict[str, Any]:
    """
    Executes the validated QAOA simulation (StatevectorEstimator + COBYLA).
    Tracks convergence energy history and constructs measurement count distribution.
    """
    t0 = time.perf_counter()
    scen = get_scenario(scenario_id)
    vars_list = scen["variables"]
    n_vars = len(vars_list)
    
    # 1. Generate QUBO and Ising Hamiltonian
    if scenario_id == "scenario_1":
        h, J = generate_qubo_scenario1()
        h_Z, J_Z, offset = qubo_to_ising(h, J, n_vars)
        offset_surrogate = SCENARIO1_OFFSET
    else:
        h, J = generate_qubo_scenario2()
        h_Z, J_Z, offset = qubo_to_ising(h, J, n_vars)
        offset_surrogate = 60
        
    paulis = []
    coeffs = []
    for i in range(n_vars):
        if abs(h_Z[i]) > 1e-9:
            p_str = ['I'] * n_vars
            p_str[i] = 'Z'
            paulis.append("".join(reversed(p_str)))
            coeffs.append(h_Z[i])
    for (i, j), weight in J_Z.items():
        if abs(weight) > 1e-9:
            p_str = ['I'] * n_vars
            p_str[i] = 'Z'
            p_str[j] = 'Z'
            paulis.append("".join(reversed(p_str)))
            coeffs.append(weight)
            
    hamiltonian_orig = SparsePauliOp(paulis, coeffs)
    scale = float(max(abs(c) for c in coeffs)) if coeffs else 1.0
    hamiltonian_scaled = SparsePauliOp(paulis, [c / scale for c in coeffs])
    
    # 2. Build QAOA Ansatz
    ansatz = QAOAAnsatz(hamiltonian_scaled, reps=p)
    
    # 3. Optimize parameters while recording convergence history
    estimator = StatevectorEstimator()
    energy_history = []
    
    def cost_func(params):
        pub = (ansatz, hamiltonian_orig, params)
        job = estimator.run([pub])
        ev = float(job.result()[0].data.evs)
        total_energy = ev + offset
        energy_history.append(total_energy)
        return total_energy
        
    np.random.seed(seed)
    initial_betas = np.random.uniform(0, np.pi, p)
    initial_gammas = np.random.uniform(0, 2 * np.pi, p)
    initial_point = np.concatenate([initial_betas, initial_gammas])
    
    opt_result = minimize(
        cost_func,
        initial_point,
        method='COBYLA',
        options={'maxiter': maxiter, 'rhobeg': 0.5}
    )
    
    # 4. Statevector theoretical limit
    bound_circ = ansatz.assign_parameters(opt_result.x)
    sv = Statevector(bound_circ)
    probs_dict = sv.probabilities_dict()
    
    # 5. Empirical sampling
    bound_circ_meas = bound_circ.copy()
    bound_circ_meas.measure_all()
    sampler = StatevectorSampler(seed=seed)
    pub = (bound_circ_meas,)
    job = sampler.run([pub], shots=shots)
    counts = job.result()[0].data.meas.get_counts()
    
    # 6. Analyze samples
    feasible_bitstrings_map = {}
    feasible_count = 0
    best_feasible_obj = float('inf')
    best_feasible_x = None
    best_feasible_resp = None
    best_feasible_cov = None
    
    most_frequent_bitstr = None
    max_count = -1
    
    for bitstr, count in counts.items():
        if count > max_count:
            max_count = count
            most_frequent_bitstr = bitstr
            
        x_dec, _ = decode_qiskit_bitstring(bitstr, vars_list)
        feas = is_feasible(x_dec, vars_list)
        feasible_bitstrings_map[bitstr] = feas
        
        if feas:
            feasible_count += count
            if scenario_id == "scenario_1":
                resp, cov, obj, _ = calculate_scenario1_raw_metrics(x_dec)
            else:
                resp, cov, obj, _ = calculate_scenario2_raw_metrics(x_dec)
                
            if obj is not None and obj < best_feasible_obj:
                best_feasible_obj = obj
                best_feasible_x = x_dec
                best_feasible_resp = resp
                best_feasible_cov = cov
                
    runtime = time.perf_counter() - t0
    feasibility_rate = feasible_count / shots
    
    # Find exact ground state for comparison
    exact_res = run_exact(scenario_id)
    exact_x = [vars_list.index(a) if a in vars_list else None for a in exact_res["assignments"]]
    # Rebuild exact bitstring
    target_x = [0] * n_vars
    for a in exact_res["assignments"]:
        if a in vars_list:
            target_x[vars_list.index(a)] = 1
    target_key = get_optimal_measurement_key(scenario_id)
    
    empirical_opt_prob = counts.get(target_key, 0) / shots
    sv_opt_prob = probs_dict.get(target_key, 0.0)
    
    # Decide which assignment to present:
    # Present the best feasible sample found; if none feasible, present no assignment
    if best_feasible_x is not None:
        selected_x = best_feasible_x
        selected_feasible = True
        selected_resp = best_feasible_resp
        selected_cov = best_feasible_cov
        selected_obj = best_feasible_obj
        best_bitstr_repr = "".join(str(b) for b in reversed(selected_x))
        assignments = decode_assignment(selected_x, vars_list)
        served_calls = {c for a, c in assignments}
        unserved = [c for c in scen["calls"] if c not in served_calls]
    else:
        # No feasible samples found: do not present infeasible state as a dispatch plan
        selected_x = None
        selected_feasible = False
        selected_resp = None
        selected_cov = None
        selected_obj = None  # Never label penalty-inclusive energy as raw objective!
        best_bitstr_repr = most_frequent_bitstr
        assignments = []
        unserved = list(scen["calls"])
    
    sample_rows = []
    sampled_total_energy = 0.0
    for bitstr, cnt in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        x_d, _ = decode_qiskit_bitstring(bitstr, vars_list)
        feas_b = feasible_bitstrings_map.get(bitstr, False)
        qe = calculate_qubo_energy(x_d, h, J)
        sampled_total_energy += cnt * qe
        asgs = decode_assignment(x_d, vars_list) if feas_b else []
        if feas_b:
            if scenario_id == "scenario_1":
                _, _, raw_o, _ = calculate_scenario1_raw_metrics(x_d)
            else:
                _, _, raw_o, _ = calculate_scenario2_raw_metrics(x_d)
        else:
            raw_o = None
        sample_rows.append({
            "bitstring": bitstr,
            "count": int(cnt),
            "feasible": bool(feas_b),
            "assignments": asgs,
            "qubo_energy": float(qe),
            "raw_objective": float(raw_o) if raw_o is not None else None
        })
    sampled_mean_e = sampled_total_energy / shots
    # Exact statevector feasibility: sum over every basis state, not only the ones that were sampled.
    sv_feas_rate = sum(
        prob for b, prob in probs_dict.items()
        if is_feasible(decode_qiskit_bitstring(b, vars_list)[0], vars_list)
    )

    experiment_payload = {
        "kind": "qaoa_sampled",
        "p": p,
        "depth_p": p,
        "seed": seed,
        "run_id": f"qaoa_{scenario_id}_p{p}_s{seed}_{int(t0*1000)}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "optimizer": "COBYLA (rhobeg=0.5)",
        "evaluations_nfev": int(opt_result.nfev),
        "nfev": int(opt_result.nfev),
        "maxiter": maxiter,
        "success": bool(opt_result.success),
        "optimizer_success": bool(opt_result.success),
        "message": str(opt_result.message),
        "shots": shots,
        "backend": "Statevector (noiseless reference)",
        "scale": float(scale),
        "hamiltonian_scale": scale,
        "initial_params": [float(v) for v in initial_point],
        "final_params": [float(v) for v in opt_result.x],
        "initial_qubo_energy": float(energy_history[0]) if energy_history else None,
        "final_qubo_energy": float(opt_result.fun),
        "qaoa_expected_qubo_energy": float(opt_result.fun),
        "final_surrogate_objective": float(opt_result.fun + offset_surrogate),
        "penalized_surrogate_objective": float(opt_result.fun + offset_surrogate),
        "sampled_mean_qubo_energy": float(sampled_mean_e),
        "sampled_mean_surrogate_objective": float(sampled_mean_e + offset_surrogate),
        "sampled_feas_rate": float(feasibility_rate),
        "feasibility_rate": float(feasibility_rate),
        "sv_feas_rate": float(sv_feas_rate),
        "sampled_opt_prob": float(empirical_opt_prob),
        "exact_optimum_sample_prob": float(empirical_opt_prob),
        "sv_opt_prob": float(sv_opt_prob),
        "exact_optimum_sv_prob": float(sv_opt_prob),
        "optimum_hits": int(counts.get(target_key, 0)),
        "best_sample_hits": int(counts.get(best_bitstr_repr, 0)) if selected_feasible else 0,
        "best_cost": selected_obj,
        "bitstring_order": "qiskit_little_endian",
        "optimal_bitstring": target_key,
        "baselines": [
            {
                "label": f"Uniform Random ({scen['landscape']['total_states']} states)",
                "feasibility_rate": scen["landscape"]["feasibility_rate"],
                "optimum_probability": scen["landscape"]["optimum_prob"]
            }
        ],
        "circuit": {
            "qubits": n_vars,
            "depth": int(bound_circ.depth()),
            "ops": dict(bound_circ.count_ops()),
            "zz_terms": len(J_Z),
            "z_terms": sum(1 for c in h_Z if abs(c) > 1e-9),
            "ising_offset": float(offset)
        },
        "energy_history": [float(val) for val in energy_history],
        "history": {
            "values": [float(val) for val in energy_history],
            "quantity": "expected_qubo_energy",
            "x": "function_evaluation",
            "running_best": False,
            "reference": {
                "value": float(calculate_qubo_energy(target_x, h, J)),
                "label": "Exact QUBO ground energy",
                "same_quantity": True
            }
        },
        "counts": dict(counts),
        "feasible_bitstrings": feasible_bitstrings_map,
        "sample_table": sample_rows,
        "best_bitstring": best_bitstr_repr,
        "target_ground_state_key": target_key,
        "notes": (
            "QAOA executed via StatevectorEstimator with Hamiltonian scaling. "
            "Simulated circuits — not executed on quantum hardware."
        )
    }
    
    return {
        "scenario_id": scenario_id,
        "method": f"QAOA (p={p}, Seed={seed})",
        "assignments": assignments,
        "unserved_calls": unserved,
        "weighted_response_cost": selected_resp,
        "coverage_penalty": selected_cov,
        "objective_value": selected_obj,
        "feasible": selected_feasible,
        "runtime_seconds": runtime,
        "experiment": experiment_payload
    }

def run_method(method: str, scenario_id: str = "scenario_2", **kwargs) -> dict[str, Any]:
    """
    Unified dispatcher executing the requested method.
    """
    m_lower = method.lower()
    if "greedy" in m_lower:
        return run_greedy(scenario_id)
    elif "exact" in m_lower or "classical" in m_lower:
        return run_exact(scenario_id)
    elif "qaoa" in m_lower or "quantum" in m_lower:
        p = kwargs.get("p", 1)
        seed = kwargs.get("seed", 10)
        maxiter = kwargs.get("maxiter", 100)
        shots = kwargs.get("shots", 1000)
        return run_qaoa(scenario_id, p=p, seed=seed, maxiter=maxiter, shots=shots)
    else:
        raise ValueError(f"Unknown dispatch method: {method}")
