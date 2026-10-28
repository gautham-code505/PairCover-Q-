# QAOA on IBM quantum hardware (Round 2, mentor follow-up)

Runs benchmark circuits from [../qaoa_benchmark](../qaoa_benchmark/README.md) on IBM backends: the same frozen instances, with the noiseless ramp-chain angles at the tight penalty. Nothing is re-tuned on the device. Each result file puts four things side by side for one dispatch problem:

- the exact classical answer and how long it took
- the noiseless probability of the optimum
- the probability measured on the backend
- the random baselines

Script: [scripts/run_ibm_hardware.py](../../scripts/run_ibm_hardware.py). It needs `pip install -r requirements-hardware.txt`; the app itself does not.

## Short answer

- **QAOA ran on a real 156-qubit IBM Heron processor (`ibm_fez`, job `dbh0tjpt9uhs73c960mg`, 28 Oct 2026).**
- On the 4-qubit dispatch problem at depth 2, the device's most frequent outcome is the optimal dispatch (A3 → C1), the same answer as the classical solver.
- The device found the optimum 27.7% of the time:
  - 59.2% noiseless
  - 20.0% when guessing among valid assignments
  - 6.25% when guessing any bitstring
- Noise roughly halves the noiseless advantage. At 6 qubits (82 two-qubit gates after routing) the device does **worse than guessing** among valid assignments.
- The exact classical answer takes under 0.1 ms. The hardware path took about 12.5 minutes end to end, of which 3.2 s was circuit time on the chip. No quantum advantage is claimed.

## Results, 4,096 shots per circuit

P(opt) is the probability of sampling the exact optimum.

| Instance | Qubits | p | 2q gates / depth on chip | P(opt) noiseless | P(opt) FakeTorino | P(opt) FakeFez | **P(opt) real ibm_fez** | Uniform-feasible | Uniform-all | Most frequent outcome optimal on ibm_fez? |
|---|---|---|---|---|---|---|---|---|---|---|
| oper-4q-1 | 4 | 1 | 18 / 64 | 0.035 | 0.037 | 0.049 | **0.059** | 0.200 | 0.0625 | no |
| oper-4q-1 | 4 | 2 | 33 / 117 | 0.592 | 0.496 | 0.521 | **0.277** | 0.200 | 0.0625 | **yes** |
| oper-6q-5 | 6 | 2 | 82 / 177 | 0.092 | 0.073 | 0.074 | **0.052** | 0.067 | 0.0156 | no |

**Valid (feasible) samples, oper-4q-1 at p = 2:** 83% noiseless, 76% on FakeFez, 45% on real `ibm_fez`. Noise pushes samples into invalid assignments, such as one ambulance sent to two calls.

**Fake vs real.** Fake backends replay a calibration snapshot. On the same device the real chip did markedly worse (0.277 vs 0.521), because of drift since the snapshot, crosstalk and other effects a simple noise model leaves out. Treat fake-backend numbers as optimistic.

## Latency, from the real job

| Stage | Time |
|---|---|
| Exact classical solve (enumerate 16 bitstrings) | < 0.1 ms |
| Queue on `ibm_fez` (open plan, 12 jobs ahead) | 169 s |
| From job start to result (compile, load, run, read out) | 580 s |
| Circuit execution on the chip, all 3 circuits × 4,096 shots | 3.2 s |
| QPU time billed | 5 s of the 600 s monthly allowance |

A real ambulance dispatch decision needs an answer in seconds. Today the hardware path is only for experiments and evidence, not for live dispatch.

## Limitations

1. **Small and synthetic.** 4–6 qubits from simulated instances. Classical enumeration solves them instantly, and does so up to roughly 25–30 qubits.
2. **Noise grows with circuit size.** Each extra depth layer or qubit adds two-qubit gates (33 at 4 qubits, 82 at 6), and the gain over guessing disappears by 6 qubits.
3. **No error mitigation yet.** Raw samples: no dynamical decoupling, no readout or twirling mitigation. These are the cheapest next improvements.
4. **Angles tuned in simulation.** The parameters are not re-optimised on the device. On-device or noise-aware tuning could recover some of the loss, at the cost of more QPU time.
5. **Invalid samples.** The X mixer lets the circuit leave the space of valid assignments, and noise makes that worse (45% valid). A feasibility-preserving (XY) mixer is the planned fix.
6. **Latency and quota.** Minutes of queue and processing against sub-millisecond classical solves, with 10 minutes of QPU time a month on the open plan.
7. **One run.** A single job on one day; device calibration changes daily. Repeated runs would give error bars.

## What it is useful for

- **Evidence that the pipeline is real.** The same QUBO the app builds runs end to end on IBM hardware, and the result is decoded back into a dispatch decision that matches the exact solver.
- **A measured noise budget.** We now know where hardware stops helping at today's error rates (between 4 and 6 qubits for this encoding). This tells the roadmap what has to improve: mitigation, XY mixer, shallower circuits.
- **An honest classical vs quantum comparison** for the demo, with the same problem, the same answer and the measured times side by side.
- **A baseline to track.** Rerun the same script on newer devices or with mitigation and compare against this file.

## Files

| File | Backend |
|---|---|
| `real_ibm_fez_dbh0tjpt.json` | Real IBM Quantum device `ibm_fez` (Heron r2, 156 qubits). |
| `fake_fez_*.json`, `fake_torino_*.json` | Local fake backends: noise from a calibration snapshot of the named device, run on Aer. No queue, no account. |
| `job_<id>.json` | Manifest written at submission. `--retrieve <id>` re-fetches and re-scores the job. |

## Running it again

1. Save an IBM Quantum Platform API key once on your own machine (never commit it):
   `python -c "from qiskit_ibm_runtime import QiskitRuntimeService as S; S.save_account(channel='ibm_quantum_platform', token='<API key>', set_as_default=True)"`
2. `python scripts/run_ibm_hardware.py --no-wait` submits to the least busy device and writes `job_<id>.json`. Add `--backend ibm_fez` to choose one.
3. `python scripts/run_ibm_hardware.py --retrieve <id>` scores the job once it's done.
