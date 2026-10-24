# Rolling dispatch simulation (Round 2, item 1)

**Question.** Round 1 showed that on one snapshot the coverage-aware assignment beats greedy (cost 13 vs 22). Does that survive a stream of calls over time, where ambulances leave, return and get reused?

**Short answer.** With a small coverage weight (λ = 5), PairCover-Q keeps measurably more of the region covered and never does worse than closest-idle dispatch on late arrivals or response time. Under heavy load it is clearly better. Most of that response-time gain comes from **assigning simultaneous calls together**, not from the coverage term. The coverage term's own contribution is lower uncovered demand at no detectable cost in punctuality. Larger coverage weights (λ ≥ 20, including the Round 1 default) and a classical single-call coverage rule both make arrivals later. Everything here is synthetic.

## Setup

| Item | Value |
|---|---|
| Region | 24 × 24 km, 36 zones of 4 km; dense centre, a town, sparse periphery ([fig_region.png](fig_region.png)) |
| Fleet | 7 ambulances at 6 stations; 2 hospitals |
| Travel | straight-line distance × 1.3 detour at 50 km/h |
| Calls | Poisson; priorities P1/P2/P3 = 25/35/40%, weights 3/2/1; on-scene time lognormal (mean 20 min); 85% transported; 15 min handover; unit returns to its station |
| Decisions | every 2 minutes (calls arriving together form a batch) |
| Coverage and late threshold | 12 minutes |
| Loads | 2, 3, 4, 5 calls per hour (5/h is close to saturation) |
| Replications | 30 × 7 simulated days per load; every policy sees the identical call stream |
| Held-out check | 30 fresh replications on seeds 5000–5029 for λ = 5 and 10 |

**Policies compared**

- **closest-idle**: each call, most urgent and then oldest first, gets the nearest idle unit. This is the reference.
- **coverage-single**: a classical rule in the spirit of Jagtenberg et al. (2017). Calls are handled one at a time; for non-P1 calls, among units arriving within 12 minutes, send the one whose departure leaves the least demand uncovered.
- **batch-no-coverage**: all pending calls are assigned together, minimising priority-weighted travel time. This is PairCover-Q with λ = 0, and it isolates what batching alone buys.
- **paircover-q (λ)**: the Round 1 objective solved exactly at every epoch, with the pairwise coverage term weighted by λ = 5, 10, 20 or 40.

**Rules shared by both coverage-aware policies**

- P1 calls always get the nearest unit.
- A unit is eligible only if it arrives within 12 minutes or is the nearest unit.
- No call waits while an ambulance is idle.

## Findings

All numbers are paired differences against closest-idle with 95% confidence intervals over 30 replications; negative is better. Full tables are in [tables.md](tables.md); the figure is [fig_paired_differences.png](fig_paired_differences.png).

1. **PairCover-Q at λ = 5 never did worse than closest-idle.** In both the main and the held-out seed sets, no load showed a significant increase in late arrivals or mean response time. Uncovered demand fell significantly at every load: by 0.17–0.67 points in the main run and 0.18–1.54 points on held-out seeds.

2. **Under heavy load, the gain is mostly from batching.** At 5 calls/hour with λ = 5:
   - mean response −2.15 min [−2.67, −1.63]
   - late arrivals −1.80 points [−2.31, −1.30]
   - P1 mean response −0.48 min [−0.72, −0.23]

   The held-out seeds give −2.18 min and −1.29 points. Batch assignment without coverage gets most of this (−2.18 min, −1.51 points), so these numbers should not be credited to the coverage term.

3. **What the coverage term adds on top of batching** (PairCover-Q minus batch-no-coverage):
   - At λ = 5: uncovered demand is lower at every load (−0.17 to −0.32 points). Late arrivals change by between −0.29 and +0.17 points, and no interval excludes zero.
   - At λ = 20 or 40: late arrivals rise significantly at 2–4 calls/hour, by up to +2.0 points.

   The trade-off curve is in [fig_lambda_tradeoff.png](fig_lambda_tradeoff.png).

4. **The single-call coverage rule hurts in this region.** Coverage-single adds 2.6–3.2 points of late arrivals at 2–4 calls/hour. It pays for coverage with a slower unit on almost every call, while the batch model only deviates from greedy when the coverage loss is worth it. This matches the mixed evidence in the literature: Jagtenberg et al. (2017) report fewer late arrivals but a higher mean response, and Lee (2011) found a preparedness rule worse than closest-available.

5. **P1 calls are protected.** No coverage-aware policy significantly slowed P1 responses at any load.

6. **The pairwise model is nearly exact, and the per-epoch QUBOs are small.**
   - The two-unit coverage term disagreed with the true coverage loss in at most 9 of about 18,000 decisions per load (under 0.1%).
   - Counting only eligible ambulance–call pairs (one qubit each), per-epoch QUBOs average 1.6–2.1 qubits. The 95th percentile is 3–5 and the maximum is 8–12, reached only under heavy load.
   - PairCover-Q's choice differed from greedy in 3–13% of decisions, rising with load.

   So in normal operation the quantum subproblem is tiny. Problems of 8 qubits or more appear only when several calls arrive together, which is why the QAOA benchmark (item 2) adds a separate family of multi-incident surge instances.

## What we can and cannot claim

**Can claim:**
- In a synthetic region, exact PairCover-Q dispatch with a small coverage weight reduces uncovered demand without measurably delaying anyone.
- Under heavy load it lowers mean response time and late arrivals versus closest-idle, mainly by assigning simultaneous calls together.

**Cannot claim:**
- That coverage-aware dispatch reduces late arrivals in general.
- That these effect sizes transfer to a real city.
- That λ = 5 is optimal anywhere but this region. It was chosen on the main seeds and only confirmed on one held-out set.

## Limitations

- **Region:** one synthetic region; results depend on the station layout and demand surface.
- **Operational simplifications:**
  - Travel times are deterministic.
  - Units always return to their home station and are never re-tasked en route.
  - All units are interchangeable: no ALS/BLS distinction.
- **2-minute decision epoch:** adds about 1 minute of queueing to every call under every policy, so it does not bias comparisons.
- **Coverage definition:** a zone counts as covered if any idle unit can reach its centroid within 12 minutes. This is deterministic coverage, not the probabilistic MEXCLP measure.
- **Simplified baseline:** coverage-single is our version of the idea in Jagtenberg et al. (2017), not their exact MEXCLP-based heuristic.
- **Exact solver:** every result uses the exact enumeration solver. QAOA has not yet been run inside the loop.

## Reproduce

```bash
python scripts/run_rolling_simulation.py                       # main run, ~4 min
python scripts/run_rolling_simulation.py --lambdas 5 10 --seed 5000 --out reports/rolling_simulation/results_holdout.json
python scripts/report_rolling_simulation.py                    # figures + tables.md
pytest tests/test_simulation.py -o pythonpath=src
```

Code: `src/qrescue/simulation/`. The modules are `region.py` (synthetic region and calls), `engine.py` (simulation loop and metrics), `policies.py` (the four policies) and `paircover.py` (epoch model, exact solver and the epoch QUBO).
