# PairCover-Q: Audited QAOA Benchmark & Mathematical Validation Report

**Project:** Q-Rescue — Quantum-Assisted Predictive Emergency Resource Allocation  
**Milestone:** Post-Audit Verified Release Artifacts  
**Date:** October 10, 2026  
**Status:** Independently Corrected, Fully Audited & Locally Reproduced  

---

## 1. Executive Summary

This report documents the local verification and experimental results of **PairCover-Q (Scenario 2)** following the independent audit corrections.

### Key Corrections Applied & Verified
1. **Hamiltonian Coefficient Scaling:** Rescaled the Ising Hamiltonian by $\text{scale} = \max_k |c_k| = 28.0$ in the QAOA cost evolution layer ($H_{\text{scaled}} = H_{\text{orig}} / 28.0$), smoothing the variational landscape while evaluating expectation values consistently against the original unscaled Hamiltonian $H_{\text{orig}}$ plus constant offset.
2. **Ansatz Parameter Ordering:** Verified that Qiskit's `QAOAAnsatz` orders all $\beta$ (mixer) parameters first and all $\gamma$ (cost evolution) parameters second. Parameter initializations were mapped accordingly ($\beta \in [0, \pi]$, $\gamma \in [0, 2\pi]$).
3. **Disciplined Optimizer Step:** Set COBYLA's initial trust region step size to `rhobeg = 0.5` (down from default 1.0), enabling stable, reproducible convergence. All runs now terminate with `success=True`.
4. **Programmatic Baselines & Key Mapping:** Removed hardcoded target bitstrings; the exact classical optimum and its Qiskit measurement key (`'100001'`) are derived programmatically from the declared variable ordering.
5. **Rigorous Dual Baselines:** Evaluated QAOA against both:
   - **Baseline A:** Uniform random bitstrings across all 64 states ($2^6$).
   - **Baseline B:** Uniform random sampling over the 13 feasible assignments.
6. **Honest Metric Definitions:** Labeled $H(x) + 60$ on infeasible/mixed states as **Penalized Surrogate Objective**, reserving **Raw Physical Objective** strictly for feasible states evaluated against ground-truth response and coverage tables.

---

## 2. Synthetic Coverage-Aware Scenario (PairCover-Q / Scenario 2)

### 2.1 Problem Setup
Ambulance $A4$ has been pre-assigned by policy to high-severity call $C1$ outside the residual-coverage QUBO. The quantum dispatch engine optimizes the residual fleet:
- **Ambulances:** $A_1, A_2, A_3$
- **Pending Calls:**
  - $C_2$: Priority weight $w_2 = 2$
  - $C_3$: Priority weight $w_3 = 1$
- **Unserved Equivalent Threshold:** $\tau = 20$ minutes  
  Unserved penalties: $U_2 = 2 \times 20 = 40$, $U_3 = 1 \times 20 = 20$, $\sum_j U_j = 60$ weighted minutes.
- **Estimated Travel Times ($t_{ij}$):**
  - $A_1 \to C_2 = 4\text{ min}$, $A_1 \to C_3 = 6\text{ min}$
  - $A_2 \to C_2 = 5\text{ min}$, $A_2 \to C_3 = 4\text{ min}$
  - $A_3 \to C_2 = 12\text{ min}$, $A_3 \to C_3 = 5\text{ min}$

### 2.2 Coverage Externality
- Ambulances $A_1$ and $A_2$ form a mutual backup pair for a shared geographic sector $Z_{\text{shared}}$.
- If either $A_1$ or $A_2$ is dispatched alone, $Z_{\text{shared}}$ remains covered by the other unit.
- If **both** $A_1$ and $A_2$ are dispatched simultaneously, $Z_{\text{shared}}$ loses coverage, incurring a quadratic penalty:
  $$\lambda \cdot g_{12} = 10\text{ weighted minutes}$$
- Ambulance $A_3$ is stationed in an independent sector and does not compromise $Z_{\text{shared}}$.

### 2.3 Decision Variables & QUBO Formulation
Six binary decision variables $x_k \in \{0, 1\}$ map to eligible dispatch pairs:
- $x_0 = (A_1, C_2)$
- $x_1 = (A_1, C_3)$
- $x_2 = (A_2, C_2)$
- $x_3 = (A_2, C_3)$
- $x_4 = (A_3, C_2)$
- $x_5 = (A_3, C_3)$

The cost function minimized over feasible assignments is:
$$F(x) = \sum_{(i,j) \in E} w_j t_{ij} x_{ij} + \sum_j U_j (1 - s_j) + \lambda g_{12} D_1 D_2$$
where $s_j = \sum_i x_{ij}$ and $D_i = \sum_j x_{ij}$.

In QUBO form:
$$H(x) = \sum_{k=0}^5 h_k x_k + \sum_{k < l} J_{kl} x_k x_l$$
with constant baseline offset $\sum_j U_j = 60$, such that $F(x) = H(x) + 60$ on all feasible states.

- **Linear Coefficients ($h_k = -w_j(\tau - t_{ij})$):**
  $$h = [-32, -14, -30, -16, -16, -15]$$
- **Quadratic Couplings ($J_{kl}$):**
  - Assignment penalty $P_A = P_C = 40$ on one-to-one conflicts (same ambulance or same call):
    - Couplings of $40$: $(0,1), (2,3), (4,5), (0,4), (2,4), (1,5), (3,5)$
  - Call conflict plus joint coverage penalty ($P_C + \lambda g_{12} = 40 + 10 = 50$):
    - Couplings of $50$: $(0,2), (1,3)$
  - Cross-assignment joint coverage penalty ($\lambda g_{12} = 10$):
    - Couplings of $10$: $(0,3), (1,2)$
  - All remaining couplings are $0$.

---

## 3. Classical Baselines & Exhaustive Enumeration

Across all $2^6 = 64$ bitstrings, direct enumeration establishes the ground truth:

### 3.1 Solution Candidates Comparison

| Strategy | Selected Assignments | Response Time Cost | Coverage Penalty | Total Objective | Feasible? |
|---|---|---|---|---|---|
| **Exact Coverage-Aware Optimum** | **$A1 \to C2, A3 \to C3$** | **13** | **0** | **13** | **Yes** |
| Coverage-Free Classical Optimum ($\lambda=0$) | $A1 \to C2, A2 \to C3$ | 12 | 10 | 22 | Yes |
| Greedy (Nearest-Available by Priority) | $A1 \to C2, A2 \to C3$ | 12 | 10 | 22 | Yes |
| Classical Alternative | $A2 \to C2, A3 \to C3$ | 15 | 0 | 15 | Yes |
| Inverted Assignment | $A1 \to C3, A2 \to C2$ | 16 | 10 | 26 | Yes |
| Partial Dispatch (Single unit) | $A1 \to C2$ only | 28 | 0 | 28 | Yes |
| Null Dispatch (No units) | None (all unserved) | 60 | 0 | 60 | Yes |

### 3.2 Operational Trade-Off
- **Greedy Deficit:** Priority-greedy dispatch sends $A1$ to $C2$ (4 min) and $A2$ to $C3$ (4 min). Response time is minimized (12), but mutual coverage for $Z_{\text{shared}}$ is stripped, adding +10 penalty for total cost **22**.
- **Coverage-Aware Resolution:** Sacrifices 1 minute on $C3$ ($A3$ arrives in 5 min instead of $A2$ in 4 min). Leaves $A2$ idle and stationed, preserving regional coverage and eliminating the 10-point penalty. Total cost is **13** (+40.9% improvement over greedy).

---

## 4. Audited QAOA Experimental Results

### 4.1 Audit Configuration
- **Qiskit Version:** 2.5.2 | **Qiskit Aer Version:** 0.17.2 | **SciPy Version:** 1.18.1
- **Cost Evolution:** Scaled Hamiltonian $H_{\text{scaled}} = H_{\text{orig}} / 28.0$.
- **Ansatz:** `QAOAAnsatz(hamiltonian_scaled, reps=p)` with unconstrained $X$-mixer.
- **Optimizer:** `scipy.optimize.minimize(method='COBYLA', options={'maxiter': maxiter, 'rhobeg': 0.5})`.
- **Expectation Evaluator:** `StatevectorEstimator` evaluating $\langle H_{\text{orig}} \rangle + 38.5$.
- **Sampling:** `StatevectorSampler` (10,000 shots).
- **Bitstring Mapping:** Little-endian reversal ($x_k = s[5 - k]$).

### 4.2 Verified Execution Logs & Metrics

| Metric | Run 1 ($p=1$) | Run 2 ($p=1$) | Run 3 ($p=1$) | Run 4 ($p=2$) | Baseline A (Uniform 64) | Baseline B (Uniform 13) |
|---|---|---|---|---|---|---|
| **Random Seed** | 10 | 42 | 99 | 42 | N/A | N/A |
| **Max Iterations** | 200 | 200 | 200 | 400 | N/A | N/A |
| **COBYLA Status** | `success=True` | `success=True` | `success=True` | `success=True` | N/A | N/A |
| **Function Evals (`nfev`)** | 35 | 42 | 35 | 121 | 0 | 0 |
| **Initial QUBO Energy** | 18.0691 | 37.6055 | 29.9261 | 24.7352 | N/A | N/A |
| **Final QUBO Energy** | -19.2905 | -4.1047 | 8.2677 | -9.6698 | N/A | N/A |
| **Final Surrogate (E + 60)** | 40.7095 | 55.8953 | 68.2677 | 50.3302 | N/A | N/A |
| **SV Feasibility Rate** | **73.41%** | **46.88%** | **29.98%** | **58.62%** | **20.31%** (13/64) | **100.00%** |
| **SV Ground State Prob.** | **6.47%** | **1.68%** | **0.86%** | **2.38%** | **1.56%** (1/64) | **7.69%** (1/13) |
| **Sampled Feasibility (10k)** | **73.70%** | **46.88%** | **29.96%** | **58.66%** | **20.31%** | **100.00%** |
| **Infeasible Samples (10k)** | 2,630 (26.3%) | 5,312 (53.1%) | 7,004 (70.0%) | 4,134 (41.3%) | 51/64 (79.69%) | 0 (0.0%) |
| **Sampled Opt Prob (10k)** | **6.93%** | **1.45%** | **0.94%** | **2.42%** | **1.56%** | **7.69%** |
| **Optimum Hits / 10k** | 693 | 145 | 94 | 242 | ~156 expected | ~769 expected |
| **Best Feasible Cost Found** | **13** | **13** | **13** | **13** | 13 | 13 |

---

## 5. Dual Baseline Analysis & Key Findings

1. **Impact of Hamiltonian Scaling and Controlled Step Size:**
   - In the unscaled setup, COBYLA stalled or hit iteration limits (`success=False`). With scaling ($S=28$) and `rhobeg=0.5`, COBYLA converged smoothly in all runs (`success=True`, 35–121 evaluations).
   - Feasibility rates improved substantially: in Run 1 ($p=1$, seed 10), feasibility reached **73.70%** (up from 29.65% unscaled, and more than 3.6× the uniform random rate of 20.31%).
2. **Comparison with Baseline A (Uniform Random Bitstrings):**
   - In Run 1, exact-optimum sampling probability reached **6.93%** (693 hits / 10k shots), a 4.4× enhancement over Baseline A (1.56%).
   - In Run 4 ($p=2$, seed 42), optimum sampling reached **2.42%** (vs 1.56% random).
   - However, in Run 2 (1.45%) and Run 3 (0.94%), optimum sampling fell below the 1.56% random threshold due to local trapping.
3. **Comparison with Baseline B (Uniform Sampling Over Feasible States):**
   - When conditioned on finding a feasible solution, picking uniformly at random among the 13 feasible states yields a **7.69%** chance of hitting the optimum.
   - Even in the best run (Run 1 at 6.93%), QAOA remains below Baseline B's 7.69% hit rate.
4. **Seed Sensitivity in Non-Convex Landscapes:**
   - The large variance across seeds ($0.86\%$ to $6.47\%$ exact statevector probability at $p=1$) demonstrates that standard transverse-field QAOA remains sensitive to initial parameter seeding.

---

## 6. Limitations & Scientific Honesty

1. **No Demonstration of Quantum Advantage:**
   - Brute-force classical enumeration evaluates all 64 states in under 0.5 milliseconds.
   - QAOA required dozens of variational evaluations and multiple seconds on a noiseless simulator, and even its best run did not surpass uniform sampling within the feasible subspace (6.93% vs 7.69%).
2. **Penalty Formulations vs. Constraint-Preserving Mixers:**
   - Unconstrained $X$-mixers must explore the full $2^n$ Hilbert space and rely on quadratic penalty terms ($P=40$) to enforce matching constraints. This creates rugged energy barriers.
   - Future extensions may investigate $XY$ or Dicke-state mixers that restrict evolution strictly to the feasible subspace.
3. **Physical Hardware Realities:**
   - These results were obtained on a noiseless statevector simulator. Physical QPUs would introduce gate noise, thermal relaxation, and readout errors, which would degrade feasibility and optimum hit rates.

---

## 7. Remaining Considerations for Future Dashboard Integration

If a Streamlit visualization dashboard is developed in subsequent milestones:
1. **Asynchronous Execution:** Statevector optimization requires several seconds per run; optimization should execute in a background thread or pull from pre-computed benchmark results to avoid freezing the UI.
2. **Transparent Terminology:** The dashboard must display the exact classical optimum as the authoritative ground truth and label QAOA as an exploratory heuristic.
3. **Accurate Cost Reporting:** Infeasible sample states must be explicitly flagged and must not have their penalized surrogate energies ($H + 60$) reported as physical response times.
4. **Input Boundary Enforcement:** Live QUBO generation should be capped to small fleets ($\le 12$ qubits) to prevent exponential simulation delays.
