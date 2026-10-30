# Mentor session 2: talking points (Team Evric, 29 Oct 2026)

Mentor: Sreenivas Ramakrishnan (Qiskit Advocate), via POC Divya Sharma. Aim for 20–30 minutes: 5 to report, 5 to demo, the rest for his feedback.

## 1. What you asked for, and what we did (2 min)

| Your input in session 1 | What we did |
|---|---|
| Show classical vs quantum side by side | New **Classical vs Quantum** page: one dispatch problem solved by nearest-available, exact search, the QAOA simulator and the real IBM chip, with answers, hit rates and timings |
| Run on IBM hardware | **6 jobs on `ibm_fez`** (IBM Heron r2, 156 qubits): 3 raw, 3 with error mitigation, 4,096 shots per circuit |
| Qubits, latency, efficiency | Each row shows qubits, two-qubit gates and depth after mapping onto the chip, queue time, processing time and time on the chip |
| Improve the workflow / demo | Demo now runs: Home (22 → 13), then Classical vs Quantum, then Create your own emergency |

## 2. Live demo (3–4 min)

1. Home: "See the decision in one click". Nearest-available costs 22, PairCover-Q costs 13.
2. Quantum → Classical vs Quantum, **4 qubits · depth 2**: the timing cards, the table, the bar chart with error bars.
3. Switch to **6 qubits · depth 2**: the chip is only around guessing, and nearest-available picks a worse plan than exact.

## 3. Results to state (1 min)

- **4 qubits, depth 2:** the best dispatch was the chip's most frequent answer in all 6 runs. It hit the optimum in 46–49% of shots in the evening session: about 2.4× guessing among valid plans (20%), and about 80% of the noiseless 59%.
- **Drift:** the first run, two hours earlier on the same qubits, gave 28%.
- **Mitigation:** readout correction gave +1 point (readout error is about 1%). Dynamical decoupling with gate and measurement twirling gave −2 points against raw runs from the same session.
- **6 qubits (82 two-qubit gates):** 5–10% against 6.7% for guessing. The gain is marginal and unreliable.
- **Latency:** classical under 1 ms; hardware 12–20 minutes per job, mostly queue; 3–5 s on the chip. We used 45 s of the 600 s monthly allowance.
- **Our reading:** two-qubit gate noise is the limit, not readout.

## 4. Questions for the mentor (the main value of this session)

1. **Mitigation:** is zero-noise extrapolation (for example through the Estimator, or by folding gates) the right next step for two-qubit gate error, or should we cut circuit depth first?
2. **Drift:** how should we present a 20-point swing between runs? Is the mean with a range across runs the right way, or should we report each session separately?
3. **Above-noiseless results:** at 4 qubits depth 1, and sometimes at 6 qubits, the chip beats the noiseless circuit. We think relaxation favours sparse bitstrings. Is that explanation sound?
4. **Story:** our honest line is "quantum helps at 4 qubits on real hardware, fades by 6; no advantage claimed". Is this strong enough for the finale, or how would you frame the scaling story?
5. **Feasibility:** only 45–71% of hardware samples are valid plans. Is an XY or Dicke mixer worth mentioning as the main roadmap item, or something else?
6. **Finale format:** what do judges weigh most: live demo, slides or Q&A? Should we bring a separate slide deck, or present from the app?
7. **Awards:** do we fit the Quantum Impact Award better than the Innovation Award? What would strengthen the impact case?
8. **Anything missing** that a Qiskit Advocate would expect to see?

## 5. Before the call

- The app is open on Classical vs Quantum, 4 qubits · depth 2 selected.
- `reports/ibm_hardware/README.md` is open in a second tab.
- One person presents and one takes notes. Write down every suggestion with who will do it and by when.
- Today is the sprint deadline: ask the POC what exactly must be submitted and in what format.
