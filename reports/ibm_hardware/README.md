# QAOA on IBM quantum hardware (Round 2, mentor follow-up)

Runs benchmark circuits from [../qaoa_benchmark](../qaoa_benchmark/README.md) on IBM backends: the same frozen instances, with the noiseless ramp-chain angles at the tight penalty. Nothing is re-tuned on the device. Each result file puts four things side by side for one dispatch problem:

- the exact classical answer and how long it took
- the noiseless probability of the optimum
- the probability measured on the backend
- the random baselines

Script: [scripts/run_ibm_hardware.py](../../scripts/run_ibm_hardware.py). It needs `pip install -r requirements-hardware.txt`; the app itself does not.

## Short answer

- **QAOA ran 6 times on a real 156-qubit IBM Heron processor** (`ibm_fez`, 28 Oct 2026): 3 raw jobs and 3 with error mitigation. All used the same physical qubits.
- **4 qubits, depth 2:** in every run the device's most frequent outcome is the optimal dispatch (A3 → C1), the same answer as the classical solver. The probability of the optimum per shot was:

  | Run | P(optimum) |
  |---|---|
  | Noiseless simulator | 59.2% |
  | `ibm_fez`, 5 jobs in the evening session, with or without mitigation | 45.5–48.9% |
  | `ibm_fez`, raw, first run two hours earlier | 27.7% |
  | Guessing among valid assignments | 20.0% |
  | Guessing any bitstring | 6.25% |

  So the chip is **2.3–2.4× better than guessing among valid plans**, and keeps about 80% of the noiseless value.
- **Across sizes** (depth 3, 30 Oct; see "Scaling across problem sizes" below): the chip beats guessing at 4, 5 and 10 qubits (2.8×, 1.1×, 2.7×), is about even at 6, and falls below at 7 and 8.
- **The device drifts.** The same circuit on the same qubits moved from 27.7% to 47.9% within two hours. A single run is not enough evidence.
- **6 qubits, depth 2:** 82 two-qubit gates after routing. Raw runs gave 5.2%, 10.1% and 10.0%, against 6.7% for guessing among valid plans. The most frequent outcome is never the optimum. The gain is marginal and not reliable at this size.
- **Mitigation barely helps here.**
  - Readout correction adds about +1 point at 4 qubits and +0.3 points at 6 qubits: readout errors on these qubits are only about 1%.
  - Dynamical decoupling plus gate and measurement twirling *lowered* the hit rate slightly against raw runs from the same session: −1.7 points at 4 qubits, −2.6 points at 6 qubits.
  - The remaining error is mostly two-qubit gate noise, which needs a different technique (zero-noise extrapolation, or shallower circuits).
- **Latency:** the exact classical answer takes under 1 ms. A hardware job took 12.5–20 minutes end to end, mostly queue. The circuits themselves ran for 3–5 s per job. No quantum advantage is claimed.

## Results: P(optimum) per shot, 4,096 shots per circuit

| Instance | Qubits | p | 2q gates / depth on chip | Noiseless | FakeFez | ibm_fez raw, 3 runs (mean, range) | + readout fix (2 runs) | + DD + twirling (3 runs) | + DD + twirling + readout (3 runs) | Uniform-feasible | Uniform-all |
|---|---|---|---|---|---|---|---|---|---|---|---|
| oper-4q-1 | 4 | 1 | 18 / 64 | 0.035 | 0.049 | 0.048 (0.039–0.059) | 0.039 | 0.043 | 0.041 | 0.200 | 0.0625 |
| oper-4q-1 | 4 | 2 | 33 / 117 | 0.592 | 0.521 | **0.411 (0.277–0.479)** | **0.488** | 0.461 | 0.475 | 0.200 | 0.0625 |
| oper-6q-5 | 6 | 2 | 82 / 177 | 0.092 | 0.074 | 0.084 (0.052–0.101) | 0.104 | 0.074 | 0.077 | 0.067 | 0.0156 |

The readout-fix column uses only the two raw jobs that carried calibration circuits. Both ran in the evening session, at a raw 0.478 for the 4-qubit case and 0.100 for the 6-qubit case. Compare mitigation against those numbers, not against the three-run mean, which includes the early outlier.

**Valid (feasible) samples, oper-4q-1 at p = 2:** 83% noiseless, 76% on FakeFez, 45% (first run) and 71% (evening runs) on `ibm_fez`. Noise pushes samples into invalid assignments, such as one ambulance sent to two calls.

**Above the noiseless value.** At 4 qubits, depth 1, and in some 6-qubit runs, the device's hit rate is *higher* than the noiseless circuit's. This is most likely a noise effect, not a quantum gain: qubits relaxing towards 0 favour bitstrings with few 1s, and these optimal dispatches have only one or two 1s.

**Fake vs real.** Fake backends replay a calibration snapshot. FakeFez (0.521) was close to the evening runs (0.46–0.49) but far from the first run (0.277). Treat fake-backend numbers as a best case for a device on a good day.

## Scaling across problem sizes (depth 3, 2 raw jobs, 30 Oct 2026)

The strongest benchmark problem at each size, at depth 3, the depth where the benchmark's noiseless gains are largest. Both jobs ran back to back (`real_ibm_fez_raw_dbi8*.json`). Gain = P(optimum) ÷ P(optimum) when guessing among valid plans.

| Instance | Qubits | 2q gates / depth on chip | Noiseless gain | ibm_fez P(opt), 2 runs | ibm_fez gain | Share of noiseless gain kept | Top answer optimal |
|---|---|---|---|---|---|---|---|
| oper-4q-1 | 4 | 52 / 180 | 4.05× | 0.555, 0.574 | **2.82×** | 70% | 2/2 |
| oper-5q-3 | 5 | 94 / 245 | 2.01× | 0.108, 0.117 | 1.13× | 56% | 2/2 |
| oper-6q-5 | 6 | 121 / 284 | 1.46× | 0.068, 0.076 | 1.08× | 74% | 0/2 |
| oper-7q-6 | 7 | 148 / 294 | 1.53× | 0.098, 0.102 | 0.85× | 56% | 0/2 |
| surg-8q-12 | 8 | 211 / 423 | 3.46× | 0.018, 0.013 | 0.84× | 24% | 0/2 |
| surg-10q-13 | 10 | 284 / 469 | 7.21× | 0.049, 0.053 | **2.68×** | 37% | 2/2 |

- The gain does not fade smoothly with size. Noise keeps 24–74% of the noiseless gain, generally less for longer circuits. The chip stays above guessing only where the noiseless gain is large: the 10-qubit problem starts at 7.2× and still ends at 2.7×.
- **Is it just relaxation bias?** We compared each result against a noise-only baseline: independent bits, each set to 1 at the rate the chip actually produced. The chip beat that baseline on every problem, by 1.5× at 4 qubits up to 7× at 10 qubits. Its samples concentrate on the best plan in a way per-qubit bias cannot explain.
- Depth 3 also improves the 4-qubit case over depth 2: 55.5–57.4% against 46–49%, despite 52 rather than 33 two-qubit gates.
- The exact classical solver still answers every one of these in under 0.5 ms.

## Mitigation used

- **Readout fix.** Every job from the second batch also measured all-0 and all-1 on the 7 physical qubits used. The per-qubit assignment matrices are inverted on the measured distribution (tensor-product model, clipped and renormalised). Measured readout errors were 0.0–2.0% per qubit.
- **DD + twirling** (`--mitigate`). IBM Runtime's dynamical decoupling (XpXm), plus gate and measurement twirling with 32 randomisations × 128 shots. Twirling turns coherent errors into random (Pauli) noise. Without an extrapolation step, that makes errors predictable rather than smaller.
- **Not tried:** zero-noise extrapolation, probabilistic error cancellation, or angle tuning on the device.

## Latency

| Stage | Time |
|---|---|
| Exact classical solve (enumerate 16 or 64 bitstrings) | < 1 ms |
| Queue on `ibm_fez` (open plan) | 2.8 min (first job), about 19 min (evening jobs) |
| From job start to result (compile, load, run, read out) | 9.7 min (first job), 0.6–1.2 min (evening jobs) |
| Circuit execution on the chip, per job | 3.2 s (3 circuits), 5.3 s (3 circuits + 2 calibrations) |
| QPU time billed, all 6 jobs on 28 Oct | 45 s of the 600 s monthly allowance |

A real ambulance dispatch decision needs an answer in seconds. Today the hardware path is only for experiments and evidence, not for live dispatch.

## Limitations

1. **Small and synthetic.** 4–6 qubits from simulated instances. Classical enumeration solves them instantly, and does so up to roughly 25–30 qubits.
2. **Noise grows with circuit size.** Each extra depth layer or qubit adds two-qubit gates (33 at 4 qubits, 82 at 6). By 6 qubits the gain over guessing is marginal and unreliable.
3. **Drift.** Results moved by 20 points within two hours on the same qubits. Six jobs on one device on one day give a range, not a distribution.
4. **Mitigation is limited.** Readout correction and DD + twirling were tried; neither addresses two-qubit gate error, which dominates here.
5. **Angles tuned in simulation.** The parameters are not re-optimised on the device. On-device or noise-aware tuning could recover some of the loss, at the cost of more QPU time.
6. **Invalid samples.** The X mixer lets the circuit leave the space of valid assignments, and noise makes that worse (45–71% valid). A feasibility-preserving (XY) mixer is the planned fix.
7. **Latency and quota.** Minutes to tens of minutes of queue and processing against sub-millisecond classical solves, with 10 minutes of QPU time a month on the open plan.

## What it is useful for

- **Evidence that the pipeline is real.** The same QUBO the app builds runs end to end on IBM hardware, and the result is decoded back into a dispatch decision that matches the exact solver.
- **A measured noise budget.** The gain over guessing holds at 4 qubits (33 two-qubit gates) and fades by 6 (82). Readout error is not the bottleneck; two-qubit gate error is. This points the roadmap at shallower circuits, an XY mixer and zero-noise extrapolation.
- **An honest classical vs quantum comparison** for the demo, with the same problem, the same answer and the measured times side by side.
- **A baseline to track.** Rerun the same script on newer devices, or with new mitigation, and compare against these files.

## Files

| File | What it is |
|---|---|
| `real_ibm_fez_dbh0tjpt.json` | First real job (raw, no calibration circuits), 15:16 UTC. |
| `real_ibm_fez_raw_*.json` | Raw jobs with readout calibration, evening session (about 17:23 UTC). |
| `real_ibm_fez_mit_*.json` | DD + twirling jobs with readout calibration, same session. |
| `fake_fez_*.json`, `fake_torino_*.json` | Local fake backends: noise from a calibration snapshot of the named device, run on Aer. No queue, no account. |
| `job_<id>.json` | Manifest written at submission. `--retrieve <id>` re-fetches and re-scores the job. |

## Running it again

1. Save an IBM Quantum Platform API key once on your own machine (never commit it):
   `python -c "from qiskit_ibm_runtime import QiskitRuntimeService as S; S.save_account(channel='ibm_quantum_platform', token='<API key>', set_as_default=True)"`
2. `python scripts/run_ibm_hardware.py --backend ibm_fez --no-wait` submits a raw job, and `--mitigate` adds DD + twirling. Each submission writes `job_<id>.json`.
3. `python scripts/run_ibm_hardware.py --retrieve <id>` scores the job once it's done.
