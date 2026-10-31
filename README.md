# PairCover-Q: coverage-aware ambulance dispatch with QAOA on IBM quantum hardware

[![Tests: 149 passed](https://img.shields.io/badge/pytest-149%20passed-brightgreen.svg)](tests/)
[![Qiskit: 2.5.2](https://img.shields.io/badge/Qiskit-2.5.2-blue.svg)](https://www.ibm.com/quantum/qiskit)
[![Streamlit: 1.65.0](https://img.shields.io/badge/Streamlit-1.65.0-red.svg)](https://streamlit.io/)
[![Python: 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

Team Evric's project for **Q-HACK India 2026**, Track: Quantum Computing and Optimization.
Problem statement: *Quantum-Assisted Ambulance Allocation for Optimized Emergency Response.*

When several emergencies arrive at once, sending the nearest ambulance to each one can leave a whole neighbourhood without backup. PairCover-Q plans simultaneous calls together and penalises sending away two ambulances that cover the same area for each other. We write that trade-off as a QUBO, solve it with QAOA in Qiskit, check every answer against an exact classical solver and random guessing, and have run it on real IBM quantum computers.

**No quantum advantage is claimed.** At these problem sizes an exact classical search is faster. What we show is a complete, validated pipeline from an emergency to a real quantum chip and back to a correct dispatch decision, and a measured boundary of where today's hardware helps.

---

## Results at a glance

| Study | Result | Details |
|---|---|---|
| Round 1 example (6 qubits, all 64 plans checked) | Our optimum costs **13** vs **22** for nearest-available (41% lower) | [reports/experiment_results.md](reports/experiment_results.md) |
| 7-day simulated city (24 × 24 km, 7 ambulances, 30 runs per load) | At 5 calls/hour: mean response **−2.15 min** (95% CI −2.67 to −1.63), late arrivals **−1.8 points**, less uncovered demand at all 4 loads | [reports/rolling_simulation](reports/rolling_simulation/README.md) |
| QAOA benchmark, 23 problems of 4–12 qubits (simulated) | Depth-3 QAOA beats guessing among valid plans on **19 of 23** (median 2.2×) | [reports/qaoa_benchmark](reports/qaoa_benchmark/README.md) |
| Real IBM hardware: `ibm_fez`, `ibm_marrakesh` (IBM Heron, 156 qubits), 9 jobs | Best dispatch found up to **2.8×** more often than guessing (4 qubits) and **2.7×** at 10 qubits; below guessing at 7–8 qubits | [reports/ibm_hardware](reports/ibm_hardware/README.md) |
| Latency | Exact classical < 1 ms; one hardware job 11 s (empty queue) to 20 min (busy queue), of which 3–5 s on the chip | [reports/ibm_hardware](reports/ibm_hardware/README.md) |

All data is synthetic and labelled as such; no real ambulance records are used.

---

## How it works

1. **Calls arrive:** waiting calls, free ambulances and travel minutes.
2. **QUBO:** one binary variable xᵤⱼ per eligible ambulance–call pair (the unit arrives within 12 minutes, or it is the nearest), so one qubit per decision.
3. **QAOA circuit** in Qiskit: X-mixer QAOA at depth 1–3, linear-ramp start with INTERP warm starts, COBYLA.
4. **Run:** exact statevector simulator, IBM fake backends, or real IBM hardware through Qiskit Runtime.
5. **Check:** decode every bitstring to a dispatch plan and grade it against the exact solver, nearest-available and random guessing.

The cost minimised is

```
F(x) = Σ wⱼ tᵤⱼ xᵤⱼ  +  Σ Uⱼ (1 − Σᵤ xᵤⱼ)  +  λ Σᵤ cᵤ yᵤ  +  λ Σ g(a,b) y(a) y(b),     yᵤ = Σⱼ xᵤⱼ
```

priority-weighted travel, a penalty Uⱼ per unserved call, and coverage lost when units leave, including the pairwise term when two backup partners both leave. That term is a product of two binary variables, so coverage fits the QUBO with no extra qubits. One-to-one constraints enter as a penalty P = max(Uⱼ − wⱼ tᵤⱼ) + 1, the smallest value that provably makes every QUBO minimum a valid plan. Substituting xₖ = (1 − Zₖ)/2 gives the Ising Hamiltonian QAOA runs. Details: [docs/architecture.md](docs/architecture.md).

---

## The app

`streamlit run app/main.py` serves a multi-page web app:

| Page | What it shows |
|---|---|
| Home | The 22 → 13 replay and the headline hardware result |
| Dispatch console | Calls, ambulances, the response zone; run nearest, exact and QAOA |
| Create your own emergency | Place calls on a map; every solver runs live |
| Classical vs Quantum | One problem solved by nearest, exact, the QAOA simulator and real IBM chips, with answers, hit rates, gate counts and timings, plus a hardware scaling chart |
| Quantum Lab | QAOA settings, optimiser trace, measured plans vs guessing |
| Compare runs | Every run of the session side by side |
| Evidence | The 7-day simulation and the QAOA benchmark |
| Method & data | The formulation and the data disclosure |

---

## Quick start

```bash
git clone https://github.com/gautham-code505/PairCover-Q-.git
cd PairCover-Q-
python -m venv venv
# Windows: .\venv\Scripts\activate      Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

streamlit run app/main.py                 # the web app
pytest tests/ -o pythonpath=src           # 149 tests
```

### Reproducing the results

| Command | What it does |
|---|---|
| `python scripts/run_qaoa_scenario2.py` | Round 1 QAOA audit on the 6-qubit example |
| `python scripts/run_rolling_simulation.py` then `report_rolling_simulation.py` | 7-day simulated city (about 4 min; `--quick` for a smoke run) |
| `python scripts/run_qaoa_benchmark.py`, `run_qaoa_noise.py`, `run_qaoa_in_loop.py`, `report_qaoa_benchmark.py` | QAOA benchmark, noise study, QAOA inside the simulation |
| `python scripts/run_ibm_hardware.py --fake FakeFez` | Benchmark circuits on an IBM fake backend (no account needed) |
| `python scripts/run_ibm_hardware.py --backend ibm_fez [--mitigate] --no-wait` | Same circuits on real IBM hardware; needs `pip install -r requirements-hardware.txt` and your own IBM Quantum account saved locally (never commit the API key) |

Set `PYTHONPATH=src` when running scripts directly.

---

## Repository structure

```text
app/                 Streamlit app (main.py, pages in app_pages/, hardware_compare.py for Classical vs Quantum)
src/qrescue/         QUBO and solvers (optimization/), rolling simulation (simulation/), QAOA (quantum/), validation/
scripts/             Experiment and report scripts, including run_ibm_hardware.py
reports/             Write-ups and raw results: experiment_results.md, rolling_simulation/, qaoa_benchmark/, ibm_hardware/
tests/               149 automated tests
docs/                Architecture, data provenance, design notes, mentor-session notes, presentation speech
presentation/        Round 1 deck, Round 2 deck on the Q-HACK template, speaker script
notebooks/           Runnable demo notebook
research_notes/      Background research: literature, India EMS context, QUBO and QAOA notes
```

---

## Limitations

- **No quantum advantage.** Exact search solves every problem here in under a millisecond, and stays practical up to roughly 25–30 qubits.
- **Synthetic data.** The city, calls and ambulances are generated. A pilot would need real 108 call logs, such as Tamil Nadu's TNHSP research dataset.
- **Hardware noise.** The gain over guessing holds at 4–5 and 10 qubits but not at 7–8. Readout correction added about 1 point; dynamical decoupling with twirling did not help. Results drifted from 28% to 48% within two hours on the same qubits.
- **Invalid samples.** The standard X mixer lets circuits leave the valid space (45–71% valid on hardware); a feasibility-preserving XY mixer is on the roadmap.

---

## Team Evric

Team lead: **Gautham M A**. Members: **Divya**, **Harsha**, **Jayasuriya**.
Mentor: Sreenivas Ramakrishnan (Qiskit Advocate), Q-HACK India 2026.

---

## Acknowledgements and references

Built with [Qiskit](https://www.ibm.com/quantum/qiskit), [Qiskit Aer](https://github.com/Qiskit/qiskit-aer), [Qiskit IBM Runtime](https://github.com/Qiskit/qiskit-ibm-runtime), [Streamlit](https://streamlit.io/), NumPy, SciPy, Plotly and Matplotlib. Hardware runs used the IBM Quantum Platform open plan.

1. Farhi, Goldstone, Gutmann (2014), *A Quantum Approximate Optimization Algorithm*, [arXiv:1411.4028](https://arxiv.org/abs/1411.4028).
2. Zhou, Wang, Choi, Pichler, Lukin (2020), *QAOA: performance, mechanism, and implementation on near-term devices*, PRX 10, 021067, [arXiv:1812.01041](https://arxiv.org/abs/1812.01041) (INTERP initialisation).
3. Lucas (2014), *Ising formulations of many NP problems*, [arXiv:1302.5843](https://arxiv.org/abs/1302.5843).
4. Glover, Kochenberger, Du (2018), *A tutorial on formulating and using QUBO models*, [arXiv:1811.11538](https://arxiv.org/abs/1811.11538).
5. Jagtenberg, Bhulai, van der Mei (2017), *Dynamic ambulance dispatching: is the closest-idle policy always optimal?*, [doi:10.1007/s10729-016-9368-0](https://doi.org/10.1007/s10729-016-9368-0).
6. Cumming and Thomas (2022), *Using a quantum computer to solve a real-world problem* (ambulance location with QAOA), [arXiv:2211.13080](https://arxiv.org/abs/2211.13080).
7. TNHSP, [108 Ambulance research dataset](https://www.tnhsp.org/pages/view/108_Application) (Tamil Nadu).
8. ETV Bharat (June 2026), [National Ambulance Services guidelines 2026](https://www.etvbharat.com/en/bharat/national-ambulance-services-guidelines-2026-set-uniform-standards-for-emergency-care-across-india-enn26062906951); MoHFW, [ambulance norms](https://mohfw.gov.in/press-info/8546).

Further sources for the background research are listed in [research_notes/](research_notes/).

---

## Use of AI tools

We used AI coding assistants for parts of the code, documentation and presentation material. All design decisions, experiments and results were reviewed, run and verified by the team; every number in this repository comes from code in this repository and can be reproduced with the commands above.

---

## License

[MIT](LICENSE) © 2026 Team Evric.
