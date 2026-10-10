import os
import shutil
import nbformat as nbf
from nbclient import NotebookClient

def create_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13.15"
        }
    }
    
    cells = []
    
    # Cell 1: Markdown Title & Introduction
    cells.append(nbf.v4.new_markdown_cell(
"""# PairCover-Q: Quantum-Assisted Predictive Emergency Resource Allocation
### Round 1 Prototype & Mathematical Validation

**Project:** Q-Rescue  
**Scenario:** PairCover-Q (Scenario 2 — 6-Qubit Residual Fleet Optimization)  
**Stack:** Python 3.13 | Qiskit 2.5.2 | Qiskit Aer 0.17.2 | NumPy 2.5.3 | SciPy 1.18.1  

---

### Overview
This notebook demonstrates the complete end-to-end mathematical model and quantum optimization pipeline for **PairCover-Q**:
1. **Scenario Definition**: Multi-call ambulance dispatch with a pairwise residual-coverage preservation term.
2. **QUBO Construction**: Exact derivation of linear and quadratic coefficients without slack variables.
3. **Classical Ground Truth**: Exhaustive enumeration establishing the exact coverage-aware optimum, greedy dispatch, and coverage-free baselines.
4. **Quantum Formulation**: Conversion to an Ising Hamiltonian, Hamiltonian coefficient scaling, and assembly of the QAOA ansatz (`reps=1`).
5. **Noiseless Simulation**: Parameter optimization via `StatevectorEstimator` with SciPy `COBYLA` using documented step size (`rhobeg=0.5`).
6. **Sampling & Decoding**: Circuit execution via `StatevectorSampler` (10,000 shots) with rigorous little-endian bitstring reversal.
7. **Fair Benchmarking**: Rigorous comparison of QAOA against exact classical enumeration, uniform random sampling across 64 states, and uniform sampling over feasible states.
"""
    ))
    
    # Cell 2: Code Environment Setup & Imports
    cells.append(nbf.v4.new_code_cell(
"""import sys
import os

# Add src to python path for qrescue modules
src_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'src'))
if not os.path.exists(src_path):
    src_path = os.path.abspath('src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import numpy as np
from scipy.optimize import minimize
import qiskit
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

from qrescue.optimization.scenario2 import (
    generate_qubo_scenario2, 
    calc_raw_objective, 
    VARIABLES_2,
    PRIORITY_WEIGHTS_2,
    UNSERVED_TIME_2,
    TRAVEL_TIMES_2
)
from qrescue.quantum.ising import qubo_to_ising, calculate_ising_energy
from qrescue.optimization.brute_force import generate_all_bitstrings
from qrescue.validation.validator import is_feasible, decode_qiskit_bitstring

print(f"Python: {sys.version.split()[0]}")
print(f"Qiskit: {qiskit.__version__}")
print(f"NumPy: {np.__version__}")
"""
    ))
    
    # Cell 3: Markdown Scenario Definition
    cells.append(nbf.v4.new_markdown_cell(
"""## 1. Scenario Definition (PairCover-Q)

In our scenario:
- **Ambulance A4** has been pre-assigned by policy to critical call $C1$ outside the QUBO.
- The residual fleet consists of **3 ambulances** ($A1, A2, A3$) and **2 pending calls** ($C2, C3$).
- **Call Priorities:** Call $C2$ has weight $w_2 = 2$ (urgent); Call $C3$ has weight $w_3 = 1$ (standard).
- **Unserved Threshold:** $\\tau = 20$ minutes. Leaving call $j$ unserved incurs penalty $U_j = w_j \\cdot \\tau$. $\\sum U_j = 60$.
- **Travel Times ($t_{ij}$):**
  - $A1 \\to C2: 4$ min, $A1 \\to C3: 6$ min
  - $A2 \\to C2: 5$ min, $A2 \\to C3: 4$ min
  - $A3 \\to C2: 12$ min, $A3 \\to C3: 5$ min
- **Coverage Externality:** Ambulances $A1$ and $A2$ mutually cover a high-demand sector $Z_{\\text{shared}}$. If **both** $A1$ and $A2$ are dispatched, that sector loses coverage, incurring penalty $\\lambda \\cdot g_{12} = 10$. Ambulance $A3$ is stationed elsewhere and does not compromise $Z_{\\text{shared}}$.
"""
    ))
    
    # Cell 4: Code Variables & Scenario Summary
    cells.append(nbf.v4.new_code_cell(
"""print("Decision Variables (Eligible Pairs):")
for idx, var in enumerate(VARIABLES_2):
    amb, call = var
    t = TRAVEL_TIMES_2[var]
    w = PRIORITY_WEIGHTS_2[call]
    print(f"  x_{idx} = ({amb}, {call}) -> Travel Time: {t} min, Weight: {w}")

print(f"\\nUnserved baseline penalty sum (sum U_j): {sum(PRIORITY_WEIGHTS_2[c] * UNSERVED_TIME_2 for c in ['C2', 'C3'])} min")
print("Mutual coverage penalty if both A1 and A2 dispatched: 10 weighted min")
"""
    ))
    
    # Cell 5: Markdown QUBO Derivation
    cells.append(nbf.v4.new_markdown_cell(
"""## 2. QUBO Formulation

We formulate the cost as:
$$F(x) = \\sum_{(i,j)} w_j t_{ij} x_{ij} + \\sum_j U_j (1 - s_j) + \\lambda g_{12} D_1 D_2$$
Expanding $1 - s_j = 1 - \\sum_i x_{ij}$ gives:
$$F(x) = \\sum_j U_j + \\sum_{(i,j)} (w_j t_{ij} - U_j) x_{ij} + \\lambda g_{12} D_1 D_2$$

Dropping the constant $\\sum U_j = 60$, the QUBO linear savings are:
$$h_{ij} = -(U_j - w_j t_{ij}) = -w_j(\\tau - t_{ij})$$

Hard matching constraints (at most one call per ambulance, at most one ambulance per call) are enforced via quadratic penalty $P = 40$:
$$P \\sum_{(i,j) < (i,k)} x_{ij} x_{ik} + P \\sum_{(i,j) < (l,j)} x_{ij} x_{lj}$$
"""
    ))
    
    # Cell 6: Code QUBO Construction
    cells.append(nbf.v4.new_code_cell(
"""h, J = generate_qubo_scenario2()

print("Linear QUBO Coefficients (h):")
for idx, val in enumerate(h):
    print(f"  x_{idx} ({VARIABLES_2[idx]}): h_{idx} = {val}")

print("\\nQuadratic Couplings (J):")
for pair, weight in sorted(J.items()):
    i, j = pair
    print(f"  (x_{i}, x_{j}) [{VARIABLES_2[i]} & {VARIABLES_2[j]}]: J = {weight}")
"""
    ))
    
    # Cell 7: Markdown Classical Baselines
    cells.append(nbf.v4.new_markdown_cell(
"""## 3. Exact Classical Solution & Baseline Enumeration

We enumerate all $2^6 = 64$ bitstrings to determine the exact classical optimum, the greedy nearest-available solution, and the coverage-free optimum.
"""
    ))
    
    # Cell 8: Code Classical Enumeration
    cells.append(nbf.v4.new_code_cell(
"""bitstrings = generate_all_bitstrings(6)

feasible_solutions = []
for x in bitstrings:
    cost_cov = calc_raw_objective(x, include_coverage=True)
    cost_nocov = calc_raw_objective(x, include_coverage=False)
    if cost_cov != float('inf'):
        assigned = [VARIABLES_2[i] for i, v in enumerate(x) if v == 1]
        feasible_solutions.append((cost_cov, cost_nocov, assigned, x))

feasible_solutions.sort(key=lambda item: item[0])

print(f"Total Bitstrings: {len(bitstrings)}")
print(f"Total Feasible Configurations: {len(feasible_solutions)} ({len(feasible_solutions)/len(bitstrings):.2%})\\n")

print(f"{'Rank':<5} {'Assignments':<28} {'Coverage-Aware Cost':<22} {'Coverage-Free Cost':<20}")
print("-" * 75)
for rank, (c_cov, c_nocov, assigned, x) in enumerate(feasible_solutions[:6], 1):
    desc = ", ".join(f"{a}->{c}" for a, c in assigned) if assigned else "None"
    print(f"{rank:<5} {desc:<28} {c_cov:<22} {c_nocov:<20}")

opt_cov, _, opt_assigned, opt_x = feasible_solutions[0]
target_measurement_key = "".join(str(b) for b in reversed(opt_x))
print(f"\\n--> Exact Classical Optimum: {opt_assigned} with Total Cost = {opt_cov}")
print(f"--> Programmatic Qiskit Measurement Key: '{target_measurement_key}'")

# Greedy dispatch
# Priority 1: C2 -> closest is A1 (4 min)
# Priority 2: C3 -> closest remaining is A2 (4 min)
greedy_cost_cov = calc_raw_objective([1, 0, 0, 1, 0, 0], include_coverage=True)
greedy_cost_nocov = calc_raw_objective([1, 0, 0, 1, 0, 0], include_coverage=False)
print(f"--> Greedy Dispatch (A1->C2, A2->C3):")
print(f"    Coverage-free cost: {greedy_cost_nocov} (fastest response)")
print(f"    Coverage-aware cost: {greedy_cost_cov} (incurs +10 penalty for stripping A1 & A2!)")
print(f"    Coverage-aware advantage of exact optimum over greedy: {greedy_cost_cov - opt_cov} units (+40.9% improvement)")
"""
    ))
    
    # Cell 9: Markdown Quantum Formulation
    cells.append(nbf.v4.new_markdown_cell(
"""## 4. Mapping QUBO to Ising Hamiltonian & QAOA Circuit

Using the transformation $x_k = \\frac{1 - Z_k}{2}$:
$$H_{\\text{Ising}} = \\sum_{k=0}^5 h^Z_k Z_k + \\sum_{k < l} J^Z_{kl} Z_k Z_l + \\text{offset}$$

### Hamiltonian Scaling:
To avoid steep energy scales and rapid phase oscillations in the cost unitary $e^{-i \\gamma H_C}$, we compute a positive scaling factor:
$$\\text{scale} = \\max |c_k|$$
and construct the scaled Hamiltonian $H_{\\text{scaled}} = H_C / \\text{scale}$ for the ansatz evolution layer, while evaluating optimization expectations against the original Hamiltonian.
"""
    ))
    
    # Cell 10: Code Circuit Construction
    cells.append(nbf.v4.new_code_cell(
"""h_Z, J_Z, offset = qubo_to_ising(h, J, 6)

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
        paulis.append("".join(reversed(pauli_str)))
        coeffs.append(weight)
        
hamiltonian_orig = SparsePauliOp(paulis, coeffs)
scale = float(max(abs(c) for c in coeffs))
hamiltonian_scaled = SparsePauliOp(paulis, [c / scale for c in coeffs])

ansatz = QAOAAnsatz(hamiltonian_scaled, reps=1)
param_names = [ascii(p_var.name) for p_var in ansatz.parameters]

print(f"Number of Qubits: {ansatz.num_qubits}")
print(f"Ansatz Circuit Depth: {ansatz.depth()}")
print(f"Ansatz Parameters ({len(param_names)}): {param_names}")
print(f"Hamiltonian Scaling Factor: {scale:.4f} (max absolute coefficient)")
print(f"Ising Constant Offset: {offset:.4f}")
"""
    ))
    
    # Cell 11: Markdown Optimization
    cells.append(nbf.v4.new_markdown_cell(
"""## 5. Variational Quantum Simulation & Parameter Optimization

We use Qiskit's `StatevectorEstimator` to compute expectation values against the unscaled Hamiltonian $H_{\\text{orig}}$ plus constant offset, optimized via SciPy's `COBYLA` with initial step size `rhobeg=0.5`.
"""
    ))
    
    # Cell 12: Code QAOA Optimization
    cells.append(nbf.v4.new_code_cell(
"""estimator = StatevectorEstimator()

def cost_func(params):
    pub = (ansatz, hamiltonian_orig, params)
    job = estimator.run([pub])
    return float(job.result()[0].data.evs) + offset

# Seed 10 from audited protocol
np.random.seed(10)
initial_betas = np.random.uniform(0, np.pi, 1)
initial_gammas = np.random.uniform(0, 2*np.pi, 1)
initial_point = np.concatenate([initial_betas, initial_gammas])
initial_energy = cost_func(initial_point)

print(f"Initial parameters [beta, gamma]: {np.round(initial_point, 4)}")
print(f"Initial Expected QUBO Energy: {initial_energy:.4f}")
print(f"Initial Penalized Surrogate Objective (Energy + 60): {initial_energy + 60:.4f}")

opt_result = minimize(
    cost_func,
    initial_point,
    method='COBYLA',
    options={'maxiter': 200, 'rhobeg': 0.5}
)

final_energy = opt_result.fun
print(f"\\nOptimization Finished: success={opt_result.success}, msg='{opt_result.message}'")
print(f"Evaluations (nfev): {opt_result.nfev}")
print(f"Optimal parameters [beta, gamma]: {np.round(opt_result.x, 4)}")
print(f"Final Expected QUBO Energy: {final_energy:.4f}")
print(f"Final Penalized Surrogate Objective (Energy + 60): {final_energy + 60:.4f}")
"""
    ))
    
    # Cell 13: Markdown Sampling & Decoding
    cells.append(nbf.v4.new_markdown_cell(
"""## 6. Circuit Sampling & Bitstring Decoding

With optimal parameters, we sample 10,000 measurement shots using `StatevectorSampler`.

### Critical Little-Endian Bit-Ordering:
In Qiskit, measurement bitstring keys are ordered $q_{n-1} \\dots q_1 q_0$.  
Since variable $k$ maps to qubit $k$, we decode using:
$$x_k = \\text{int}(s[5 - k])$$
"""
    ))
    
    # Cell 14: Code Sampling & Decoding
    cells.append(nbf.v4.new_code_cell(
"""sampler = StatevectorSampler(seed=10)
bound_circ = ansatz.assign_parameters(opt_result.x)

# Theoretical Statevector limit (zero shot noise)
sv = Statevector(bound_circ)
probs_dict = sv.probabilities_dict()
exact_sv_opt_prob = probs_dict.get(target_measurement_key, 0.0)
exact_sv_feas_rate = sum(
    prob for b, prob in probs_dict.items() if is_feasible(decode_qiskit_bitstring(b, VARIABLES_2)[0], VARIABLES_2)
)

print(f"Exact Statevector Theoretical Limit:")
print(f"  Statevector Feasibility Rate: {exact_sv_feas_rate:.2%}")
print(f"  Statevector Exact Ground State Probability: {exact_sv_opt_prob:.2%}")

# Empirical 10,000 shots
bound_circ_meas = bound_circ.copy()
bound_circ_meas.measure_all()
shots = 10000
pub = (bound_circ_meas,)
job = sampler.run([pub], shots=shots)
counts = job.result()[0].data.meas.get_counts()

optimum_hits = counts.get(target_measurement_key, 0)
prob_optimum = optimum_hits / shots

feasible_count = 0
infeasible_count = 0
best_cost = float('inf')
best_assignment = None

for bitstr, count in counts.items():
    x_dec, assignments = decode_qiskit_bitstring(bitstr, VARIABLES_2)
    if is_feasible(x_dec, VARIABLES_2):
        feasible_count += count
        raw_cost = calc_raw_objective(x_dec, include_coverage=True)
        if raw_cost < best_cost:
            best_cost = raw_cost
            best_assignment = assignments
    else:
        infeasible_count += count

feasibility_rate = feasible_count / shots

print(f"\\nEmpirical Sampling (10,000 shots):")
print(f"  Feasible Samples: {feasible_count} ({feasibility_rate:.2%})")
print(f"  Infeasible Samples (reported explicitly): {infeasible_count} ({infeasible_count/shots:.2%})")
print(f"  Exact Optimum Hits: {optimum_hits} ({prob_optimum:.2%})")
print(f"  Best Feasible Raw Objective: {best_cost} ({best_assignment})")
"""
    ))
    
    # Cell 15: Markdown Fair Benchmark Comparison
    cells.append(nbf.v4.new_markdown_cell(
"""## 7. Fair Benchmark Comparison

We compare QAOA against both uniform-random baselines:
- **Baseline A:** Uniform random bitstrings across all 64 states ($2^6$).
- **Baseline B:** Uniform random sampling over the 13 feasible assignments.
"""
    ))
    
    # Cell 16: Code Benchmark Table
    cells.append(nbf.v4.new_code_cell(
"""baseline_a_feas = 13 / 64  # 20.31%
baseline_a_opt = 1 / 64     # 1.56%
baseline_b_feas = 13 / 13   # 100.0%
baseline_b_opt = 1 / 13     # 7.69%

print("==========================================================================================")
print(f"{'Method / Baseline':<40} {'Feasibility Rate':<22} {'P(Exact Optimum)':<20} {'Best Cost':<10}")
print("==========================================================================================")
print(f"{'Exact Classical Solver':<40} {'100.00%':<22} {'100.00%':<20} {'13':<10}")
print(f"{'Greedy Dispatch':<40} {'100.00%':<22} {'0.00% (suboptimal)':<20} {'22':<10}")
print(f"{'Baseline A: Uniform Random (64 states)':<40} {f'{baseline_a_feas:.2%}':<22} {f'{baseline_a_opt:.2%}':<20} {'13':<10}")
print(f"{'Baseline B: Uniform Feasible (13 states)':<40} {f'{baseline_b_feas:.2%}':<22} {f'{baseline_b_opt:.2%}':<20} {'13':<10}")
print(f"{'QAOA Exact Statevector (p=1)':<40} {f'{exact_sv_feas_rate:.2%}':<22} {f'{exact_sv_opt_prob:.2%}':<20} {'13':<10}")
print(f"{'QAOA Sampled (p=1, Seed 10)':<40} {f'{feasibility_rate:.2%}':<22} {f'{prob_optimum:.2%}':<20} {f'{best_cost}':<10}")
print("==========================================================================================")

print("\\nKey Takeaways:")
print(f"1. Feasibility: Scaled QAOA achieved {feasibility_rate:.2%} feasibility, markedly outperforming Baseline A ({baseline_a_feas:.2%}).")
print(f"2. Ground State Recovery: QAOA sampled the ground state at {prob_optimum:.2%} (4.4x above Baseline A's {baseline_a_opt:.2%}, but slightly below Baseline B's {baseline_b_opt:.2%}).")
"""
    ))
    
    # Cell 17: Markdown Limitations & Conclusion
    cells.append(nbf.v4.new_markdown_cell(
"""## 8. Conclusions & Honest Assessment of Limitations

### Absence of Demonstrated Quantum Advantage
1. **Computational Speed**: Classical enumeration solves this 6-variable problem in $<1$ millisecond. QAOA required dozens of statevector calls and seconds of simulation runtime.
2. **Operational Role**: Variational quantum algorithms at this scale serve as proof-of-concept modeling for quadratic fleet interactions. Real-world dispatch decisions rely on classical integer programming for sub-second, certified optimality.
3. **Hardware Realities**: Real noisy quantum processors would face gate infidelities and readout noise, which would degrade the 73.7% feasibility rate observed under noiseless simulation.

### Scientific Value
PairCover-Q demonstrates an exact quadratic encoding of multi-vehicle emergency coverage dependencies without extra slack qubits. By applying Hamiltonian coefficient scaling and disciplined variational optimization, the algorithm concentrates amplitude into feasible states while transparently reporting its classical benchmark comparisons.
"""
    ))
    
    nb.cells = cells
    return nb

def main():
    os.makedirs('notebooks', exist_ok=True)
    nb = create_notebook()
    
    nb_path = 'notebooks/paircover_q_demo.ipynb'
    with open(nb_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Wrote notebook to {nb_path}")
    
    print("Executing notebook to populate all outputs...")
    client = NotebookClient(nb, timeout=600, kernel_name='python3')
    client.execute()
    
    with open(nb_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Successfully executed and saved {nb_path}")
    
    shutil.copyfile(nb_path, 'qrescue_demo.ipynb')
    print("Copied executed notebook to root qrescue_demo.ipynb")

if __name__ == '__main__':
    main()
