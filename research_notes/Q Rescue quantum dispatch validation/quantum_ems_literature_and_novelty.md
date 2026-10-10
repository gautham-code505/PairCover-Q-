# Quantum / quantum-annealing / quantum-inspired literature for ambulance dispatch and emergency resource allocation, and adversarial novelty test of "Q-Rescue"

Notes compiled 9 October 2026. Verification legend used throughout:
- **[FULL TEXT]** = I extracted and read the paper's PDF text in this session.
- **[ABSTRACT PAGE]** = I opened the arXiv / publisher / repository landing page; details beyond the abstract are not verified.
- **[README]** = I opened the GitHub repository page and read its README summary; code was not audited.
- **[SNIPPET]** = seen only in a search-engine result summary; treat as a lead, not a verified fact.
- **[NOT OPENED]** = well-known reference named in the brief that I did not open in this session; bibliographic details are from my background knowledge and must be checked before citing.

---

## 1. Has anyone formulated ambulance dispatch / assignment / location / EMS coverage as QUBO or Ising and solved it with QAOA, VQE, quantum annealing or quantum-inspired annealers?

### Takeaway
Yes for ambulance **location/deployment** (not call assignment): Cumming & Thomas (arXiv 2022) formulate a toy ambulance-location problem as a QUBO and solve it with QAOA (X and XY mixers), VQE on IBM hardware and D-Wave annealing; Chancellor, Cumming & Thomas (arXiv 2020) discuss quantum approaches to "ambulance dispatch" conceptually. I did **not find** a peer-reviewed or preprint paper that solves multi-ambulance-to-multi-call *dispatch assignment* with QAOA, but several hackathon-grade GitHub projects sit very close, including one already named "Q-Rescue".

### Cited Findings

**A. Cumming & Thomas (2022) — closest verified academic prior work [FULL TEXT]**
- Title: "Using a quantum computer to solve a real-world problem -- what can be achieved today?"; authors R. Cumming and T. Thomas; arXiv:2211.13080 (quant-ph), submitted 23 Nov 2022; 62 pages, 27 figures; no journal reference listed; **preprint, not peer-reviewed** as far as the arXiv page shows — [arXiv abs](https://arxiv.org/abs/2211.13080)
- The paper states its chosen use case is "ambulance location and dispatch": where a finite number of ambulances should be positioned in a geographical area. It then narrows explicitly to *location only*: placing a small number of ambulances on a grid to minimise aggregate (squared-Euclidean) journey distance from each location to its closest ambulance, described as a version of weighted set cover / facility location — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- It distinguishes strategic, tactical and operational levels and names the operational question "which ambulance service resources should be sent to a specific urgent incident?" as part of the wider ambulance problem, but does not formulate or solve that question — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- Encoding: one-hot; for m ambulances and n locations, variables for "ambulance l located at i" plus variables for "ambulance l serves location i", totalling 2nm qubits; domain-wall encoding discussed as a qubit-saving alternative. Constraints: total ambulances deployed equals number available; every destination served; only one ambulance serves any location. Constraints handled by penalty terms or by Dicke-state initialisation with XY mixers — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- Problem sizes (Table II and text): variant A = 1 ambulance, 5 locations, 5 qubits; variant B = 2 ambulances, 4 locations, 16 qubits (2 x 2 x 4); variant C = 2 ambulances, 8 locations, 8 qubits (relaxed distance metric); variant D = 1 ambulance, 17 locations, 17 qubits; variant E = 2 ambulances, 5 locations, 20 qubits. (The extracted table layout was jumbled; A, B, C and D are confirmed by the surrounding prose, E is read from the table only.) — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- QAOA results (simulator): XY mixer with Dicke initial state gave 100% feasible-state probability and probability of the lowest-cost state "close to 1" for the 5-location case at p = 3 and p = 5, versus 0.1–0.15 for the X mixer with a penalty term under the same conditions. For the 8-site, 2-ambulance instance the XY mixer explores 28 states versus 256 for the X mixer; with X mixer + penalty at p = 3 the ground-state weight was only 2.18x its weight in the initial state — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- They also propose a "3XY" mixer (three separate XY mixers reflecting the Hamming-weight constraints of the 4-location, 2-ambulance encoding) and test INTERP/EXTRAP parameter-seeding strategies as p increases; INTERP (Zhou et al.) worked well — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- Real hardware: gate-model hardware runs used **VQE, not QAOA**, on IBM Perth (7 qubits, QV 32) and IBM Guadalupe (16 qubits, QV 32), 13-parameter ansatz; on Perth the best two of 10 runs had solution-state probabilities of 2.4% and 45.6% after 100 iterations — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- Quantum annealing: D-Wave Advantage 4.1; on a 3 x 2 grid with 2 ambulances the best success probability was 0.031, ten times the worst (0.00325), and highly sensitive to penalty weight (penalty ratio > 1.6 gave much lower success). Problems up to an 8 x 8 grid could be embedded "albeit that no feasible solutions were found during our trial runs" — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- Classical baseline: D-Wave Ocean tabu search and simulated annealing for 2 ambulances on n x n grids; tabu found the optimum up to 9 x 9 (success rate falling to roughly 1 in 10,000 at 8 x 8), and not at 10 x 10 and above; simulated annealing failed even at 5 x 5. Note these are untailored heuristics, not an exact solver — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- Authors' conclusion (abstract): gate-based hardware needs much more scale and fidelity before commercially valuable use; annealing is closer but also needs more scale and connectivity — [arXiv abs](https://arxiv.org/abs/2211.13080)
- Internal inconsistency worth knowing: Table II defines Problem B as 2 ambulances / 4 locations, but the hardware section calls it "Problem B (5 locations, 2 ambulances)" — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- **Overlap with Q-Rescue:** same domain (ambulances), same toolchain class (QUBO, QAOA with penalty vs XY mixer, small instances, simulator, classical baselines). **Different decision:** static positioning of ambulances on a grid, with no emergency calls, no priorities, no eligibility, and no term for coverage lost after dispatch.

**B. Chancellor, Cumming & Thomas (2020) — conceptual precedent for quantum ambulance dispatch and for the "coverage hole" idea [FULL TEXT]**
- Title: "Toward a standardized methodology for constructing quantum computing use cases"; authors Nicholas Chancellor, Robert Cumming, Tim Thomas; arXiv:2006.05846 (cs.AI, quant-ph), submitted 10 June 2020; no journal listed; **preprint, conceptual/methodological, nothing implemented** — [arXiv abs](https://arxiv.org/abs/2006.05846)
- Uses "the ambulance dispatch problem" as its single worked use case, defined as deciding how to deploy assets (ambulances to motorcycles) to emergencies and assigning them locations so an area is effectively covered; objectives listed include minimising wait times and "optimal coverage of areas" — [arXiv PDF](https://arxiv.org/pdf/2006.05846)
- States that if the utility of an asset in an area is lower when similar assets are already nearby, the solution space grows exponentially and the problem is "likely to be hard to solve classically, at least at busy times" — an asset-interaction (quadratic) structure that is naturally QUBO/Ising-shaped — [arXiv PDF](https://arxiv.org/pdf/2006.05846)
- "Deployment 3" explicitly describes the coverage-aware dispatch rule: developing policies such as "sending the second closest asset to respond to an incident if sending the first closest would leave a 'hole' in the asset coverage", using Ising models as probabilistic graphical models for (conditional) sampling to inform dispatch policy offline — [arXiv PDF](https://arxiv.org/pdf/2006.05846)
- Judges full routing by direct optimisation on a near-term quantum computer infeasible (machine too small, data-intensive) and suggests quantum-inspired methods or sub-problems instead — [arXiv PDF](https://arxiv.org/pdf/2006.05846)
- **Overlap with Q-Rescue:** this is the nearest thing I found to the *idea* of coverage-aware ambulance dispatch in a quantum/Ising context, but it contains no QUBO, no QAOA, no experiment, and frames the quantum role as sampling for policy design rather than optimising a dispatch decision.

**C. Maximal covering location on quantum devices (generic, not EMS-specific)**
- Giraldo-Quintero, Lalinde-Pulido, Duque, Sierra-Sosa, "Using quantum computing to solve the maximal covering location problem", Computational Urban Science 2(1), article 43 (2022), DOI 10.1007/s43762-022-00070-x; peer-reviewed. Abstract: solves the Church–ReVelle MCLP on quantum computers; "promising results" but more qubits and less noise needed **[ABSTRACT PAGE]** — [journal page](https://journal.hep.com.cn/cus/EN/10.1007/s43762-022-00070-x)
- A secondary overview says this paper maps MCLP to both D-Wave annealing and IBM gate-based devices, ran QA and QAOA on real devices and simulators, and found annealing succeeded while gate-based faced more difficulty **[SNIPPET of secondary source; primary full text not read]** — [Quantum Computing in Logistics overview, arXiv:2402.17520](https://arxiv.org/pdf/2402.17520)
- Saavedra-Benavides, Montanez-Barrera, Maldonado-Romo, Sierra-Sosa, "A Hybrid Classical-Quantum Approach for Multi-Constrained Location Optimization Problem", arXiv:2607.16277 (8 July 2026), preprint: MCLP as QUBO with unbalanced penalization instead of slack variables, QAOA and warm-start QAOA, linear-ramp schedule; abstract claims the combination "consistently improves solution quality and feasibility metrics". No EMS framing visible in the abstract; instance sizes not in abstract **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2607.16277)
- Broesamle et al., arXiv:2602.10951 (Feb 2026): QUBO formulations for p-median, p-center, fixed-charge facility location and discrete ordered median, tested with QAOA, WS-QAOA and classical heuristics **[SNIPPET]** — [arXiv HTML](https://arxiv.org/html/2602.10951v1)

**D. Emergency / disaster-themed quantum work that is not ambulance dispatch**
- Cadeliña et al., "D-Wave Implementation of Quantum Annealing for Optimal Resource Allocation in Disaster Response Operation of Marikina City", ECTI-CIT 18(1):24–33 (2024), DOI 10.37936/ecti-cit.2024181.253577; peer-reviewed regional journal. Vehicle routing for disaster response via QUBO with D-Wave Leap and a Solution Partitioning Solver; whether QPU or hybrid solver, sizes and baselines are not on the landing page **[ABSTRACT PAGE]** — [journal page](https://ph01.tci-thaijo.org/index.php/ecticit/article/view/253577)
- Lee, Jeong, Kim, Seo, "Quantum-Based k-Coverage Optimization for UAV-Aided Search and Rescue Missions", arXiv:2609.01930 (1 Sep 2026), stated as accepted by IEEE Internet of Things Journal. Exact-penalty QUBO for 3-coverage waypoint selection, solved with QAOA on a noise-free simulator **and on IBM's 127-qubit Eagle processor**; campus-scale hardware runs reported 99.3% mean 3-coverage over ten runs with a 90% feasible-run rate **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2609.01930)
- "A Proposal for Optimal Emergency Vehicle Routing using Quantum Annealing", Vanderbilt Young Scientist Journal (student journal): BQM + Dijkstra routing proposal, run on a local simulator because annealer access was not sustained **[SNIPPET]** — [Vanderbilt YSJ](https://www.vanderbilt.edu/youngscientistjournal/article/a-proposal-for-optimal-emergency-vehicle-routing-using-quan-tum-annealing/)
- "A Quantum-Inspired Approach to Emergency Patient Allocation Using Digital Annealing" (IEEE Xplore document 10313617, reported as 2023): patient-to-hospital allocation by injury severity as a QUBO on a digital annealer, reported to outperform simulated annealing. The IEEE page returned no content to my fetch, so title and summary are **[SNIPPET]** only — [IEEE Xplore](https://ieeexplore.ieee.org/document/10313617/)
- Government pilot (news, not research): Andhra Pradesh Quantum Mission pilot in Guntur district covering 67 ambulances, using three years of call data to pre-position ambulances, to run on a Coherent Ising Machine being installed at the state data centre; four unnamed startups; no results reported (article dated 31 Aug 2026). This is placement plus routing guidance, not call-assignment logic, and a Coherent Ising Machine is not a gate-model device **[news article opened]** — [Gulte](https://www.gulte.com/political-news/429060/ap-brings-quantum-computing-to-ambulance-services)

**E. GitHub / hackathon projects (grey literature)**
- **Name collision / possible self-match:** `Sibi7Antony/Q-Rescue` — "Quantum Disaster Response & Coordination Platform"; Next.js + FastAPI digital twin with QUBO and QAOA-simulation endpoints; Qiskit, Qiskit Aer, Qiskit Optimization with "QAOA-inspired local simulation and graceful fallback"; example API call is a 4-variable `drone_allocation` problem at depth 2; default scenario includes 12 ambulances among other assets; README disclaims quantum advantage and operational use; 4 commits, no stated hackathon; no explicit objective or coverage term in the README **[README]** — [GitHub](https://github.com/Sibi7Antony/Q-Rescue)
- `Devsuthar2006/ambulance` ("RESQAI"): hackathon prototype built on an "Emergency Fleet Assignment with Coverage Preservation" engine. **Classical, no quantum.** Scoring rule = Euclidean distance + COVERAGE_PENALTY x (1 if vehicle is the last idle unit in its quadrant) / incident weight, with priority weighting so critical calls still get the nearest unit; benchmarked against nearest-unit greedy on 20 vehicles / 100 incidents **[README]** — [GitHub](https://github.com/Devsuthar2006/ambulance)
- `Amaan-Hans/Grid-Aware-Emergency-Resource-Allocation`: hackathon build; QUBO over load-shedding schedule solved with QAOA/VQE via qiskit-optimization, with a risk term reflecting ambulance response times; no results reported; many placeholders **[README]** — [GitHub](https://github.com/Amaan-Hans/Grid-Aware-Emergency-Resource-Allocation)
- Several near-identical student repos encode traffic signals as a ~16-variable QUBO solved by QAOA on Qiskit Aer with an "emergency green corridor" for ambulances (ambulance is a routing overlay, not an assignment variable) **[SNIPPET]** — [Q-TRAFFIC](https://github.com/Theshiya30/Q-TRAFFIC-Quantum-Urban-Traffic-Optimization)
- Egypt's first national quantum hackathon included a challenge to route an ambulance carrying five patients to hospital with quantum optimisation (a routing/TSP-type task) **[SNIPPET]** — [CERN Open Quantum Institute](https://open-quantum-institute.web.cern.ch/celebrating-egypts-first-ever-national-quantum-computing-hackathon/)
- "mediQal" (University of Michigan students, 2022): quantum-annealing-based routing for mobile medical services **[SNIPPET; page returned HTTP 403]** — [Michigan Engineering News](https://news.engin.umich.edu/2022/04/mentoring-for-the-greater-good/)

### Inferences
- The domain "ambulances + QUBO + QAOA" is **not virgin territory**: Cumming & Thomas already did QAOA (penalty vs XY mixer), VQE on hardware and D-Wave for an ambulance problem at 5–20 qubits. Any claim of "first quantum approach to ambulance optimisation" is false.
- The specific decision Q-Rescue models (several simultaneous prioritised calls assigned to several ambulances, with eligibility) was not found as a QAOA study. It is, however, structurally a small generalised-assignment QUBO, which is extensively covered in the generic quantum-optimisation literature (Section 2).
- The existence of a public repo also named "Q-Rescue" with QUBO/QAOA endpoints for disaster response is a practical risk: a judge who searches the name will find it. I could not determine whether it belongs to the same team. If it does, fine; if not, the name and theme are already taken.
- Emergency-themed QAOA hackathon projects are common in 2026; "quantum + ambulance" as a theme will not look original on its own.

### Gaps
- Giraldo-Quintero et al. full text (algorithms, instance sizes, qubits) was not accessible; do not cite numbers from it without reading the PDF.
- The IEEE digital-annealing patient-allocation paper could not be opened; authors, venue and exact year are unverified.
- IEEE Xplore, ACM DL, ScienceDirect and PubMed were reached only through general web search, not their native search interfaces; site-restricted queries did not appear to be honoured by the search tool. A paper indexed only there could have been missed.
- Google Scholar forward-citation chaining from Cumming & Thomas (2022) and Chancellor et al. (2020) was **not** performed; this is the single most valuable follow-up check.
- Non-English literature and theses were not searched.

---

## 2. Closely related quantum formulations a judge might cite (not the same problem)

### Takeaway
Q-Rescue's mathematical core (one-hot assignment with a quadratic interaction term) is a standard pattern with direct precedents in QAOA work on VRP, graph colouring, rostering, facility location, drone assignment and patient allocation. The ambulance framing is a domain re-skin of well-studied structure unless the coverage term is made the substantive contribution.

### Cited Findings
- **Vehicle routing, QAOA (the sizes Q-Rescue will be compared against):** Azad, Behera, Ahmed, Panigrahi, Farouk, "Solving Vehicle Routing Problem Using Quantum Approximate Optimization Algorithm", IEEE Trans. Intelligent Transportation Systems (2022), DOI 10.1109/TITS.2022.3172241, arXiv:2002.01351. VRP as Ising model, QAOA simulated in Qiskit; instances (n, k) = (4, 2), (5, 2), (5, 3) locations/vehicles; performance depends on classical optimiser, depth p, initialisation and instance. **Simulator only.** **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2002.01351)
- **Feasibility problem of penalty-QAOA for routing:** Xie, Lee, Cai, Saito, Asai, Lau, "A Feasibility-Preserved Quantum Approximate Solver for the Capacitated Vehicle Routing Problem", arXiv:2308.08785 (preprint): penalty-based QAOA "faces challenges in sampling solutions satisfying all constraints"; proposes constraint-preserving mixing **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2308.08785). A search summary reports a feasibility ratio of about 1 for their method versus 1.77e-5 for penalty QUBO-QAOA on the smallest instance **[SNIPPET — verify in the PDF before quoting]** — [arXiv PDF](https://arxiv.org/pdf/2308.08785)
- **VRP on gate hardware:** "Quantum-Assisted Vehicle Routing: Realizing QAOA-based Approach on Gate-Based Quantum Computer", arXiv:2505.01614 (2025) **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/2505.01614)
- **Harwood et al., "Formulating and Solving Routing Problems on Quantum Computers", IEEE Transactions on Quantum Engineering (2021)** — named in the brief; **[NOT OPENED]** in this session (the arXiv ID I tried resolved to a different paper). Verify at IEEE before citing.
- **One-hot assignment with XY mixers (graph colouring):** Wang, Rubin, Dominy, Rieffel, "XY-mixers: analytical and numerical results for QAOA", Phys. Rev. A 101, 012320 (2020), DOI 10.1103/PhysRevA.101.012320: XY mixers enforce one-hot hard constraints and "significantly outperform" the X mixer on graph-colouring benchmarks; W-state initial states outperform simpler ones **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/1904.09314)
- **Workforce / rostering:** Gupta & Hassan, "Constraint-Preserving QAOA for Personnel Rostering: Coverage-Preserving and Guarded-XY Mixer Constructions", arXiv:2607.09145 (July 2026, preprint): hard constraints embedded in the mixer; compares Penalty-X, Coverage-XY and guarded-XY; claims elimination of penalty calibration and better concentration on optimal feasible schedules under expectation and CVaR objectives **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2607.09145). Note "coverage" here means shift coverage, not geographic coverage.
- **Nurse scheduling on an annealer:** "Application of Quantum Annealing to Nurse Scheduling Problem" (arXiv:1904.12139), D-Wave 2000Q; probability of satisfying all constraints decays as schedule and roster grow **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/1904.12139)
- **Physician scheduling, QAOA on simulators and IBM hardware:** Chalmers master's thesis (2025), "Quantum Optimization of Physician Scheduling For Maximal Healthcare Capacity"; classical solvers consistently feasible, QAOA limited by hardware **[SNIPPET]; thesis** — [Chalmers ODR](https://odr.chalmers.se/items/02ae9e7a-c287-4a88-b8cf-bcf834f60925)
- **Hospital resources, quantum-inspired:** ICCS 2026 paper proposing a unified QUBO for operating-room scheduling, bed management and staff allocation, solved with neural-guided quantum-inspired simulated annealing (classical) **[SNIPPET]** — [ICCS 2026](https://www.iccs-meeting.org/archive/iccs2026/papers/167870188.pdf)
- **Patient-to-hospital allocation:** Tohoku University (Ohzeki's T-QARD group) announced a D-Wave-based model for allocating critically ill COVID-19 patients to hospitals, up to 10,000 variables via Leap 2; described as an initiative, no peer-reviewed results found **[SNIPPET]** — [Tohoku University](https://www.tohoku.ac.jp/en/news/research/quantum_technology_to_the_researchers.html). Plus the digital-annealing emergency patient allocation paper listed in Section 1 **[SNIPPET]** — [IEEE Xplore](https://ieeexplore.ieee.org/document/10313617/)
- **Facility location, QAOA:** Wang et al., arXiv:2312.06922, uncapacitated facility location with a QAOA+ variant **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/2312.06922v3); Classiq p-median example using CVaR-QAOA (vendor tutorial) **[SNIPPET]** — [Classiq docs](https://docs.classiq.io/latest/explore/applications/logistics/facility_location/facility_location); Calabria two-level facility location on D-Wave, underperforming for large instances **[SNIPPET]** — [Optimization Online](https://optimization-online.org/2024/07/quantum-annealing-for-the-two-level-facility-location-problem)
- **Drone / UAV assignment and dispatch:** drone delivery packing on D-Wave Advantage with Gurobi and SA baselines (arXiv:2406.08430) **[SNIPPET]** — [arXiv](https://arxiv.org/html/2406.08430v1); multi-UAV routing with a constrained XY-mixer QAOA preserving one-hot route assignment **[SNIPPET]** — [arXiv](https://www.arxiv.org/pdf/2409.18631); "Optimality-Preserving Decomposition for Scalable QAOA in Natural-Language-Guided Multi-Drone Assignment", arXiv:2606.14252 **[SNIPPET, title only]** — [arXiv](https://arxiv.org/pdf/2606.14252)
- **Mobility dispatch on an annealer:** 2026 preprint on micro-mobility dispatch building a QUBO from predicted travel times and historical distribution data **[SNIPPET]** — [arXiv:2601.20887](https://www.arxiv.org/pdf/2601.20887)
- **Traffic control:** "Quantum Annealing Approach for the Optimal Real-time Traffic Control using QUBO", arXiv:2403.09023 **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/2403.09023)
- **Disaster / evacuation / restoration:** survey "Quantum Artificial Intelligence for Mission-Critical Systems" (arXiv:2511.09884) summarising QUBO evacuation studies **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/2511.09884); "Quantum Computing for EVs to Enhance Grid Resilience and Disaster Relief" (arXiv:2511.00736) **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/2511.00736); quantum-inspired QUBO-assisted ALNS for hurricane restoration crews (arXiv:2607.29544) **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/2607.29544); a Devpost hackathon wildfire crew-deployment QAOA prototype with capacity and clustering penalties **[SNIPPET]** — [Devpost](https://devpost.com/software/superposition-seekers)

**How patient-to-hospital assignment differs from ambulance-to-emergency assignment (my analysis, not a cited claim):** see Inferences.

### Inferences
- **Patient→hospital vs ambulance→call.** (i) *Direction and resource:* patient allocation assigns demand (patients) to fixed-location capacitated facilities; ambulance dispatch assigns mobile, unit-capacity servers to demand points. (ii) *Constraint type:* hospital problems are dominated by knapsack-style capacity inequalities (beds, specialties), which need slack variables or unbalanced penalties; ambulance-to-call assignment at Q-Rescue's scale is dominated by one-hot equalities/at-most-one constraints on both sides (each call gets one ambulance, each ambulance at most one call), which are XY-mixer-friendly. (iii) *After-effect:* assigning a patient to a hospital consumes capacity at a place that does not move; dispatching an ambulance removes a server from a zone and changes the spatial coverage of future, not-yet-observed demand. That externality is what Q-Rescue's coverage term models, and it has no direct analogue in the patient-allocation QUBOs I saw. (iv) *Time-criticality:* dispatch is an online decision in seconds; patient allocation in the cited work is planning-level.
- A judge can fairly say "this is the linear/generalised assignment problem with a quadratic regulariser". With 3 ambulances x 4 calls the variable count is 12 (more with slack variables), i.e. the same scale as Azad et al.'s (4,2)–(5,3) VRP instances and Cumming & Thomas's 5–20 qubit instances.
- Because pure linear assignment is polynomial-time (Hungarian algorithm), the *only* part of Q-Rescue that makes the problem genuinely quadratic — and therefore a natural QUBO rather than a forced one — is the coverage interaction term. That is where any defensible contribution has to sit.

### Gaps
- I found no QAOA paper specifically on the generalised assignment problem or on ride-hailing/taxi matching in this search; they may well exist (search queries returned drone and routing work instead). "Not found in this search".
- Quadratic assignment problem (QAP) QAOA literature was not specifically retrieved.
- Harwood et al. not verified this session.

---

## 3. Has prior work combined (a) current call assignment with (b) a future-coverage / preparedness / post-dispatch availability term inside a QUBO, Ising or QAOA formulation?

### Takeaway
**Not found in this search.** The idea exists (i) conceptually in a quantum context (Chancellor et al. 2020, coverage "hole" dispatch policy via Ising sampling, not implemented), (ii) as mature classical operations research (preparedness-based dispatching/relocation), and (iii) in a classical hackathon repo with an explicit coverage-penalty dispatch rule; but I found no QUBO/QAOA implementation that puts both terms in one objective.

### Cited Findings
- Chancellor, Cumming & Thomas describe, in words, dispatching the second-closest asset when sending the closest "would leave a 'hole' in the asset coverage", and propose Ising-model sampling to inform such policies; there is no formulation or experiment **[FULL TEXT]** — [arXiv PDF](https://arxiv.org/pdf/2006.05846)
- Cumming & Thomas optimise positions only; their cost is aggregate distance to the closest ambulance with no calls and no post-dispatch term **[FULL TEXT]** — [arXiv PDF](https://arxiv.org/pdf/2211.13080)
- Classical precedent: "Integrating the ambulance dispatching and relocation problems to maximize system's preparedness" (Carvalho, Captivo, Marques; European Journal of Operational Research, 2020) integrates dispatching and relocation to maximise coverage under a preparedness definition, solved with a mathematical model and a pilot-method heuristic — no quantum method. Details are from a search summary; the ScienceDirect page returned HTTP 403 **[SNIPPET]** — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0377221719309683)
- Classical precedent, ADP: Schmid's dynamic ambulance relocation and dispatching via approximate dynamic programming **[SNIPPET]** — [ResearchGate listing](https://www.researchgate.net/publication/230846936_Solving_the_Dynamic_Ambulance_Relocation_and_Dispatching_Problem_using_Approximate_Dynamic_Programming)
- A 2025 survey-style preprint notes most EMS studies derive dispatching, redeployment and relocation policies for online settings, often as MDPs with approximate dynamic programming or deep RL **[SNIPPET]** — [arXiv:2503.11848](https://arxiv.org/pdf/2503.11848)
- Classical hackathon precedent with the same idea: RESQAI's coverage-aware policy penalises sending the last idle unit in a quadrant, scaled by incident priority; purely classical greedy scoring **[README]** — [GitHub](https://github.com/Devsuthar2006/ambulance)
- The other "Q-Rescue" repo exposes QUBO/QAOA endpoints for team/drone allocation but its README shows no coverage or preparedness term **[README]** — [GitHub](https://github.com/Sibi7Antony/Q-Rescue)

### Inferences
- The *concept* "do not strip a zone of its last ambulance" is decades-old in classical EMS research and is present in at least one 2026 hackathon repo. Q-Rescue cannot claim the concept.
- What appears unoccupied (in this search) is the narrow combination: *a single QUBO whose objective contains both priority-weighted response cost for simultaneous calls and a quadratic zone-coverage-loss term, solved with QAOA and compared with greedy and exact baselines*. This is a formulation-level gap, not an algorithmic or performance gap.
- The gap is plausibly unoccupied because it is small and of limited scientific interest at toy scale, not because it is hard. That should temper how it is described.
- A coverage-loss term is genuinely quadratic when it depends on *pairs* of ambulances leaving the same zone (e.g. penalty for zone z dropping below k available units). If Q-Rescue's coverage term is only linear per ambulance (a fixed cost for ambulance a leaving its zone), the QUBO collapses to a linear assignment problem that the Hungarian algorithm solves exactly in polynomial time, and the quantum framing loses its main justification. The team should check which case their formulation is.

### Gaps
- What I searched for this specific question: "QAOA ambulance dispatch", "quantum ambulance dispatch QUBO QAOA", "quantum annealing emergency medical services ambulance location", "QUBO emergency vehicle allocation D-Wave", "QAOA dynamic ambulance redeployment/relocation/dispatching 2025 2026", "ambulance" with "quantum approximate optimization"/"quantum-inspired"/"digital annealer" plus "coverage preparedness", arXiv-targeted "ambulance QUBO Ising", and GitHub-targeted "ambulance QAOA qiskit QUBO assignment emergency calls". None returned a QUBO/QAOA formulation with a combined assignment + future-coverage objective.
- Not checked: forward citations of the two Cumming/Thomas/Chancellor preprints; IEEE Quantum Week (QCE) 2023–2026 proceedings by native search; theses; conference posters; non-English work; private or unindexed hackathon submissions (Devpost, QHack, iQuHACK, Womanium, QWorld archives were not systematically browsed).
- Therefore the correct statement is "not found in a targeted but non-exhaustive search on 9 October 2026", never "does not exist".

---

## 4. State of evidence on QAOA for constrained assignment-type problems at small scale, mitigation techniques, and credible skeptical findings

### Takeaway
Penalty-encoded QAOA with the standard X mixer at p = 1–3 typically puts little probability on feasible/optimal states for one-hot constrained problems, and results are highly sensitive to penalty weight; constraint-preserving mixers are the best-evidenced fix. Independently, credible published work says small simulated QAOA demonstrates nothing about quantum advantage, and at these sizes exact classical solvers are instantaneous.

### Cited Findings

**Feasibility, penalty weights and low depth (ambulance-specific evidence)**
- On an ambulance-location QUBO, X mixer + penalty gave 0.1–0.15 probability of the optimal state at p = 3 and p = 5 for a 5-location instance, versus close to 1 for XY mixer + Dicke state with 100% feasibility; for an 8-qubit instance the X-mixer ground-state weight at p = 3 was only 2.18x the uniform-superposition weight **[FULL TEXT]** — [Cumming & Thomas](https://arxiv.org/pdf/2211.13080)
- Same paper: penalty-weight setting is "essential"; on D-Wave the optimal-state probability varied tenfold (0.031 vs 0.00325) with penalty ratio, feasibility probability rose then flattened as the penalty grew, while approximation ratio fell; grid search over penalty weight is typically required **[FULL TEXT]** — [Cumming & Thomas](https://arxiv.org/pdf/2211.13080)
- Same paper: increasing p improves performance but lengthens optimisation; INTERP-style parameter seeding (Zhou et al.) was much more effective than many random restarts **[FULL TEXT]** — [Cumming & Thomas](https://arxiv.org/pdf/2211.13080)
- Penalty-based QAOA's ability "diminishes notably" for constrained problems such as CVRP because it struggles to sample solutions satisfying all constraints **[ABSTRACT PAGE]** — [Xie et al., arXiv:2308.08785](https://arxiv.org/abs/2308.08785)
- Reported in search summaries, **not verified in the papers**: a portfolio benchmark stating QAOA did not perform significantly better than random sampling for feasibility and approximation ratio **[SNIPPET]** — [arXiv:2509.17876](https://arxiv.org/pdf/2509.17876); a knapsack study with warm-started XY mixers where single-constraint failure rates rise with depth and strict post-selection "does not scale" **[SNIPPET]** — [arXiv:2603.00260](https://arxiv.org/pdf/2603.00260); an irrigation-scheduling QAOA study reporting an explicit null result for XY-QAOA at depth ≤ 3 on a small instance **[SNIPPET]** — [arXiv:2607.13374](https://arxiv.org/pdf/2607.13374)

**Mitigation techniques (verified at landing-page level)**
- Quantum Alternating Operator Ansatz: Hadfield, Wang, O'Gorman, Rieffel, Venturelli, Biswas, Algorithms 12(2):34 (2019), DOI 10.3390/a12020034 — generalises QAOA to broader families of mixers so hard constraints can be preserved **[ABSTRACT PAGE]** — [arXiv:1709.03489](https://arxiv.org/abs/1709.03489)
- XY mixers for one-hot constraints: Wang, Rubin, Dominy, Rieffel, Phys. Rev. A 101, 012320 (2020) — implementable without Trotter error in depth O(κ) for some classes; outperform X mixer on graph colouring **[ABSTRACT PAGE]** — [arXiv:1904.09314](https://arxiv.org/abs/1904.09314)
- Grover-mixer QAOA: Bärtschi & Eidenbenz, IEEE QCE 2020, pp. 72–82, DOI 10.1109/QCE49297.2020.00020 — needs efficient preparation of the uniform superposition of feasible states; same-cost solutions sampled with equal amplitude; no Trotter error **[ABSTRACT PAGE]** — [arXiv:2006.00354](https://arxiv.org/abs/2006.00354)
- CVaR objective: Barkoutsos, Nannicini, Robert, Tavernelli, Woerner, Quantum 4, 256 (2020), DOI 10.22331/q-2020-04-20-256 — CVaR aggregation gives faster convergence to better solutions in simulation and hardware experiments on all problems tested **[ABSTRACT PAGE]** — [arXiv:1907.04769](https://arxiv.org/abs/1907.04769)
- Warm-start QAOA: Egger, Marecek, Woerner, Quantum 5, 479 (2021), DOI 10.22331/q-2021-06-17-479 — initial state from a classical relaxation; particularly beneficial at low depth for portfolio optimisation **[ABSTRACT PAGE]** — [arXiv:2009.10095](https://arxiv.org/abs/2009.10095); Qiskit Optimization ships a `WarmStartQAOAOptimizer` tutorial **[SNIPPET]** — [Qiskit Optimization docs](https://qiskit-community.github.io/qiskit-optimization/tutorials/10_warm_start_qaoa.html)
- Recursive QAOA: Bravyi, Kliesch, Koenig, Tang, Phys. Rev. Lett. 125, 260505 (2020), DOI 10.1103/PhysRevLett.125.260505 — shows Goemans–Williamson outperforms constant-depth QAOA on certain MaxCut instances (a limitation result) and proposes a non-local variant (RQAOA) that numerically outperforms standard QAOA **[ABSTRACT PAGE]** — [arXiv:1910.08980](https://arxiv.org/abs/1910.08980)
- Unbalanced penalization: Montanez-Barrera, Willsch, Maldonado-Romo, Michielsen, Quantum Science and Technology 9(2) (2024), DOI 10.1088/2058-9565/ad35e4 — encodes inequality constraints without slack variables; on D-Wave Advantage/hybrid bin packing reached 29 items versus 11 with slack variables **[ABSTRACT PAGE]** — [arXiv:2211.13914](https://arxiv.org/abs/2211.13914). Relevant only if Q-Rescue has inequality constraints (e.g. "at most one call per ambulance").
- Linear-ramp / fixed-schedule parameters (avoids the classical optimisation loop): "Toward a linear-ramp QAOA protocol: evidence of a scaling advantage in solving some combinatorial optimization problems", npj Quantum Information (2025) **[SNIPPET]** — [Nature](https://www.nature.com/articles/s41534-025-01082-1)
- Parameter transfer/concentration: named in the brief; I did not open a primary source this session **[NOT OPENED]** — see Gaps.

**Credible skeptical findings**
- Guerreschi & Matsuura, "QAOA for Max-Cut requires hundreds of qubits for quantum speed-up", Scientific Reports 9, 6903 (2019), DOI 10.1038/s41598-019-43176-9 — realistic simulations conclude speed-up is not attainable until several hundred qubits are available **[ABSTRACT PAGE]** — [arXiv:1812.07589](https://arxiv.org/abs/1812.07589)
- Stilck França & García-Patrón, "Limitations of optimization algorithms on noisy quantum devices" (published version DOI 10.1038/s41567-021-01356-3) — substantial advantages for classical optimisation are unlikely unless noise rates fall by orders of magnitude or problem topology matches the device, even as qubit counts grow; covers annealers, VQE and QAOA **[ABSTRACT PAGE]** — [arXiv:2009.05532](https://arxiv.org/abs/2009.05532)
- Wang, Fontana, Cerezo, Sharma, Sone, Cincio, Coles, "Noise-Induced Barren Plateaus in Variational Quantum Algorithms", Nature Communications 12, 6961 (2021), DOI 10.1038/s41467-021-27045-6 — under local Pauli noise gradients vanish exponentially in qubit number when depth grows linearly; explicitly covers the Quantum Alternating Operator Ansatz **[ABSTRACT PAGE]** — [arXiv:2007.14384](https://arxiv.org/abs/2007.14384)
- Costa, Morales, An, Sanders, arXiv:2412.13035 (Dec 2024, preprint) — "asymptotic analysis alone cannot support a credible claim of quantum advantage"; a simple classical approach matched the quantum methods tested on Sherrington–Kirkpatrick **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2412.13035)
- Stopfer & Wagner, "Quantum Portfolio Optimization: An Extensive Benchmark", arXiv:2509.17876 — 270 instances up to 1,000 assets; quantum methods only testable up to 30 assets; all instances solved to proven optimality by MIP "in the order of seconds"; tailored heuristic beats quantum approaches at fixed runtime; "very limited room for a potential quantum advantage" **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2509.17876)
- A follow-up to a claimed quantum–classical scaling gap in approximate QUBO optimisation showed the gap closed when a stronger classical reference (simulated bifurcation) was used, and argued small sizes are insufficient to infer scaling **[SNIPPET]** — [arXiv:2505.22514](https://arxiv.org/html/2505.22514v1)
- Classical simulability: Medvidović & Carleo simulated QAOA at 54 qubits with neural-network quantum states **[SNIPPET]** — [arXiv:2009.01760](https://arxiv.org/abs/2009.01760v2)
- A 2026 hackathon repo's own documentation concedes that QAOA on simulators or NISQ hardware gives no speed-up and that classical exact solvers and heuristics solve its QUBO in milliseconds at that size **[SNIPPET]** — [Q-TRAFFIC](https://github.com/Theshiya30/Q-TRAFFIC-Quantum-Urban-Traffic-Optimization)
- Cumming & Thomas's own verdict after a 62-page study on an ambulance problem: gate-based hardware "needs much more scale and fidelity" before commercially valuable use **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2211.13080)

### Inferences
- For a 3 x 4 instance (12 assignment qubits before slack), the search space is 4,096 bitstrings; brute-force enumeration is microseconds and the feasible set is tiny. Any reported QAOA "success" must therefore be benchmarked against **uniform random sampling over bitstrings** and against **random sampling over feasible assignments**, not only against greedy. A QAOA that returns the optimum in 5% of shots is not impressive if the feasible set has ~20–100 members.
- Expect, from the cited ambulance-location evidence, that X-mixer + penalty at p ≤ 3 will give low optimal-state probability and partial infeasibility, and that results will swing with penalty weight. Reporting a penalty-weight sweep and feasibility rate is therefore not optional.
- The cheapest credible upgrade is a per-call (or per-ambulance) XY/ring mixer with a feasible initial state, plus CVaR; these are the mitigations with the most direct supporting evidence on closely analogous problems. Note the XY mixer preserves only one family of one-hot constraints at a time; the second family (ambulance used at most once) still needs penalties or a more elaborate mixer.
- Noise results imply nothing should be claimed about hardware performance from a noiseless simulator.

### Gaps
- I did not find a published table of "typical" feasibility rates and approximation ratios for penalty-QAOA on generalised-assignment instances at p = 1–3; the numbers above come from one ambulance-location preprint and abstracts/snippets on other problems. There is no single authoritative number to quote.
- Not opened this session (verify before citing): parameter concentration/transfer papers; Zhou et al. (INTERP); McClean et al. (original barren plateaus); Lucas (Ising formulations of NP problems); any "QAOA scaling advantage on LABS" result (a search result pointed to an Argonne news item only).
- The specific 1.77e-5 feasibility figure and the "no better than random sampling" statement are from search summaries and must be confirmed in the PDFs.

---

## 5. Typical criticisms of hackathon / student "quantum optimization for X" projects, and published benchmarking guidance

### Takeaway
The recurring criticisms are: instances trivially solvable by enumeration, weak or untuned classical baselines, simulator results presented as quantum advantage, overhead excluded from timings, selective reporting, and a quantum component that is decorative or silently replaced by a classical fallback. Formal guidance exists (Abbas et al. 2024; QOBLIB 2025/2026) and stresses strong baselines, standardised reporting and reproducibility.

### Cited Findings
- Abbas et al. (46 authors), "Challenges and Opportunities in Quantum Optimization", Nature Reviews Physics (2024), DOI 10.1038/s42254-024-00770-9 — emphasises benchmarking and "clear metrics to conduct appropriate comparisons with classical optimization techniques", and distinguishes provably exact from heuristic settings for possible advantage **[ABSTRACT PAGE]** — [arXiv:2312.02279](https://arxiv.org/abs/2312.02279)
- Koch, Bernal Neira, Chen, et al. (27 authors), "Quantum Optimization Benchmarking Library – The Intractable Decathlon", Nature Computational Science 6, 653–671 (2026), arXiv:2504.03832 — ten problem classes hard for classical solvers, under 100 to about 100,000 variables, aiming at "systematic, fair, and comparable benchmarks", with standardised result reporting, reproducibility and solution track records **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2504.03832); IBM's accompanying blog frames the metrics as enabling fair comparison across quantum and classical methods **[SNIPPET]** — [IBM Quantum blog](https://ibm.com/quantum/blog/quantum-optimization-benchmarking)
- QOBLIB's authors caution the chosen classes are not necessarily where advantage will appear **[SNIPPET]** — [arXiv HTML](https://arxiv.org/html/2504.03832v2)
- Runtime accounting critique: arXiv:2510.06337 argues analyses that exclude system-level overheads (readout, transpilation, thermalisation) bias performance claims, and that runtime advantage has not been shown on current NISQ hardware under comprehensive benchmarking **[SNIPPET]** — [arXiv](https://arxiv.org/pdf/2510.06337v3)
- Weak-baseline critique: a claimed scaling gap disappeared once a stronger classical solver was used; small sizes cannot support scaling inferences **[SNIPPET]** — [arXiv:2505.22514](https://arxiv.org/html/2505.22514v1)
- A 2026 quantum-annealing review is reported to flag selective reporting, poor classical baselines and excluded preprocessing overhead as benchmarking problems **[SNIPPET]**; the abstract page I opened confirms only the embedding-overhead point (5–12 physical qubits per logical variable, 80–92% capacity loss) **[ABSTRACT PAGE]** — [arXiv:2602.03101](https://arxiv.org/abs/2602.03101)
- Cumming & Thomas explicitly set out to vary "many meta-parameters that papers often ignore" (optimiser, penalty weight, mixer, initialisation), i.e. under-reported hyperparameter sensitivity is a recognised weakness **[ABSTRACT PAGE]** — [arXiv abs](https://arxiv.org/abs/2211.13080)
- Example of decorative-quantum risk in the wild: the other Q-Rescue repo describes "QAOA-inspired local simulation and graceful fallback when quantum packages are not installed" and a "deterministic local fallback", so a demo may show results with no quantum circuit executed **[README]** — [GitHub](https://github.com/Sibi7Antony/Q-Rescue)
- Example of honest framing judges respond to: the same README states QAOA experiments are "intentionally small" and that Aer simulation "does not imply quantum advantage" **[README]** — [GitHub](https://github.com/Sibi7Antony/Q-Rescue)

### Inferences
Likely judge objections to Q-Rescue, with the response that the evidence supports:
1. *"3 x 4 is solved instantly by brute force / Hungarian."* True. Concede it; position the instance as a formulation-validation testbed, and show a scaling table (qubits vs ambulances x calls) rather than pretending the instance is hard.
2. *"Greedy is a straw-man baseline."* Include the exact optimum (enumeration or MILP/CP-SAT), Hungarian on the linearised problem, simulated annealing on the same QUBO, and random feasible sampling. Greedy should be shown to be suboptimal on designed instances *because of the coverage term*, with the exact solver confirming the optimum.
3. *"Is QAOA actually run?"* Show circuit, depth p, shots, optimiser, seeds, transpiled gate counts; no silent classical fallback.
4. *"Penalty weights were tuned to make it work."* Report a penalty sweep and feasibility rate per setting.
5. *"The coverage term is arbitrary."* Tie weights to an interpretable quantity (e.g. expected demand per zone x probability of a call arriving while the unit is away), and show sensitivity.
6. *"Simulator ≠ quantum."* State plainly: noiseless simulator, no hardware, no advantage claim.
7. *"The quantum part adds nothing."* Honest answer: at this size it does not; the contribution is the formulation and an honest benchmark.
- Minimum reporting set consistent with the guidance above: feasibility rate; probability of sampling the optimum; approximation ratio over feasible samples; comparison with uniform random sampling; mean and variance over many random instances and seeds; wall-clock including optimisation loop; qubit and two-qubit-gate counts; all hyperparameters.

### Gaps
- I found no published document that specifically critiques *hackathon* quantum-optimisation projects; the criticisms above are transferred from research-level benchmarking critiques and from what the repos themselves disclaim. This is inference, not a sourced claim about judging practice.
- I did not read the full QOBLIB or Abbas et al. texts, so their specific recommended metrics lists are not reproduced here.

---

## 6. Novelty-risk assessment for Q-Rescue

### Takeaway
Overall novelty is **low at the method level and low-to-moderate at the formulation level**. "Quantum for ambulances" exists; "coverage-aware dispatch" exists classically and conceptually in a quantum context; the one thing not found is their explicit combination in a single QUBO solved with QAOA and honestly benchmarked. Q-Rescue should be presented as an application-formulation and benchmarking exercise, not a research first.

### Cited Findings
Closest related work and overlap level:

| # | Work | Type | Quantum execution | Overlap | Why |
|---|------|------|-------------------|---------|-----|
| 1 | Cumming & Thomas 2022, [arXiv:2211.13080](https://arxiv.org/abs/2211.13080) | Preprint | QAOA on simulator (X, XY, 3XY mixers); VQE on IBM Perth/Guadalupe; D-Wave Advantage 4.1 | **High on domain + method, medium on problem** | Ambulance QUBO, QAOA, 5–20 qubits, penalty vs XY, classical baselines. But location only: no calls, priorities, eligibility or coverage-loss term |
| 2 | Chancellor, Cumming & Thomas 2020, [arXiv:2006.05846](https://arxiv.org/abs/2006.05846) | Preprint, conceptual | None | **Medium (idea-level high)** | Names ambulance dispatch as a quantum use case and describes coverage-"hole"-aware dispatch with Ising models; nothing formulated or run |
| 3 | RESQAI, [GitHub](https://github.com/Devsuthar2006/ambulance) | Hackathon repo | None (classical) | **Medium** | Same dispatch-with-coverage-preservation idea and priority weighting, greedy scoring, no QUBO |
| 4 | Sibi7Antony/Q-Rescue, [GitHub](https://github.com/Sibi7Antony/Q-Rescue) | Repo | Qiskit Aer QAOA endpoints with classical fallback (execution unverified) | **Medium–high on branding/theme, low–medium on formulation** | Same name, emergency response, QUBO + QAOA, tiny instances; disaster-wide rather than ambulance-to-call; no coverage term visible |
| 5 | Azad et al. 2022, [arXiv:2002.01351](https://arxiv.org/abs/2002.01351) | Peer-reviewed | QAOA on Qiskit simulator | **Medium** | Same pipeline and scale ((4,2)–(5,3)); routing rather than assignment; no EMS |
| 6 | MCLP on quantum devices: Giraldo-Quintero et al. 2022 ([DOI page](https://journal.hep.com.cn/cus/EN/10.1007/s43762-022-00070-x)); Saavedra-Benavides et al. 2026 ([arXiv:2607.16277](https://arxiv.org/abs/2607.16277)) | Peer-reviewed / preprint | D-Wave and IBM (per secondary source); QAOA + WS-QAOA | **Medium** | Coverage as the objective in QUBO/QAOA, but static siting, no dispatch |
| 7 | Lee et al. 2026, [arXiv:2609.01930](https://arxiv.org/abs/2609.01930) | Accepted journal paper (per arXiv) | QAOA on simulator and IBM 127-qubit Eagle | **Low–medium** | Emergency (search and rescue) coverage QUBO with QAOA on real hardware; sets a much higher bar for "emergency QAOA" work |
| 8 | Patient allocation by digital annealing ([IEEE 10313617](https://ieeexplore.ieee.org/document/10313617/)); Tohoku/D-Wave ([announcement](https://www.tohoku.ac.jp/en/news/research/quantum_technology_to_the_researchers.html)) | Conference paper (unverified) / announcement | Quantum-inspired classical; D-Wave hybrid | **Low–medium** | Emergency medical assignment QUBO, but patients to hospitals |
| 9 | Marikina disaster VRP, [ECTI-CIT 2024](https://ph01.tci-thaijo.org/index.php/ecticit/article/view/253577) | Peer-reviewed | D-Wave Leap (QPU vs hybrid unverified) | **Low** | Emergency logistics routing, annealing |
| 10 | Carvalho et al. 2020 EJOR ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0377221719309683)) | Peer-reviewed, classical | None | **High on problem concept, zero on quantum** | Integrated dispatch + preparedness/coverage is established classical OR |

### Inferences
**Remaining possible research gap (carefully bounded):** a single QUBO that jointly encodes (i) priority-weighted assignment of multiple simultaneous calls to eligible ambulances and (ii) a quadratic penalty for post-dispatch loss of zone coverage, evaluated with QAOA and compared against greedy and exact solvers. Not found in this search. It is an *application-formulation* gap; it is not an algorithmic contribution and carries no performance claim.

**Evidence needed to support even that gap:**
1. Forward-citation check (Google Scholar / Semantic Scholar) of arXiv:2211.13080 and arXiv:2006.05846, and native searches of IEEE Xplore (incl. QCE 2023–2026), ACM DL and Scopus for "ambulance" AND (QAOA OR QUBO OR "quantum annealing").
2. Clarify whether `Sibi7Antony/Q-Rescue` is the team's own repository; if not, differentiate or rename.
3. Demonstrate the coverage term is genuinely quadratic and changes the optimal decision: instances where exact-with-coverage ≠ exact-without-coverage ≠ greedy, verified by enumeration.
4. A follow-on simulation showing the coverage-aware choice reduces expected response time to the *next* call (otherwise the coverage term is an unvalidated modelling assumption).
5. QAOA results with feasibility rate, optimal-sample probability, approximation ratio, penalty sweep, p = 1–3, multiple seeds and random instances, versus random sampling, simulated annealing on the same QUBO, greedy and exact.
6. Ideally an XY-mixer and/or CVaR variant, since the closest prior work already compares X vs XY on an ambulance QUBO.

**Recommended contribution statement (wording to adapt):**
> "Q-Rescue is a proof-of-concept that formulates small-fleet ambulance dispatch for simultaneous prioritised calls as a QUBO that includes an explicit penalty for the geographic coverage lost when units leave their zones, and evaluates QAOA on a noiseless simulator against greedy and exact classical baselines. Prior quantum work has addressed ambulance *location* with QAOA and annealing (Cumming & Thomas, 2022) and has discussed coverage-aware dispatch conceptually (Chancellor et al., 2020); coverage-aware dispatch itself is well established in classical operations research. In a targeted, non-exhaustive literature search we did not find a QUBO/QAOA formulation combining call assignment with a future-coverage term. At the sizes studied the problem is solved exactly and instantly by classical methods; we make no claim of quantum advantage."

**Claims to avoid:**
- "First quantum approach to ambulance dispatch / emergency response" (contradicted by items 1, 2, 4, 7, 9).
- "Novel coverage-aware dispatch" (classical OR and a hackathon repo already do this).
- Any form of "quantum advantage", "faster than classical", "outperforms classical solvers", or "QAOA finds better solutions than greedy" without the exact solver alongside — the exact solver finds the same or better instantly.
- "Runs on a quantum computer" (it is a simulator).
- "Scales to real cities" — qubit count grows as ambulances x calls (plus slack), and the cited evidence shows feasibility collapsing with size under penalty encodings.
- "Real-time" — the variational optimisation loop is far slower than the classical solve at this size.
- "No prior work exists" — say "not found in our search".

**Confidence and unresolved uncertainty:**
- High confidence that ambulance-themed QUBO/QAOA work pre-exists (verified from full text).
- High confidence that Q-Rescue's method stack (QUBO → QAOA in Qiskit → greedy/exact comparison at ~12 qubits) is not methodologically novel.
- Moderate confidence (roughly two in three, my subjective estimate) that no *indexed, English-language paper* combines call assignment and a future-coverage term in a QUBO/QAOA formulation; lower confidence for unindexed hackathon submissions, theses and 2026 conference papers, where a near-duplicate is quite plausible given how many similar student repos surfaced.
- Unresolved: ownership of the same-named GitHub repo; contents of Giraldo-Quintero et al. and the IEEE digital-annealing paper; whether the Andhra Pradesh pilot's startups have published a dispatch formulation; whether Q-Rescue's own coverage term is quadratic or linear.

### Gaps
- No access to the Q-Rescue team's actual formulation or code; the assessment is against the project description in the brief only.
- Overlap ratings are my judgement, not a measured quantity.

---

## 7. Search scope and limits

### Takeaway
This was a targeted web search of roughly 20 queries and about 40 page fetches conducted on 9 October 2026; it is not exhaustive and should be described as such.

### Cited Findings
- Two papers were read from extracted PDF text: [arXiv:2211.13080](https://arxiv.org/pdf/2211.13080) and [arXiv:2006.05846](https://arxiv.org/pdf/2006.05846). All other papers were verified at abstract/landing-page level at most, as tagged in each section.
- Three GitHub repositories were opened at README level: [Sibi7Antony/Q-Rescue](https://github.com/Sibi7Antony/Q-Rescue), [Devsuthar2006/ambulance](https://github.com/Devsuthar2006/ambulance), [Amaan-Hans/Grid-Aware-Emergency-Resource-Allocation](https://github.com/Amaan-Hans/Grid-Aware-Emergency-Resource-Allocation). Code was not inspected or run.

### Inferences
- Query themes covered: quantum/QAOA/QUBO + ambulance dispatch, ambulance location, EMS, emergency vehicle allocation, dynamic redeployment/relocation, preparedness/coverage; maximal covering and facility location with QAOA; disaster relief and evacuation; patient-to-hospital allocation; fire station/shelter location; drone/taxi/ride-hailing assignment; GAP with XY mixers; QAOA skepticism and noise limits; benchmarking libraries and critiques; GitHub/hackathon ambulance QAOA projects.
- Date coverage: results spanned 2018–October 2026, with most hits from 2022–2026. Several 2026 arXiv items (IDs 26xx) post-date my training knowledge and are reported solely from the pages fetched.

### Gaps
- Not done: native database searches (IEEE Xplore, ACM DL, Scopus, Web of Science, PubMed, SpringerLink, ScienceDirect, MDPI); Google Scholar citation chaining; systematic browsing of QHack, iQuHACK, Womanium, QWorld, Qiskit hackathon and Devpost archives; D-Wave application/example catalogue; theses repositories; non-English sources.
- Pages that failed to load: ScienceDirect (403), Michigan Engineering news (403), IEEE Xplore document page (empty), Springer and Nature (login redirects). Claims depending on them are tagged [SNIPPET].
- Items named in the brief that I did not open this session and that must be verified before citation: Harwood et al. (routing on quantum computers), parameter concentration/transfer papers, Zhou et al. (INTERP), original barren-plateau paper, large-scale QAOA benchmarking studies beyond those listed.
- Search-engine summaries can misattribute findings; every [SNIPPET] item should be opened before it is used in a report or slide.
