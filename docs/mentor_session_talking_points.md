# Mentor session: talking points (Team Evric, Q-HACK INDIA 2026)

Mentor: Sreenivas Ramakrishnan (Qiskit Advocate). All contact goes through the POC, Divya Sharma.

## 30-second opener
Q-Rescue decides which ambulance goes to which emergency when several calls arrive together. Sending the nearest unit to every call can strip a neighbourhood of backup. We write the trade-off between response time and remaining coverage as a QUBO (one qubit per ambulance-call pair), solve it with QAOA in Qiskit, and check every answer against an exact solver and random guessing.

## Demo order (about 4 minutes, updated 28 Oct after mentor feedback)
1. Landing page, "See the decision in one click": nearest-available costs 22, PairCover-Q costs 13, because A2 stays home.
2. **Quantum → Classical vs Quantum**: same problem solved by nearest-available, exact search, the QAOA simulator and the real IBM chip `ibm_fez`, with timings. Start on 4 qubits · depth 2, then switch to 6 qubits.
3. "Create your own emergency": the user builds a case and the solvers run live.
4. Evidence page: the 7-day simulation and the QAOA benchmark, with the hardware bullet.

## Numbers to have ready (all synthetic, all from the repo reports)
| Claim | Number | Source |
|---|---|---|
| Round 1 snapshot | cost 13 vs 22 (40.9% lower) | README section 2 |
| Rolling simulation, 5 calls/hour, lambda = 5 | mean response -2.15 min, 95% CI [-2.67, -1.63] | reports/rolling_simulation |
| Where that gain comes from | batching alone gives -2.18 min; coverage term adds lower uncovered demand | same |
| QAOA benchmark | depth-3 ramp/INTERP beats uniform-over-valid on 19 of 23 instances (median 2.2x, 4.4x at 10 qubits) | reports/qaoa_benchmark |
| From random starts | mostly does not beat the baseline | same |
| Noise | at 1% two-qubit error, 10-12 qubit instances lose about half or more of the gain | same |
| QAOA in the loop | exact optimum 1,355 / 1,360, but uniform random gets 1,360 / 1,360 | same |
| Real IBM hardware, 4 qubits, depth 2 | ibm_fez hits the optimum in 27.7% of shots (noiseless 59.2%, guessing among valid plans 20%); most frequent answer = best dispatch | reports/ibm_hardware |
| Real IBM hardware, 6 qubits, depth 2 | 5.2% vs 6.7% guessing: below the baseline (82 two-qubit gates after routing) | same |
| Latency | classical < 1 ms; ibm_fez 12.5 min end to end (2.8 min queue, 9.7 min processing, 3.2 s on the chip); 5 s of the free 600 s/month used | same |
| Job | ibm_fez (Heron r2, 156 qubits), job dbh0tjpt9uhs73c960mg, 28 Oct 2026, 4,096 shots per circuit | same |

## The honest framing (say this before they ask)
- No quantum advantage is claimed. Exact enumeration of these problems is instant.
- Most real dispatch decisions are tiny (mean about 2 qubits). Problems of 8+ qubits only appear when several calls coincide.
- QAOA is a validated drop-in solver whose circuit does concentrate probability on the optimum, but at these sizes random sampling matches it.
- On real IBM hardware the gain over guessing survives at 4 qubits and is gone by 6 qubits.
- The roadmap is about pushing that limit: error mitigation, a feasibility-preserving XY mixer, device-tuned angles, repeated runs, larger fleets.

## Questions to ask the mentor
1. 20-40% of samples are infeasible with the standard X mixer. Is an XY or Dicke-state mixer the right next experiment?
2. Our penalty is the provable bound + 1, and larger penalties lowered optimum probability. Is that consistent with what you see, or should we try another encoding?
3. Is there a fair way to claim a scaling story without a demonstrated advantage?
4. Is the quantum severity classifier (a variational classifier feeding the cost function) worth building before the sprint ends on 29 Oct, or should we polish what exists?
5. ~~Can we run a small instance on real IBM hardware before the finale?~~ Done on 28 Oct (ibm_fez). Follow-up: which error mitigation should we try first?
6. What would you want to see in the finale demo?

## Before the call
- Branch `rolling-simulation` is clean; all 137 tests pass.
- Start the app: `.\venv\Scripts\python.exe -m streamlit run app/main.py`
- Open `reports/qaoa_benchmark/README.md` in a second tab.
- One person presents, one takes notes.
