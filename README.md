# Q-Rescue: Quantum-Assisted Predictive Emergency Resource Allocation

[![Tests: Passing](https://img.shields.io/badge/pytest-53%20passed-brightgreen.svg)](tests/)
[![Qiskit: 2.5.2](https://img.shields.io/badge/Qiskit-2.5.2-blue.svg)](https://qiskit.org/)
[![Streamlit: 1.65.0](https://img.shields.io/badge/Streamlit-1.65.0-red.svg)](https://streamlit.io/)
[![Python: 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

**Q-Rescue** is an exploratory emergency response optimization project developed for **Q-HACK INDIA 2026**. It formulates multi-call ambulance dispatch under geographic coverage constraints as a Quadratic Unconstrained Binary Optimization (QUBO) problem, evaluated using the Quantum Approximate Optimization Algorithm (QAOA) in Qiskit alongside rigorous classical baselines.

---

## 1. Project Scope & The PairCover-Q Model

Standard ambulance dispatch rules (such as closest-idle dispatch) assign each emergency to its nearest available ambulance. However, in simultaneous-call scenarios, dispatching multiple units from neighboring stations can strip an entire district of its primary and secondary emergency coverage, leaving subsequent emergency calls vulnerable to delayed responses.

**PairCover-Q** formulates this trade-off as a static one-shot batch assignment problem:
- **Primary Objective:** Minimize priority-weighted travel response times and penalties for unserved calls.
- **Pairwise Residual Coverage:** Introduce a quadratic coupling penalty that activates if and only if two mutually backing ambulances in a shared geographic sector are dispatched simultaneously.
- **Formulation Elegance:** By expressing residual coverage through pairwise couplings across mutual backup pairs, the model captures the coverage externality in an exact quadratic form without requiring extra slack or auxiliary qubits.

---

## 2. Mathematical Validation & Classical Baselines

The repository implements and verifies two benchmark instances:
1. **5-Qubit Hand-Checkable Scenario (Scenario 1):** 2 ambulances, 3 calls, with exact analytical proof.
2. **6-Qubit PairCover-Q Scenario (Scenario 2):** 3 ambulances ($A1, A2, A3$), 2 calls ($C2, C3$), with a pre-assigned unit $A4$ dispatched to critical call $C1$.

### Scenario 2 Problem Parameters
- **Calls:** $C2$ (weight $w_2 = 2$), $C3$ (weight $w_3 = 1$).
- **Unserved Threshold:** $\tau = 20$ minutes ($U_2 = 40, U_3 = 20, \sum U = 60$).
- **Travel Times:**
  - $A1 \to C2: 4$, $A1 \to C3: 6$
  - $A2 \to C2: 5$, $A2 \to C3: 4$
  - $A3 \to C2: 12$, $A3 \to C3: 5$
- **Coverage Penalty:** $\lambda \cdot g_{12} = 10$ if both $A1$ and $A2$ are dispatched simultaneously.

### Benchmark Outcomes Across 64 Hilbert States

| Strategy | Selected Assignment | Response Time | Coverage Penalty | Total Cost | Feasible? |
|---|---|---|---|---|---|
| **Coverage-Aware Exact Optimum** | **$A1 \to C2, A3 \to C3$** | **13** | **0** | **13** | **Yes** |
| Coverage-Free Classical Optimum ($\lambda = 0$) | $A1 \to C2, A2 \to C3$ | 12 | 10 | 22 | Yes |
| Nearest-Available Greedy | $A1 \to C2, A2 \to C3$ | 12 | 10 | 22 | Yes |
| Alternative Feasible Dispatch | $A2 \to C2, A3 \to C3$ | 15 | 0 | 15 | Yes |
| Single-Unit Partial Dispatch | $A1 \to C2$ only | 28 | 0 | 28 | Yes |
| Null Dispatch (All unserved) | None | 60 | 0 | 60 | Yes |

**The Operational Trade-off:**  
The coverage-aware optimum deliberately accepts a 1-minute response delay on lower-priority call $C3$ ($A3$ arrives in 5 min instead of $A2$ in 4 min). By keeping $A2$ idle and stationed, it preserves regional coverage and avoids a 10-point penalty, yielding a net cost of **13** compared to **22** for greedy dispatch (+40.9% improvement).

---

## 3. QAOA Experimental Audit & Findings

The QAOA simulation was audited across three $p=1$ seeds and one $p=2$ execution using Qiskit's `StatevectorEstimator` and `StatevectorSampler` (10,000 shots).

### Audited Configurations & Results (Scenario 2, 6 Qubits)

- **Hamiltonian Scaling:** $H_{\text{scaled}} = H / 28.0$ (scaled by $\max |c_i|$).
- **Optimizer:** COBYLA with initial step size $\text{rhobeg} = 0.5$, $\beta \in [0, \pi]$, $\gamma \in [0, 2\pi]$.
- **Baselines:**
  - *Baseline A (Uniform Random across all 64 states):* Feasibility rate **20.31%** (13/64), Optimum recovery **1.56%** (1/64).
  - *Baseline B (Uniform Random over feasible states):* Optimum recovery **7.69%** (1/13).

| Run Configuration | Evaluations (COBYLA) | Optimizer Status | Feasible Rate (Statevector / Sampled) | Optimum Recovery (Statevector / Sampled) | Optimum Hits (10,000 shots) | Best Feasible Cost Found |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$p=1$, Seed 10** | 35 | Converged (`success=True`) | 73.41% / **73.70%** | 6.47% / **6.93%** (~6.8% at 1k shots) | **693 / 10,000** | **13** |
| **$p=1$, Seed 42** | 42 | Converged (`success=True`) | 46.88% / **46.88%** | 1.68% / **1.45%** | **145 / 10,000** | **13** |
| **$p=1$, Seed 99** | 35 | Converged (`success=True`) | 29.98% / **29.96%** | 0.86% / **0.94%** | **94 / 10,000** | **13** |
| **$p=2$, Seed 42** | 121 | Converged (`success=True`) | 58.62% / **58.66%** | 2.38% / **2.42%** | **242 / 10,000** | **13** |

### Reading these figures: shot count and seed
- **6.8% and 6.93% are the same Seed 10 circuit.** COBYLA stops after 35 evaluations at the same angles either way. The app samples it with 1,000 shots (68 optimum hits, 720 feasible) and the audit with 10,000 shots (693 optimum hits, 7,370 feasible). Both estimate the exact statevector values of **6.47%** optimum and **73.41%** feasible, and both sit within sampling error of them.
- **The outcome depends heavily on the seed.** Seed 99 finds the optimum in 0.94% of shots (exact 0.86%), which is below the 1.56% uniform-random baseline, and Seed 42 at $p=1$ is at chance (exact 1.68%). Only Seed 10 is clearly above it.
- **Earlier versions of this README listed 0.94% under Seed 10.** With the current code that figure is reproduced by Seed 99 (94 / 10,000), not Seed 10. All four rows above were re-run and reproduced on 10 Oct 2026.
- **"Best Feasible Cost Found" is 13 in every row because it is the best of 10,000 samples.** Uniform random sampling would also contain the optimum at that shot count, so this column does not measure circuit quality. The optimum-recovery columns do.

---

## 4. Limitations & Absence of Quantum Advantage

In keeping with scientific integrity, the following limitations are explicitly stated:
1. **No Demonstrated Quantum Advantage:** Classical brute force enumerates all 64 configurations in under 1 millisecond. QAOA required dozens of variational iterations and several seconds on an unconstrained classical simulator without surpassing classical exact optimization.
2. **Rugged Penalty Landscape:** Enforcing matching constraints using quadratic penalties ($P = 40$) distorts the Hamiltonian energy landscape, creating local minima where classical gradient-free optimizers (COBYLA) can stall if unscaled.
3. **Hardware Considerations:** Physical quantum processing units (QPUs) would suffer from two-qubit gate errors and readout noise, which would further diminish ground-state sampling rates compared to ideal statevector simulation.
4. **Algorithmic Role:** QAOA serves as an exploratory proof-of-concept for formulating quadratic fleet dependencies. Operational dispatch decisions rely strictly on classical integer programming or exact solvers as ground truth.

---

## 5. Setup & Installation

### Prerequisites
- Python 3.10 – 3.13 (tested on Python 3.13.15 64-bit Windows)
- Git

### Installation
Clone the repository and install the verified dependencies:
```bash
git clone https://github.com/Sibi7Antony/Q-Rescue.git
cd Q-Rescue

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install exact pinned requirements
pip install -r requirements.txt
```

---

## 6. Execution Guide

### 1. Launch the Interactive Streamlit Web Console
Launch the full PairCover-Q emergency operations console:
```bash
streamlit run app/main.py
```
This serves the interactive application at `http://localhost:8501`, organized into four primary areas:
- **Dispatch Console:** Leading operational view with open emergency queue, unit availability, response zone topology chart (true distance geometry), candidate vs assigned routes, A1–A2 backup relationship capsule, run trigger, and "Why it changed" delta statement.
- **Quantum Lab:** Parameter configuration (depth $p$, seed, iterations, shots), execution status, optimizer convergence trace, top-10 measured bitstrings against the random guessing baseline, and circuit metrics.
- **Results and Benchmarks:** Cost ranking across all feasible plans with stacked response/coverage bars, and comprehensive multi-method performance comparison table.
- **Methodology:** Dispatch cost formulation, separation of dispatch cost vs QUBO energy vs expected energy $\langle H \rangle$, inputs matrix, and explicit synthetic data / no quantum advantage disclosure.

### 2. Run the Regression and Integration Test Suite
Run the 58 automated regression and integration tests covering the mathematical formulation, QAOA simulation, result adapter, geometry, and UI integration:
```bash
# Set PYTHONPATH to src and run pytest
pytest tests/ -v -o pythonpath=src
```

### 3. Run the QAOA Optimization Audit Script
Execute the multi-seed parameter optimization and sampling experiment:
```bash
python scripts/run_qaoa_scenario2.py
```
*(Ensure `PYTHONPATH=src` is set in your environment).*

### 4. Run the Interactive Jupyter Demonstration
Launch Jupyter to explore the step-by-step tutorial:
```bash
jupyter notebook notebooks/paircover_q_demo.ipynb
```

---

## 7. Repository Structure

```text
Q-Rescue/
├── README.md                           # Project overview, validation, and execution guide
├── requirements.txt                    # Pinned, reproducible project dependencies
├── qrescue_demo.ipynb                  # Interactive walkthrough notebook (root copy)
├── app/                                # Interactive Streamlit Application
│   ├── main.py                         # Application entrypoint (5 views, session state)
│   ├── result_adapter.py               # Adapter connecting backend to UI schema
│   ├── ui_components.py                # Reusable UI presentation components & charts
│   ├── ui_helpers.py                   # Pure Python data formatters & normalizers
│   └── README.md                       # Streamlit architecture documentation
├── docs/
│   ├── architecture.md                 # System architecture and formulation notes
│   ├── ui_ux_spec.md                   # Complete UI/UX design specification
│   └── ui_integration_note.md          # Interface contract between backend and UI
├── notebooks/
│   └── paircover_q_demo.ipynb          # Runnable demonstration notebook with saved outputs
├── reports/
│   ├── experiment_results.md           # Full QAOA audit report with exact benchmark tables
│   └── Q Rescue quantum dispatch...md  # Initial research validation and literature review
├── scripts/
│   ├── run_qaoa_scenario2.py           # QAOA simulation and multi-seed audit script
│   └── generate_notebook.py            # Automated notebook generator and runner
├── src/
│   └── qrescue/
│       ├── optimization/
│       │   ├── scenario.py             # 5-qubit scenario parameters
│       │   ├── scenario2.py            # 6-qubit PairCover-Q scenario implementation
│       │   ├── qubo.py                 # QUBO energy evaluation
│       │   └── brute_force.py          # Classical enumeration solver
│       ├── quantum/
│       │   └── ising.py                # QUBO-to-Ising mapping and Pauli operators
│       └── validation/
│           └── validator.py            # Hard-constraint feasibility validator
└── tests/
    ├── test_app_integration.py         # Full application & adapter integration tests (18 tests)
    ├── test_quantum.py                 # Basis-state ordering & QAOA smoke tests (2 tests)
    ├── test_qubo.py                    # 5-qubit QUBO and Ising equivalence tests (5 tests)
    ├── test_scenario2.py               # 6-qubit PairCover-Q exhaustive benchmark tests (10 tests)
    ├── test_ui_components_smoke.py     # UI components and view smoke tests (5 tests)
    └── test_ui_helpers.py              # Pure presentation helper tests (18 tests)
```
