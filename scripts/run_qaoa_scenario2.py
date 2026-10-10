"""
PairCover-Q (Scenario 2) QAOA Experiment & Audit Script.

Applies independent QAOA audit corrections:
1. Hamiltonian scaling in QAOA cost evolution: H_scaled = H_orig / scale,
   where scale = max(|coefficients|).
2. Cost evaluation against original unscaled Hamiltonian: <H_orig> + offset.
3. Correct parameter ordering matching installed QAOAAnsatz API (betas first, gammas second).
4. Documented initial parameter bounds (betas in [0, pi], gammas in [0, 2*pi])
   and initial optimization step size (rhobeg=0.5).
5. Programmatic derivation of exact classical optimum and Qiskit measurement key.
6. Honest reporting:
   - QUBO energy + 60 labeled as 'Penalized Surrogate Objective' for mixed/infeasible states.
   - Raw physical objective evaluated independently only on feasible states.
   - Explicit reporting of infeasible samples without silent repair.
   - Dual baseline comparisons:
     (A) Uniform random bitstrings across all 64 states.
     (B) Uniform random sampling over feasible assignments.
7. Exact statevector probabilities computed alongside 10,000-shot empirical sampling.
"""

import os
import sys

_SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import numpy as np
from scipy.optimize import minimize
import qiskit
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

from qrescue.optimization.scenario2 import (
    generate_qubo_scenario2, 
    calc_raw_objective, 
    VARIABLES_2
)
from qrescue.quantum.ising import qubo_to_ising
from qrescue.optimization.brute_force import generate_all_bitstrings
from qrescue.validation.validator import is_feasible, decode_qiskit_bitstring

def run_qaoa_experiment(p, seed, maxiter=200, shots=10000):
    print(f"\n{'='*60}")
    print(f"QAOA Experiment: Depth p={p}, Seed={seed}, MaxIter={maxiter}, Shots={shots}")
    print(f"{'='*60}", flush=True)
    
    # 1. Programmatic determination of classical baselines
    all_bitstrings = generate_all_bitstrings(6)
    feasible_bitstrings = [b for b in all_bitstrings if is_feasible(b, VARIABLES_2)]
    
    best_classical_cost = float('inf')
    exact_optimum_x = None
    for b in feasible_bitstrings:
        cost = calc_raw_objective(b, include_coverage=True)
        if cost < best_classical_cost:
            best_classical_cost = cost
            exact_optimum_x = b
            
    # Programmatic target key in Qiskit little-endian convention (q5 ... q0)
    target_key = "".join(str(bit) for bit in reversed(exact_optimum_x))
    
    # Baseline statistics
    baseline_a_feas_rate = len(feasible_bitstrings) / len(all_bitstrings)  # 13/64 = 20.31%
    baseline_a_opt_prob = 1.0 / len(all_bitstrings)                         # 1/64 = 1.5625%
    baseline_b_opt_prob = 1.0 / len(feasible_bitstrings)                    # 1/13 = 7.6923%
    
    # 2. Derive QUBO and Ising coefficients
    h, J = generate_qubo_scenario2()
    h_Z, J_Z, offset = qubo_to_ising(h, J, 6)
    
    paulis = []
    coeffs = []
    for i in range(6):
        if abs(h_Z[i]) > 1e-9:
            pauli_str = ['I'] * 6
            pauli_str[i] = 'Z'
            paulis.append("".join(reversed(pauli_str)))
            coeffs.append(h_Z[i])
            
    for (i, j), weight in J_Z.items():
        if abs(weight) > 1e-9:
            pauli_str = ['I'] * 6
            pauli_str[i] = 'Z'
            pauli_str[j] = 'Z'
            paulis.append("".join(reversed(pauli_str)))
            coeffs.append(weight)
            
    hamiltonian_orig = SparsePauliOp(paulis, coeffs)
    
    # Positive scaling factor from maximum absolute Hamiltonian coefficient
    scale = float(max(abs(c) for c in coeffs))
    scaled_coeffs = [c / scale for c in coeffs]
    hamiltonian_scaled = SparsePauliOp(paulis, scaled_coeffs)
    
    print(f"Original Hamiltonian: {len(hamiltonian_orig)} Pauli terms")
    print(f"Hamiltonian Scaling Factor: {scale:.4f} (max absolute coefficient)")
    print(f"Ising constant offset: {offset:.4f}")
    print(f"Exact Classical Optimum: x={exact_optimum_x}, Target Qiskit Key='{target_key}', Cost={best_classical_cost}")
    
    # 3. Build QAOA Ansatz with scaled Hamiltonian
    ansatz = QAOAAnsatz(hamiltonian_scaled, reps=p)
    param_names = [ascii(p_var.name) for p_var in ansatz.parameters]
    print(f"Ansatz Parameters ({len(param_names)}): {param_names}")
    
    # 4. Evaluator: Evaluate expectation of original unscaled Hamiltonian + offset
    estimator = StatevectorEstimator()
    eval_count = 0
    
    def cost_func(params):
        nonlocal eval_count
        eval_count += 1
        pub = (ansatz, hamiltonian_orig, params)
        job = estimator.run([pub])
        exp_val = float(job.result()[0].data.evs)
        return exp_val + offset

    # 5. Parameter initialization consistent with parameter ordering:
    # Betas are mixer parameters: range [0, pi]
    # Gammas are cost evolution parameters: range [0, 2*pi]
    np.random.seed(seed)
    initial_betas = np.random.uniform(0, np.pi, p)
    initial_gammas = np.random.uniform(0, 2 * np.pi, p)
    initial_point = np.concatenate([initial_betas, initial_gammas])
    
    initial_qubo_energy = cost_func(initial_point)
    print(f"Initial parameters: {np.round(initial_point, 4)}")
    print(f"Initial QUBO Energy: {initial_qubo_energy:.4f}")
    print(f"Initial Penalized Surrogate Objective (Energy + 60): {initial_qubo_energy + 60:.4f}")
    
    # 6. Variational Optimization with documented initial step (rhobeg=0.5)
    print("\nRunning COBYLA optimization...")
    opt_result = minimize(
        cost_func,
        initial_point,
        method='COBYLA',
        options={'maxiter': maxiter, 'rhobeg': 0.5}
    )
    
    final_qubo_energy = opt_result.fun
    print(f"Optimizer Termination: success={opt_result.success}")
    print(f"Status Message: {opt_result.message}")
    print(f"Evaluations (nfev): {opt_result.nfev} (recorded: {eval_count})")
    print(f"Final parameters: {np.round(opt_result.x, 4)}")
    print(f"Final Expected QUBO Energy (Statevector): {final_qubo_energy:.4f}")
    print(f"Final Expected Penalized Surrogate Objective (Energy + 60): {final_qubo_energy + 60:.4f}")
    
    # 7. Exact Statevector Probabilities (zero shot noise)
    bound_circ = ansatz.assign_parameters(opt_result.x)
    sv = Statevector(bound_circ)
    probs_dict = sv.probabilities_dict()
    exact_sv_opt_prob = probs_dict.get(target_key, 0.0)
    
    # Exact feasibility rate from statevector
    exact_sv_feas_rate = 0.0
    for bitstr, prob in probs_dict.items():
        x_dec, _ = decode_qiskit_bitstring(bitstr, VARIABLES_2)
        if is_feasible(x_dec, VARIABLES_2):
            exact_sv_feas_rate += prob
            
    print(f"\nExact Statevector Analysis (Theoretical Limit):")
    print(f"  Exact Statevector Feasibility Rate: {exact_sv_feas_rate:.2%}")
    print(f"  Exact Statevector Ground State Probability: {exact_sv_opt_prob:.2%}")
    
    # 8. Empirical Sampling with 10,000 shots
    bound_circ_meas = bound_circ.copy()
    bound_circ_meas.measure_all()
    sampler = StatevectorSampler(seed=seed)
    pub = (bound_circ_meas,)
    job = sampler.run([pub], shots=shots)
    counts = job.result()[0].data.meas.get_counts()
    
    feasible_count = 0
    infeasible_count = 0
    optimum_hits = counts.get(target_key, 0)
    best_feasible_cost = float('inf')
    best_feasible_assignment = None
    
    sampled_qubo_energy_sum = 0.0
    
    for bitstr, count in counts.items():
        x_dec, assignments = decode_qiskit_bitstring(bitstr, VARIABLES_2)
        
        # Calculate QUBO energy of this state
        e_x = sum(h[i] * x_dec[i] for i in range(6)) + sum(
            J.get((i, j), 0) * x_dec[i] * x_dec[j] for i in range(6) for j in range(i+1, 6)
        )
        sampled_qubo_energy_sum += e_x * count
        
        # Validate feasibility independently
        if is_feasible(x_dec, VARIABLES_2):
            feasible_count += count
            raw_cost = calc_raw_objective(x_dec, include_coverage=True)
            if raw_cost < best_feasible_cost:
                best_feasible_cost = raw_cost
                best_feasible_assignment = assignments
        else:
            infeasible_count += count
            
    sampled_mean_qubo_energy = sampled_qubo_energy_sum / shots
    empirical_feas_rate = feasible_count / shots
    empirical_opt_prob = optimum_hits / shots
    
    print(f"\nEmpirical Sampling Results ({shots} shots):")
    print(f"  Feasible Samples: {feasible_count} ({empirical_feas_rate:.2%})")
    print(f"  Infeasible Samples (reported explicitly): {infeasible_count} ({infeasible_count/shots:.2%})")
    print(f"  Exact Optimum Hits: {optimum_hits} ({empirical_opt_prob:.2%})")
    print(f"  Sampled Mean QUBO Energy: {sampled_mean_qubo_energy:.4f}")
    print(f"  Sampled Mean Penalized Surrogate Objective: {sampled_mean_qubo_energy + 60:.4f}")
    print(f"  Best Feasible Raw Objective Found: {best_feasible_cost} ({best_feasible_assignment})")
    
    # 9. Comparison against baselines
    print("\n--- Comparative Evaluation ---")
    print(f"{'Method / Baseline':<40} {'Feasibility Rate':<20} {'P(Exact Optimum)':<20}")
    print("-" * 80)
    print(f"{'Baseline A: Uniform Random (64 states)':<40} {f'{baseline_a_feas_rate:.2%}':<20} {f'{baseline_a_opt_prob:.2%}':<20}")
    print(f"{'Baseline B: Uniform Feasible (13 states)':<40} {'100.00%':<20} {f'{baseline_b_opt_prob:.2%}':<20}")
    print(f"{'QAOA Exact Statevector (p=' + str(p) + ')':<40} {f'{exact_sv_feas_rate:.2%}':<20} {f'{exact_sv_opt_prob:.2%}':<20}")
    print(f"{'QAOA Empirical Sampled (p=' + str(p) + ')':<40} {f'{empirical_feas_rate:.2%}':<20} {f'{empirical_opt_prob:.2%}':<20}")
    print("-" * 80)
    
    return {
        "p": p,
        "seed": seed,
        "maxiter": maxiter,
        "shots": shots,
        "scale": scale,
        "success": opt_result.success,
        "message": opt_result.message,
        "nfev": opt_result.nfev,
        "initial_params": initial_point.tolist(),
        "final_params": opt_result.x.tolist(),
        "initial_qubo_energy": initial_qubo_energy,
        "final_qubo_energy": final_qubo_energy,
        "sv_feas_rate": exact_sv_feas_rate,
        "sv_opt_prob": exact_sv_opt_prob,
        "sampled_feas_rate": empirical_feas_rate,
        "sampled_opt_prob": empirical_opt_prob,
        "optimum_hits": optimum_hits,
        "best_cost": best_feasible_cost
    }

def main():
    print("=================================================================")
    print("PairCover-Q QAOA Corrected Multi-Seed Experiment (Q-Rescue)")
    print("=================================================================")
    
    results = []
    
    # Phase 5: Three reproducible p=1 optimization runs
    print("\n>>> Phase 5.1: Three reproducible p=1 runs (Seeds 10, 42, 99) <<<")
    for s in [10, 42, 99]:
        res = run_qaoa_experiment(p=1, seed=s, maxiter=200, shots=10000)
        results.append(res)
        
    # Phase 5.2: One p=2 experiment
    print("\n>>> Phase 5.2: One p=2 run (Seed 42) <<<")
    res_p2 = run_qaoa_experiment(p=2, seed=42, maxiter=400, shots=10000)
    results.append(res_p2)
    
    print("\n" + "="*70)
    print("SUMMARY OF ALL AUDITED RUNS")
    print("="*70)
    for r in results:
        print(f"p={r['p']} | Seed={r['seed']} | Evals={r['nfev']} | Status={r['success']} | "
              f"SV Feas={r['sv_feas_rate']:.2%} | SV Opt={r['sv_opt_prob']:.2%} | "
              f"Sampled Feas={r['sampled_feas_rate']:.2%} | Sampled Opt={r['sampled_opt_prob']:.2%} | "
              f"Opt Hits={r['optimum_hits']}/10000 | Best Cost={r['best_cost']}")
    print("="*70)

if __name__ == "__main__":
    main()
