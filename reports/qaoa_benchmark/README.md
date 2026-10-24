# QAOA benchmark on simulation-derived dispatch problems (Round 2, item 2)

All 23 instances are synthetic: they come from the simulated city in [../rolling_simulation](../rolling_simulation/README.md) or are constructed surge cases. None is taken from observed ambulance records.

**Question.** Round 1 ran QAOA on one hand-made 6-qubit scenario. How does it do on the problems PairCover-Q actually has to solve, at 4–12 qubits, against fair baselines, under noise, and inside the live simulation?

**Short answer.**
- **The starting point decides everything.** With a linear-ramp start and INTERP warm starts, depth-3 QAOA puts more probability on the exact optimum than guessing uniformly among valid assignments on 19 of 23 instances (median 2.2×; 4.4× at 10 qubits, 3.0× at 12). From random starting points it mostly does not.
- **Bigger penalties backfire.** Raising the constraint penalty buys feasibility and costs optimum probability.
- **Noise erodes the larger instances.** At 1% two-qubit error, 10–12 qubit instances lose roughly half or more of their advantage.
- **QAOA in the loop matches random sampling.** Inside the simulation it picks the exact optimum 99.6% of the time from 1,024 shots, but uniform random bitstrings do just as well at these sizes. It is a correct, validated drop-in solver, not a better one.
- No quantum advantage is claimed or shown. Everything is synthetic and simulated.

## Setup

**Instances** (frozen in [instances.json](instances.json) before any tuning). All are built with exactly the epoch model the simulation uses: λ = 5, τ = 20, 12-minute eligibility, one qubit per eligible ambulance–call pair.

| Family | Qubits | Count | Source |
|---|---|---|---|
| operational | 4, 5, 6, 7 | 2 each | decisions that actually occurred in the rolling simulation at 4 calls/hour |
| surge | 8, 10, 12 | 5 each | 2–5 simultaneous non-P1 calls with 4–7 idle units in a busy hour |

The surge family exists because, with the eligibility rule, real epochs are small (mean about 2 qubits, see [../rolling_simulation](../rolling_simulation/README.md)). Problems of 8 qubits or more only arise when several incidents coincide.

**QAOA**
- Standard X-mixer QAOA at depth p = 1, 2, 3, with the cost Hamiltonian scaled by its largest Ising coefficient.
- COBYLA on exact expectation values (`rhobeg` 0.5, up to 500 evaluations).
- The state is computed by `src/qrescue/quantum/qaoa_fast.py`. Tests check it against Qiskit's `QAOAAnsatz` amplitude by amplitude, and it reproduces the Round 1 audit figure of 6.47%.

**Starting points**
- **Ramp chain:** a linear ramp at p = 1, then INTERP (Zhou et al. 2020) from each depth's optimum to the next.
- **Control:** 20 random starts per depth.

**Penalty:** P0 = (provable bound) + 1, plus a sweep at 2·P0 and 4·P0 on the ramp chain.

**Ground truth:** exhaustive enumeration of the QUBO. On every instance the QUBO minimum is feasible and equals the exact assignment solver's optimum (asserted in the runner).

**Baselines**
- **Uniform over all bitstrings:** chance = number of optimal strings / 2^n.
- **Uniform over valid assignments ("uniform-feasible"):** chance = optimal / feasible. This is the bar that matters.

## Findings

Full per-instance tables are in [tables.md](tables.md). The figures are [fig_qaoa_vs_random.png](fig_qaoa_vs_random.png) and [fig_noise.png](fig_noise.png).

**1. Depth and initialisation.** Ramp chain, tight penalty; values are QAOA's probability of the optimum divided by the uniform-feasible chance.

| Qubits | p = 1 | p = 2 | p = 3 | Instances where p = 3 beats uniform-feasible | 20 random starts at p = 3 (median) |
|---|---|---|---|---|---|
| 4–7 (operational) | 0.20–0.73× | 0.78–2.0× | 1.2–2.3× | 6/8 | 0.49–1.03× |
| 8 (surge) | 0.80× | 1.09× | 2.37× | 4/5 | 0.49× |
| 10 (surge) | 0.82× | 1.85× | 4.38× | 5/5 | 1.14× |
| 12 (surge) | 0.49× | 1.07× | 3.01× | 4/5 | 0.18× |

- Depth 1 essentially never beats the uniform-feasible baseline. Depth 3 with a good start does.
- Random starts at 12 qubits beat the baseline in only 10% of runs, so reporting a lucky seed would badly overstate QAOA.
- One instance (surg-8q-10) is a clear failure: about 7% feasible samples and 0.01× at every depth.

**2. Penalty strength** (ramp chain, p = 3, medians over 23 instances).

| Penalty | Feasible samples | Probability of the optimum vs uniform-feasible | Beats uniform-feasible |
|---|---|---|---|
| tight (bound + 1) | 81% | 2.16× | 19/23 |
| 2× | 95% | 0.85× | 8/23 |
| 4× | 98% | 0.62× | 4/23 |

A larger penalty makes almost every sample valid, but flattens the differences between valid assignments, so the optimum gets harder to find. This confirms the Round 1 guidance to keep the penalty just above the provable bound.

**3. Noise and hardware routing** (ramp angles at p = 1–2; a generic depolarising and readout noise model, not a calibration of any specific IBM device).

- **Routing cost:** onto IBM's heavy-hex layout, two-qubit gate counts grow 1.4–2.3×. At 12 qubits and p = 2 that is 307–317 CZ gates, up from 140.
- **Robust:** small operational instances keep most of their advantage at 1% two-qubit error.
- **Eroded:** the best 10-qubit instance falls from 3.8× to 1.9× (all-to-all), and to about 1.2× with the heavy-hex-equivalent error. 12-qubit instances fall below the uniform-feasible bar.
- **Approximation:** the heavy-hex numbers raise the two-qubit error to match the routed circuit's total gate count; they are not a simulation of the routed circuit itself.
- **Caveat:** noise was studied at p ≤ 2, so the stronger p = 3 results have not yet been tested under noise.

**4. QAOA in the loop** (PairCover-Q, λ = 5, p = 2, 1,024 shots per decision; 6 simulated weeks at 4–5 calls/hour; 3,271 decisions).

- **Most decisions need no quantum step.** 1,875 decisions had at most one QUBO variable, and 36 needed a unit beyond the threshold, which is outside the QUBO. Both were solved exactly.
- **The remaining 1,360 decisions ran QAOA.** Best valid sample from 1,024 shots, checked against the exact optimum:

  | Method | Picked the exact optimum |
  |---|---|
  | QAOA, best of 1,024 shots | 1,355 / 1,360 (4 fell back to the exact solver) |
  | Uniform random bitstrings, best of 1,024 shots | 1,360 / 1,360 |
  | QAOA's single most likely bitstring | 950 / 1,360 (70%) |

  Average probability of the optimum per decision: QAOA 44–60%, uniform over all bitstrings 14–25%.
- **Simulation outcomes are unchanged.** Mean response is identical to the exact-solver run in 5 of 6 replications, and within 0.2 minutes in the sixth.

QAOA works as a validated drop-in solver, and the circuit genuinely concentrates probability on the optimum. But at these sizes, taking the best of 1,024 shots is something random guessing also achieves. The in-loop "99.6%" must never be shown without the random column next to it.

## What we can and cannot claim

**Can claim:**
- A tested QAOA pipeline solves real PairCover-Q dispatch subproblems inside a live simulation, with every answer validated and an exact fallback that was rarely needed (4 in 1,360).
- With a good starting strategy, depth-3 QAOA concentrates 2–4× more probability on the exact optimum than uniform guessing among valid assignments, on most 8–12 qubit surge instances.

**Cannot claim:**
- That QAOA is faster or better than classical solving. Exact enumeration of these problems is instant.
- That it would work as well on hardware. Noise and routing erode the larger instances.
- That the in-loop success shows quantum benefit. Random sampling does equally well.

## Limitations

- **Small samples:** 23 instances, 2–5 per size. The surge family comes from a synthetic generator, not observed data.
- **Ideal results:** noiseless results use exact expectation values, meaning infinitely many shots during optimisation.
- **Noise study coverage:** the noise model is generic, depths stop at p ≤ 2, and heavy-hex results are an error-rate approximation, not a routed-circuit simulation.
- **One mixer only:** only the standard X mixer was tested. Feasibility-preserving mixers (XY or Dicke-state) are the obvious next experiment, given that 20–40% of samples are infeasible.

## Reproduce

```bash
python scripts/run_qaoa_benchmark.py     # ~20 min; --quick for a smoke run
python scripts/run_qaoa_noise.py         # ~3 min, needs results.json
python scripts/run_qaoa_in_loop.py       # ~12 min
python scripts/report_qaoa_benchmark.py  # figures + tables.md
pytest tests/test_qaoa_fast.py tests/test_qaoa_loop.py -o pythonpath=src
```
