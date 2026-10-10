# QUBO formulation and future-coverage model for Q-Rescue (ambulance-to-emergency assignment)

Notes dated 9 October 2026. Status labels used throughout:

- **[LIT-VERIFIED]** — I read the passage in the source itself during this session (full text or abstract page, as stated).
- **[LIT-SECONDARY]** — confirmed only through a search summary or a paper citing the source; not read in the original.
- **[DERIVED]** — my own algebra/argument, not taken from a source.
- **[COMPUTED]** — my own brute-force numerical check (script `verify_qubo.py` + `boundary_check.py`, kept only in the scratch directory `C:\Users\haris\AppData\Local\Temp\claude\C--q-Rescue\586bf9ea-cea7-4373-84cc-1550be57b355\scratchpad`; output in `verify_output.txt` there). These are my computed checks, not literature results.
- **[DESIGN]** — a proposed modelling choice.

No file in `app, src, scripts, tests, data, docs` was created or modified. No application code was written.

---

## 1. Base model: sets, parameters, units, reward form vs explicit unserved variable

### Takeaway
Use one binary per *eligible* (ambulance, call) pair only, a reward-for-service objective `sum (w_j t_ij − U_j) x_ij`, and pairwise at-most-one penalties. On the worked 3×4 instance this needs 8 qubits, versus 12 with explicit unserved bits and 16 if ineligible pairs were also kept; all three give the same optimum (my computed check for the 8- and 12-qubit versions).

### Cited Findings
- QUBO/Ising models encode constraints as quadratic penalties added to the objective; the Glover–Kochenberger–Du tutorial states that penalties yield "exact model representations" and that P "must be chosen sufficiently large" for the penalty to be equivalent to the constraint. [LIT-VERIFIED, full text] — [Glover, Kochenberger & Du, arXiv:1811.11538](https://arxiv.org/abs/1811.11538)
- Lucas gives Ising formulations where the qubit count is driven by the number of binary decision plus auxiliary variables ("at most cubic in the size of the problem"), which is why removing variables structurally matters. [LIT-VERIFIED, abstract + full text] — [Lucas 2014, Front. Phys. 2:5](https://doi.org/10.3389/fphy.2014.00005)
- The pure assignment problem is the classical linear assignment problem solved by the Hungarian method. [LIT-SECONDARY for content; bibliographic data verified] — [Kuhn 1955, Naval Res. Logist. Q. 2:83–97](https://doi.org/10.1002/nav.3800020109)

### Inferences
**Definitions [DESIGN].**

| Symbol | Meaning | Unit |
|---|---|---|
| `A` | currently idle ambulances, index `i` (also `a, b`) | – |
| `C` | pending calls, index `j` (also `k`) | – |
| `E ⊆ A×C` | eligible pairs: capability matches (e.g. ALS-required call only to ALS unit), unit available, and optionally `t_ij ≤ T_max` | – |
| `E_i`, `E^j` | calls eligible for ambulance `i`; ambulances eligible for call `j` | – |
| `t_ij` | estimated travel/response time | minutes |
| `w_j` | priority weight (higher = more urgent) | dimensionless |
| `τ` | "unserved-equivalent" time: leaving call `j` unserved in this round costs as much as a `τ`-minute response | minutes |
| `U_j = w_j τ` | unserved-call penalty = service reward | weighted minutes |
| `x_ij ∈ {0,1}`, `(i,j) ∈ E` | 1 if ambulance `i` is assigned to call `j` | – |
| `D_i = Σ_{j∈E_i} x_ij` | dispatch indicator of ambulance `i` (0/1 when feasible) | – |
| `s_j = Σ_{i∈E^j} x_ij` | served indicator of call `j` (0/1 when feasible) | – |

Constraints: `D_i ≤ 1 ∀i`, `s_j ≤ 1 ∀j`, `x_ij` exists only for `(i,j) ∈ E`. No "serve every call" equality — this is what makes `|C| > |A|` (3 ambulances, 4 calls) unproblematic: at most `min(|A|,|C|, max matching in E)` calls are served and the rest pay `U_j`.

**Reward form vs explicit unserved variable [DERIVED].** Total cost in natural form:
`F(x) = Σ_{(i,j)∈E} w_j t_ij x_ij + Σ_j U_j (1 − s_j) + λ L(x)`.
Because `1 − s_j` is exactly the unserved indicator whenever `s_j ≤ 1`, expanding gives
`F(x) = Σ_j U_j + Σ_{(i,j)∈E} (w_j t_ij − U_j) x_ij + λ L(x)`,
i.e. minimising `Σ (w_j t_ij − U_j) x_ij` = maximising `Σ (U_j − w_j t_ij) x_ij`. No extra variable is needed. With `U_j = w_j τ` the coefficient is `w_j (t_ij − τ)`: negative (attractive) iff `t_ij < τ`.
- Correctness condition: the identity holds only on bitstrings with `s_j ≤ 1`; that is guaranteed by the per-call penalty (Section 7).
- A call is served only if that lowers total cost. `U_j` is therefore a real modelling parameter (it decides whether a slow assignment or a coverage loss is "worth it"), not a mere penalty constant.

Explicit form: add `u_j ∈ {0,1}`, constraint `s_j + u_j = 1`, penalty `P (s_j + u_j − 1)^2`, objective term `U_j u_j`. Same optimum, `|C|` more qubits, and an equality penalty whose expansion has both signs.

**Qubit counts [DERIVED; 8 and 12 COMPUTED on the main instance].**

| Encoding | Qubits (general) | Main instance (3 amb, 4 calls, 4 ineligible pairs) |
|---|---|---|
| Reward form, ineligible pairs eliminated | `|E|` | **8** |
| Explicit `u_j`, ineligible eliminated | `|E| + |C|` | 12 |
| Reward form, ineligible kept and penalised | `|A||C|` | 12 |
| Explicit `u_j`, ineligible kept | `|A||C| + |C|` | 16 |

[COMPUTED] The 12-qubit explicit-`u_j` QUBO (λ=20, P=100) has global minimum 168.00, identical to the reward-form `F* = 168.00` (8 qubits); its lowest infeasible energy was 178.00.

**Ineligible pairs: eliminate, do not penalise [DESIGN, justified].** (a) Fewer qubits and a `2^{#ineligible}`-times smaller search space; (b) a penalised ineligible bit can still be sampled by QAOA, so a capability-violating dispatch (BLS to an ALS-only call) can appear in the output — with elimination it cannot be *represented*; (c) one fewer penalty weight to tune and a smaller energy scale. The only cost is an index map from qubit to pair, which the decoder needs anyway (Section 9).

**Why not `P (s_j − 1)^2` without `u_j` [DERIVED + COMPUTED].** On binaries `(S − 1)^2 = 2 Σ_{a<b} x_a x_b − S + 1` (checked on all bitstrings for n ≤ 6). So an "exactly one" penalty without an unserved bit is the pairwise penalty with weight `2P` *plus a service reward of `P` per served call*. It silently forces `U_j = P` for every call, mixing a physical trade-off parameter with a constraint weight. The reward form keeps them separate.

### Gaps
- The journal version of the Glover tutorial ("Quantum Bridge Analytics I: a tutorial on formulating and using QUBO models", 4OR 17:335–371, 2019) was not opened this session; the arXiv page shows the title "A Tutorial on Formulating and Using QUBO Models" and lists no journal reference. Cite the arXiv version unless the 4OR record is checked.
- No source was found (or searched for) that prescribes a numerical value for `τ`/`U_j` in EMS dispatch; it is a project design parameter.

---

## 2. Inequality constraints without slack variables

### Takeaway
For binaries, `Σ x ≤ 1` is enforced *exactly* by `P Σ_{a<b} x_a x_b = P·C(S,2)`: zero iff feasible, at least `P` otherwise, no slack qubits. This is the textbook form in both Glover et al. and Lucas; the unbalanced-penalization method of Montañez-Barrera et al. is an approximation in general but collapses to exactly this pairwise penalty for unit-coefficient at-most-one constraints.

### Cited Findings
- Glover et al.'s table of known constraint/penalty pairs lists `x + y ≤ 1 → P(xy)`, `x1 + x2 + x3 ≤ 1 → P(x1x2 + x1x3 + x2x3)`, `x + y = 1 → P(1 − x − y + 2xy)`, `x + y ≥ 1 → P(1 − x − y + xy)`, `x ≤ y → P(x − xy)`, `x = y → P(x + y − 2xy)`. [LIT-VERIFIED, full text p. 9–10] — [arXiv:1811.11538](https://arxiv.org/abs/1811.11538)
- Glover et al.: general inequality constraints with integer data "can always be put in this form by including slack variables and then representing the slack variables by a binary expansion". [LIT-VERIFIED] — [arXiv:1811.11538](https://arxiv.org/abs/1811.11538)
- Lucas, set packing (Sec. 4.2): `H_A = A Σ_{i,j: V_i∩V_j≠∅} x_i x_j`, `H_B = −B Σ_i x_i`, and "Choosing B < A ensures that it is never favorable to violate the constraint H_A". Pairwise product penalty, no auxiliary spins. [LIT-VERIFIED, arXiv full text] — [Lucas 2014](https://doi.org/10.3389/fphy.2014.00005) / [arXiv:1302.5843](https://arxiv.org/abs/1302.5843)
- Lucas, knapsack with integer weights (Sec. 5.2): inequality handled with auxiliary one-hot weight variables `y_n` (`H_A = A(1 − Σ y_n)^2 + A(Σ n y_n − Σ w_α x_α)^2`), condition `0 < B max(c_α) < A`, spins `N + ⌊1 + log W⌋` with the "log trick". Lucas does not use the word "slack". [LIT-VERIFIED] — [arXiv:1302.5843](https://arxiv.org/abs/1302.5843)
- Montañez-Barrera, Willsch, Maldonado-Romo & Michielsen: for `h(x) = B − Σ l_i x_i ≥ 0` they replace the constraint by `ζ(x) = −λ1 h(x) + λ2 h(x)^2`, obtained by truncating `e^{−h}` at second order; no slack variables. The paper calls it an approximation; for a 5-city TSP the optimum was not always the ground state (worst case position 7 of 2^20). 4-city TSP: 17 qubits with slack vs 12 unbalanced. λ's were tuned by Nelder–Mead. [LIT-VERIFIED via ar5iv full text] — [arXiv:2211.13914](https://arxiv.org/abs/2211.13914), Quantum Sci. Technol. 9 (2024), [doi:10.1088/2058-9565/ad35e4](https://doi.org/10.1088/2058-9565/ad35e4)

### Inferences
- **Exactness proof [DERIVED].** With `S = Σ_a x_a`, `Σ_{a<b} x_a x_b = C(S,2) = S(S−1)/2`. It is 0 for `S ∈ {0,1}` and ≥ 1 for `S ≥ 2` (grows quadratically: 1, 3, 6, …). [COMPUTED] Verified on every bitstring for n = 1..6.
- **Comparison [DERIVED].**

| Encoding of `S ≤ 1` | Extra qubits | Feasible states | Notes |
|---|---|---|---|
| Pairwise `P·C(S,2)` | 0 | energy 0 for S=0 and S=1 | exact; only positive couplings |
| Equality `P(S−1)^2` | 0 | S=0 penalised by `P` | wrong constraint (forces service) unless that is intended |
| Slack `P(S + s − 1)^2`, `s∈{0,1}` | 1 per constraint | 0 after minimising over `s` | exact ([COMPUTED] n ≤ 5) but adds 1 qubit and `|group|` couplings per constraint; pointless here |
| Unbalanced `−λ1 h + λ2 h^2`, `h = 1 − S` | 0 | see below | general-purpose approximation |

- **Unbalanced penalization reduces to the pairwise penalty here [DERIVED + COMPUTED].** With `λ1 = λ2 = λ`: `−(1−S) + (1−S)^2 = S(S−1) = 2·C(S,2)`; computed values for S = 0..3 are 0, 0, 2, 6. So for unit-coefficient at-most-one constraints it is *exactly* the pairwise penalty with `P = 2λ`. With `λ1 ≠ λ2` (e.g. 0.5, 1) the values are 0.5, 0, 1.5, 5: `S = 0` is penalised relative to `S = 1`, i.e. it injects a hidden service reward. Conclusion: unbalanced penalization offers nothing for Q-Rescue's constraints; it matters only for weighted/capacity inequalities, which this model does not have.
- For the main instance: 3 per-ambulance and 4 per-call constraints would need 7 slack qubits (8 → 15) under a slack encoding; the pairwise form needs none.

### Gaps
- Lucas's maximal-independent-set and clique Hamiltonians were not re-read line by line (only set packing and knapsack were).

---

## 3. Future coverage, approach A: per-ambulance linear coverage-loss penalty

### Takeaway
A linear term `λ Σ_i c_i D_i` is trivially QUBO-compatible but is exact only when at most one ambulance is dispatched, or when no zone is shared. On the worked instance it reports a loss of 0.5 calls/h for dispatching all three ambulances when the true loss is 2.6, and consequently never holds an ambulance back until λ ≈ 90.

### Cited Findings
- The MEXCLP dispatch heuristic of Jagtenberg, Bhulai & van der Mei evaluates, for *one* incident, "the marginal coverage that each ambulance provides for the region" and sends the one with smallest marginal coverage among those that can arrive in time. This is exactly a per-ambulance marginal quantity computed with all other idle units present. [LIT-VERIFIED, author manuscript Sec. 4.2] — [Jagtenberg et al. 2017, Health Care Manag. Sci. 20:517–531](https://doi.org/10.1007/s10729-016-9368-0); manuscript: [ir.cwi.nl/pub/24632/24632A.pdf](https://ir.cwi.nl/pub/24632/24632A.pdf)

### Inferences
- **Interpretation [DERIVED].** `c_i` = demand rate (expected calls/hour) that becomes uncovered if ambulance `i` alone leaves. Substituting `D_i = Σ_j x_ij` gives the linear coefficient `λ c_i` on every `x_ij` of ambulance `i`: no new couplings. It is the correct quantity for a one-call-at-a-time rule such as the Jagtenberg heuristic.
- **Flaw [DERIVED + COMPUTED].** Coverage loss is not additive across ambulances. Main-instance zones (Section 8): marginal `c = (0.3, 0, 0.2)`; "participation" definition `c' = (0.9, 2.1, 1.7)` (all demand in zones the ambulance covers).

| Dispatched set | True loss | Σ marginal `c_i` | Σ participation `c'_i` |
|---|---|---|---|
| {A1} | 0.30 | 0.30 | 0.90 |
| {A2} | 0.00 | 0.00 | 2.10 |
| {A3} | 0.20 | 0.20 | 1.70 |
| {A1,A2} | 0.90 | 0.30 | 3.00 |
| {A1,A3} | 0.50 | 0.50 | 2.60 |
| {A2,A3} | 1.70 | 0.20 | 3.80 |
| {A1,A2,A3} | 2.60 | 0.50 | 4.70 |

  Marginal definition under-counts whenever two dispatched units back each other up (A2 and A3 share zone Z3 with 1.5 calls/h: each looks free to send, together they strip it). Participation definition over-counts everything, including single dispatches (A2 alone: 2.1 vs true 0).
- [COMPUTED] Optimising with the marginal-linear term at λ = 20, 50, 89 returns "dispatch all three" (true cost 186.0 / 264.0 / 365.4) while the exact optimum is A1→C1, A3→C3 (cost 168.0 / 183.0 / 202.5). Approach A switches only at λ > 90.

### Gaps
- None for the mathematics. Whether approach A is "good enough" in realistic geographies (few shared sole-backup zones) is an empirical question not answered here.

---

## 4. Future coverage, approach B: post-dispatch zone coverage and its polynomial degree

### Takeaway
Exact single coverage is a degree-`|N_z|` polynomial in the dispatch indicators: `uncovered_z = Π_{i∈N_z} D_i`. It is exactly quadratic iff every zone has `|N_z| ≤ 2`, in which case the loss is `Σ_i c_i D_i + Σ_{a<b} g_ab D_a D_b`. For larger cover sets, exactness needs auxiliary qubits (one per 3- or 4-cover zone via Ishikawa); second-order truncations of MEXCLP are exact only up to two covering units and become non-monotone beyond.

### Cited Findings
- Maximal covering: a demand node is covered if at least one facility lies within the service standard; the model maximises covered demand. [Bibliographic data verified; content LIT-SECONDARY] — [Church & ReVelle 1974, Papers Reg. Sci. Assoc. 32:101–118](https://doi.org/10.1007/BF01942293)
- MEXCLP as restated by Jagtenberg et al.: each ambulance is unavailable with probability `q` (busy fraction); a node within range of `k` ambulances has expected covered demand `E_k = d_i (1 − q^k)`; "the marginal contribution of the kth ambulance to this expected value is `E_k − E_{k−1} = d_i (1 − q) q^{k−1}`"; the MILP uses binaries `y_ik` = 1 iff node `i` is within range of at least `k` ambulances, objective `max Σ_i Σ_k d_i (1 − q) q^{k−1} y_ik`. Their simulations used `q = 0.3`. [LIT-VERIFIED in Jagtenberg manuscript Sec. 4.1; Daskin's original not opened] — [Jagtenberg et al. 2017 manuscript](https://ir.cwi.nl/pub/24632/24632A.pdf); original: [Daskin 1983, Transp. Sci. 17(1):48–70](https://doi.org/10.1287/trsc.17.1.48)
- Preparedness (Andersson et al.): zone `j` has weight `c_j` mirroring demand; `p_j = (1/c_j) Σ_{l=1}^{L_j} γ^l / t_j^l`, where the `L_j` closest ambulances contribute, ordered `t_j^1 ≤ t_j^2 ≤ …` with contribution factors `γ^1 > γ^2 > …`. [LIT-VERIFIED in the 2004 conference paper that defines the same measure, eq. (1)–(3)] — [Andersson, Petersson & Värbrand 2004, WIT Trans. ICT 32](https://www.witpress.com/Secure/elibrary/papers/MIS04/MIS04032FU.pdf); journal paper: [Andersson & Värbrand 2007, JORS 58(2):195–201](https://doi.org/10.1057/palgrave.jors.2602174)
- Andersson & Värbrand's dispatch rule as described by a later paper: priority-1 calls get the closest available ambulance; for priority 2–3 they send the ambulance within a travel-time threshold "that will result in the least decrease in the minimum preparedness measure over all zones". The same source reports that Lee (2011) found this rule performed worse than closest-available. [LIT-SECONDARY] — ["Operation of an ambulance fleet under uncertainty", arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Ishikawa's reduction: a positive-coefficient monomial of degree `d` is rewritten with `n_d = ⌊(d−1)/2⌋` auxiliary binaries as `x_1⋯x_d = min_w Σ_{i=1}^{n_d} w_i (c_{i,d}(−S_1 + 2i) − 1) + S_2`, with `S_1 = Σ x`, `S_2 = Σ_{i<j} x_i x_j`, `c_{i,d} = 1` if `d` is odd and `i = n_d`, else 2; Rosenberg-style substitution needs `d − 2`. Later work (Boros, Crama, Rodríguez-Heck) gives `⌈log2 d⌉ − 1`. [LIT-SECONDARY: formula taken from search summaries of papers quoting Ishikawa; Ishikawa's PDF returned HTTP 403. Bibliographic data verified: IEEE TPAMI 33(6):1234–1249, 2011] — ["Quadratization of Symmetric Pseudo-Boolean Functions", arXiv:1404.6535](https://arxiv.org/abs/1404.6535); compendium: [Dattani, arXiv:1901.04405](https://arxiv.org/abs/1901.04405)
- Boros & Hammer, "Pseudo-Boolean optimization", Discrete Applied Mathematics 123(1–3):155–225, 2002 — survey covering reduction of general pseudo-Boolean optimisation to the quadratic case. [Bibliographic data verified; content LIT-SECONDARY] — [Rutgers record](https://scholarship.libraries.rutgers.edu/esploro/outputs/conferenceProceeding/Pseudo-Boolean-optimization/991031665032004646)

### Inferences
**Setup [DESIGN].** Zones `z ∈ Z`, forecast demand `d_z ≥ 0` (expected calls/hour), cover set `N_z ⊆ A` = idle ambulances able to reach `z` within threshold `T`. `y_i = 1 − D_i` = ambulance `i` remains available.

**Degree [DERIVED].** Zone `z` is covered after dispatch iff some `i ∈ N_z` has `y_i = 1` (an OR). Hence
`uncovered_z = Π_{i∈N_z} (1 − y_i) = Π_{i∈N_z} D_i`, and residual-coverage loss is
`L(D) = Σ_z d_z Π_{i∈N_z} D_i`.
A multilinear polynomial representing a pseudo-Boolean function is unique, so the degree is exactly `|N_z|` and cannot be lowered without auxiliaries. [COMPUTED] The best quadratic least-squares fit to `D1·D2·D3` on `{0,1}^3` has max error 0.125 (> 0), confirming no exact quadratic exists.

**Exactly quadratic case `|N_z| ≤ 2` [DERIVED].** Define
`c_i = Σ_{z: N_z = {i}} d_z` (demand only `i` covers), `g_ab = Σ_{z: N_z = {a,b}} d_z` (demand covered only by the pair). Then
`L(D) = Σ_i c_i D_i + Σ_{a<b} g_ab D_a D_b`.
Joint loss of dispatching both `a` and `b` = `c_a + c_b + g_ab`: the per-ambulance marginals plus the demand whose only covers were exactly those two. The cross term `g_ab D_a D_b` is the correction approach A lacks. Zones with `N_z = ∅` are already uncovered and contribute a constant. [COMPUTED] With this formula the QUBO energy plus constant equalled the coverage recomputed zone-by-zone from raw data on all 27 feasible assignments of the main instance (max difference 0).

**(i) Preparedness-style or second-order concave approximation [DERIVED].** Preparedness has rank-dependent weights (`γ^l` attaches to the `l`-th *closest remaining* ambulance), and Andersson & Värbrand use the *minimum* over zones; neither is a fixed quadratic in `y`. A quadratic surrogate is possible but is a new measure, not theirs. In general any function of the count `k = Σ_{i∈N_z} y_i` of the form `a k − b C(k,2)` is quadratic in `y`, but it has only two free parameters, so it can match a concave coverage curve at `k = 0, 1, 2` and nowhere else.

**(ii) MEXCLP [DERIVED + COMPUTED].** Removing dispatched units and keeping busy fraction `q` for the rest, `E_z(y) = d_z (1 − Π_{i∈N_z} (1 − (1−q) y_i))` — multilinear of degree `|N_z|` with top coefficient `±d_z (1−q)^{|N_z|}`. It is *not* quadratic for `|N_z| ≥ 3` (for n=3, q=0.3 the best quadratic fit has max error 0.0429; cubic coefficient 0.343). It *is* exactly quadratic for `|N_z| ≤ 2`: `E = d(1−q)(y_a + y_b) − d(1−q)^2 y_a y_b`. Second-order (Bonferroni) truncation `d[(1−q)k − (1−q)^2 C(k,2)]` versus exact, per unit demand:

| q | k=1 | k=2 | k=3 | k=4 |
|---|---|---|---|---|
| 0.3 exact | 0.70 | 0.91 | 0.973 | 0.9919 |
| 0.3 truncated | 0.70 | 0.91 | **0.63** | **−0.14** |
| 0.5 exact | 0.50 | 0.75 | 0.875 | 0.9375 |
| 0.5 truncated | 0.50 | 0.75 | **0.75** | **0.50** |

  The truncation is non-monotone: it claims a third covering unit *reduces* coverage. A least-squares quadratic is better (max error 0.054 for n=3, 0.117 for n=4 at q=0.3; 0.020 and 0.047 at q=0.5) but is exact nowhere. Exact MEXCLP for general `|N_z|` therefore needs auxiliaries. Daskin's `y_zk` variables can be used as a unary counter: `min_w [ −Σ_k v_k w_k + P_z (Σ_k w_k − Σ_{i∈N_z} y_i)^2 ]` with `v_k = d_z (1−q) q^{k−1}`; concavity (`v_1 > v_2 > …`) makes the minimiser fill `w_1, w_2, …` in order. [COMPUTED] For n=3, q=0.3 this gadget reproduces `−E(k)` exactly for `P_z = 0.71` and `1.0` and fails for `P_z = 0.5`; the threshold is `P_z > v_1 = 0.7`. Cost: `|N_z|` auxiliary qubits per zone plus another penalty weight.

**(iii) Truncated double coverage [DERIVED].** "Reward first and second cover only" is `v_1 min(k,1) + v_2 min(max(k−1,0),1)`. `min(k,1)` is itself the OR, so this is still degree `|N_z|`; it is exactly quadratic only when `|N_z| ≤ 2` (where it coincides with (ii)). For larger `N_z` it needs two counter auxiliaries `w_z1, w_z2` plus an *inequality* `w_z1 + w_z2 ≤ k`, which in turn needs slack bits or a full unary counter. No qubit saving over (ii).

**(iv) Rosenberg / Ishikawa quadratization [DERIVED + COMPUTED].** The loss term `+λ d_z Π D_i` is a *positive* monomial in the dispatch indicators (we minimise), so the cheap one-auxiliary negative-monomial gadget does not apply. Ishikawa: `⌊(|N_z|−1)/2⌋` auxiliaries per zone — 1 for 3- or 4-cover zones, 2 for 5–6. Degree 3: `D_a D_b D_c = min_w [ w(1 − D_a − D_b − D_c) + D_a D_b + D_a D_c + D_b D_c ]`. Rosenberg: replace a product by `w` with penalty `M(x_1 x_2 − 2 x_1 w − 2 x_2 w + 3w)`, `d − 2` auxiliaries per monomial and one more penalty weight `M`.
  - [COMPUTED] Ishikawa identity holds on all `2^d` points for d = 3..7 (aux = 1,1,2,2,3). Rosenberg penalty is 0 iff `w = x_1 x_2` and ≥ 1 otherwise, and `min_w [w x_3 + pen] = x_1 x_2 x_3`. Negative-monomial gadget `−Π x = min_w −w(S_1 − (d−1))` holds for d = 2..6.
  - [COMPUTED] Main instance plus a fifth zone Z5 covered by all three ambulances (0.8 calls/h), 9 qubits with one Ishikawa auxiliary, P = 100: global QUBO minimum equals the raw-data optimum of the true cubic problem at λ = 5 (−149.0, all three dispatched), λ = 8 (−140.8, A1→C1, A2→C3) and λ = 20 (−132.0, A1→C1, A3→C3); minimising over the auxiliary reproduced the raw cost on every feasible assignment (max difference 3e−14).
  - Caveat: the gadget identity is proved for 0/1 arguments. Since `D_i` is a *sum* of qubits, it holds only where the per-ambulance constraint holds; on infeasible strings it is just some polynomial, and the penalty bound of Section 7 must be re-checked by enumeration (done above for P = 100: lowest infeasible −89.0 vs optimum −132.0 at λ = 20).

**Summary table [DERIVED].**

| Coverage measure | Exact quadratic? | Auxiliary qubits | Independence assumption | Double counting |
|---|---|---|---|---|
| A: linear `c_i` | only if one unit dispatched or no shared zones | 0 | none | under- or over-counts shared zones |
| B, `|N_z| ≤ 2` | yes | 0 | none (deterministic) | none |
| B, general, Ishikawa | yes | `⌊(|N_z|−1)/2⌋` per zone | none | none |
| MEXCLP, `|N_z| ≤ 2` | yes | 0 | units busy independently with common `q` | none if dispatched units are removed rather than also discounted by `q` |
| MEXCLP 2nd-order truncation | no (non-monotone for k ≥ 3) | 0 | as above | — |
| MEXCLP unary counter | yes | `|N_z|` per zone | as above | none |
| Double coverage, general | yes only with counter + slack | ≥ 2 per zone + slack | none | none |

### Gaps
- Daskin (1983) and Andersson & Värbrand (2007) were not opened in the original (paywalled). MEXCLP content is as restated by Jagtenberg et al.; the preparedness formula is from the authors' 2004 conference paper, which the later literature treats as the same measure. The independence assumption behind `q` is standard knowledge about MEXCLP but I did not read Daskin's own statement of it.
- Rosenberg's paper: I could not confirm the commonly cited "Cahiers du Centre d'Études de Recherche Opérationnelle 17 (1975) 71–74". A 1972 RAIRO article cites it as a Université de Montréal report "submitted to Operations Research". Treat year/venue as unverified.
- Ishikawa's formula was not read in Ishikawa's own paper (403); it is corroborated by secondary sources and by my enumeration for d ≤ 7. DOIs for Ishikawa (10.1109/TPAMI.2010.91) and Boros & Hammer (10.1016/S0166-218X(01)00341-9) are from memory and unverified.

---

## 5. Substituting y_i = 1 − Σ_j x_ij: couplings and validity

### Takeaway
The substitution keeps everything quadratic: `g_ab D_a D_b = g_ab Σ_{j∈E_a} Σ_{k∈E_b} x_aj x_bk`, adding up to `|E_a||E_b|` couplings per backed-up pair. On the main instance couplings rise from 14 to 22 (of 28 possible). `D_i` is a 0/1 indicator only when the per-ambulance constraint holds; on violating strings `y_i` goes negative, which is harmless here only because all coverage coefficients are non-negative.

### Cited Findings
- Quadratic penalties can make problems "much more dense" and introduce "large energy scales", which can worsen quantum-optimisation performance, particularly on sparse hardware. [LIT-VERIFIED, abstract] — [Mirkarimi et al., Phys. Rev. Research 6, 043241 (2024), arXiv:2404.05467](https://arxiv.org/abs/2404.05467)

### Inferences
- **Coupling count [DERIVED].**
  - per-ambulance penalties: `Σ_i C(|E_i|, 2)`;
  - per-call penalties: `Σ_j C(|E^j|, 2)`;
  - coverage: for each pair with `g_ab ≠ 0`, `|E_a||E_b|` products, of which `|E_a ∩ E_b|` (same call) coincide with existing per-call couplings.
  - Main instance: 8 + 6 = 14 without coverage; coverage adds 8 (pair A1–A2) + 4 (pair A2–A3) = 12 products, 4 already present → **22** total. [COMPUTED] 14 at λ = 0, 22 at λ = 20, out of C(8,2) = 28.
  - Worst case (full eligibility, every pair backed up): every pair of variables is coupled, i.e. the complete graph `C(|A||C|, 2)`. Each QAOA layer needs one two-qubit ZZ rotation per coupling, so coverage raises per-layer two-qubit gate count by 57% here and removes any sparsity. Irrelevant on a statevector simulator at 8–12 qubits; relevant for any hardware claim.
  - Approach A adds zero couplings.
- **Validity of the indicator [DERIVED].** `D_i ∈ {0,1}` iff ambulance `i`'s at-most-one constraint holds. If violated (`D_i = 2`), `y_i = −1` and `D_a D_b` can be 2 or 4. In the loss form used here (`c_i, g_ab ≥ 0`, written in `D`), every such violation *raises* the energy further, so it cannot create a spurious low-energy state; this is what makes the simple penalty bound of Section 7 valid. If coverage is instead written as a *reward* in `y` with mixed signs (e.g. MEXCLP's `−d(1−q)^2 y_a y_b`, or any gadget), a violated row can be rewarded, and the penalty must additionally exceed the largest such gain. Always verify by enumeration at prototype size.
- [COMPUTED] Example: A1→C1 and A1→C2 simultaneously (`D_1 = 2`): objective part −147.0 (below the optimum −132.0), total energy −47.0 at P = 100 but −97.0 at P = 50. Decoded energies of infeasible strings are meaningless as costs and must never be reported as objective values.

### Gaps
- No source consulted quantifies QAOA depth/fidelity cost per added coupling for problems of this size; the gate-count statement is structural, not a performance measurement.

---

## 6. Recommended prototype formulation, the "dynamic future coverage" claim, and λ

### Takeaway
Prototype: reward-form assignment + exact pair-coverage term (approach B with cover sets truncated to the two nearest idle units, or 1 Ishikawa auxiliary per 3-cover zone). Describe it as "post-dispatch residual coverage of forecast demand in a static one-shot snapshot", not "dynamic future coverage". Set λ by unit conversion (`λ = w̄ · Δt · H`) and report a λ sweep.

### Cited Findings
- Jagtenberg et al.: the MEXCLP dispatch heuristic "reduces the fraction of late arrivals by 18% compared to the 'closest idle' benchmark", but increases average response time (37% in their instance); "we expect that in realistic cases decision makers will prefer the closest idle policy over the MEXCLP heuristic." Results come from long discrete-event simulations (20 runs of 5,000 simulated hours). [LIT-VERIFIED, abstract + manuscript Sec. 6] — [Jagtenberg et al. 2017](https://doi.org/10.1007/s10729-016-9368-0)
- A later book chapter by the same authors reports 13% rather than 18%. [LIT-SECONDARY, search summary] — [IDEAS record](https://ideas.repec.org/h/spr/isochp/978-3-319-47766-4_9.html)
- Lee (2011) found the Andersson–Värbrand preparedness dispatch rule performed worse than closest-available. [LIT-SECONDARY] — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Andersson & Värbrand restrict coverage-aware dispatch to lower priorities; priority-1 calls get the closest available ambulance. [LIT-SECONDARY] — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)

### Inferences
- **Recommended model [DESIGN].** `min Σ_{(i,j)∈E} (w_j t_ij − U_j) x_ij + λ [Σ_i c_i D_i + Σ_{a<b} g_ab D_a D_b] + P_A Σ_i C(D_i,2) + P_C Σ_j C(s_j,2)`. If the data contain zones with 3+ covers: either (a) define `N_z` as the two nearest idle ambulances within `T` and state that the model measures "coverage by one of the two nearest units", or (b) keep the exact cubic term with one Ishikawa auxiliary per such zone. Do not use the second-order MEXCLP truncation for 3+ covers.
- **Honesty of the "dynamic" claim [DERIVED].** The model has no time axis: no arrival process, no service completion, no relocation, no re-optimisation. `d_z` is a forecast *rate* and coverage is evaluated once, for the post-dispatch state. Supportable wording: "one-shot assignment with a penalty for forecast demand left without a unit within T minutes after dispatch (residual coverage)". Not supportable without a simulation: "dynamic", "optimises future response times", or any claim of better patient outcomes. The literature's own evidence is mixed (18% fewer late arrivals but 37% longer mean response; preparedness rule worse than closest in Lee's tests), so even the classical idea is a trade-off, not a free win.
- **The coverage term is inert when everything is dispatched [DERIVED + COMPUTED].** If every idle ambulance is sent in every near-optimal solution (typical when calls outnumber ambulances and all `U_j` are large), `L` is constant and coverage cannot change the answer. With 3 ambulances and 4 calls, coverage can only act by (a) changing *which* ambulance serves a call when eligibility leaves a unit spare, or (b) *deferring* a low-priority call to keep a unit. In the main instance it does (b): at λ = 20 call C4 (w = 1) is left unserved. This is a policy decision with safety implications (Section 11) and must be presented as such.
- **λ: units and a principled value [DERIVED/DESIGN].** Objective units are weighted minutes; `L` is in expected calls/hour. `λ` has units weighted-minutes per (call/hour). Conversion: an uncovered rate `d` over the expected unavailability `H` hours of the dispatched unit yields `d·H` expected calls, each incurring about `Δt` extra minutes at mean priority `w̄`: `λ = w̄ · Δt · H`. Example used below: `w̄ = 2`, `Δt = 10 min`, `H = 1 h` → `λ = 20`. Because all three factors are rough, report a sweep rather than a single value.
- **Sweep [COMPUTED, main instance, P = 100].**

| λ range | Optimal assignment | Weighted response (wt-min) | Unserved penalty | Uncovered (calls/h) |
|---|---|---|---|---|
| 0 ≤ λ < 10.59 | A1→C1, A2→C3, A3→C4 | 44 | 90 (C2) | 2.6 |
| 10.59 ≤ λ < 15 | A1→C1, A2→C3 | 32 | 120 (C2, C4) | 0.9 |
| 15 < λ < 180 | A1→C1, A3→C3 | 38 | 120 (C2, C4) | 0.5 |
| λ > 180 | A2→C3 only | 8 | 240 (C1, C2, C4) | 0.0 |

  Breakpoints: change observed between λ = 10.58 and 10.59 (algebraically 18/1.7 = 10.588); exact ties at λ = 15 and λ = 180 (two optimal assignments each). The last row is a warning: for large λ the model leaves the priority-4 call C1 unserved to protect coverage.
- **Pareto sweep caveat [DERIVED, standard fact not sourced here].** A weighted-sum sweep finds only supported Pareto points (those on the convex hull of the response/coverage trade-off). At prototype size, enumerate all feasible assignments and plot (response cost, uncovered demand) directly instead.
- **Double-counting warnings [DERIVED].**
  1. *Unserved penalty vs coverage*: the coverage term can buy "future" coverage by leaving a *present* call unserved. To guarantee call `j` is never deferred for coverage by ambulance `i`: `λ · (c_i + Σ_b g_ib) < U_j − w_j t_ij`. For C1/A1 in the main instance: `λ · 0.9 < 96`, i.e. λ < 106.7 is sufficient (the sweep shows C1 stays served up to λ = 180).
  2. *Forecast vs current calls*: if `d_z` is estimated from data that include the very calls being assigned, their zones are counted twice. Use a forecast that excludes pending calls.
  3. *Busy fraction*: with MEXCLP, dispatched units must be removed from `N_z`; also applying `q` to them double-counts their unavailability.
  4. *Approach A + B together*: never add a linear `c_i` computed with the participation definition on top of the zone formula; the zone formula already contains the correct linear part.

### Gaps
- No source was found giving an empirically calibrated exchange rate between response minutes and coverage; `λ = w̄ Δt H` is my proposal.
- No simulation was run; nothing here shows the coverage-aware rule improves any real performance indicator.

---

## 7. Full QUBO in minimisation form and penalty selection

### Takeaway
`H(x) = Σ_e h_e x_e + Σ_{e<f} J_ef x_e x_f` with closed-form coefficients below. A provable sufficient penalty is `P > max_{(i,j)∈E} (U_j − w_j t_ij)` (96 for the main instance); enumeration shows the true threshold there is 57 (λ = 20) or 63 (λ = 0). Keep P just above the provable bound, not orders of magnitude above it.

### Cited Findings
- Glover et al.: "A penalty value that is too large can impede the solution process as the penalty terms overwhelm the original objective function information"; too small "jeopardizes the search for feasible solutions"; there is usually a "Goldilocks region"; a starting point is P at 75%–150% of an estimate of the original objective value; solutions "can always be checked for feasibility". [LIT-VERIFIED, full text Sec. 4] — [arXiv:1811.11538](https://arxiv.org/abs/1811.11538)
- Lucas: penalty/objective ratio conditions of the form `B < A` (set packing: "a penalty of at least A per extra set included") and `0 < B max(c_α) < A` (knapsack). Same logic as the bound below: the penalty for one violation must exceed the largest objective gain one violation can buy. [LIT-VERIFIED] — [arXiv:1302.5843](https://arxiv.org/abs/1302.5843)
- Verma & Lewis, "Penalty and partitioning techniques to improve performance of QUBO solvers", Discrete Optimization 44 (2022) 100594: presents approaches to bound the magnitude of the penalty scalar M, tested on problems with a single equality constraint. A 2025 paper summarises their method as deriving weights from the largest possible gain from violating a constraint. [LIT-SECONDARY: journal summary and a citing paper only; full text not read] — [doi:10.1016/j.disopt.2020.100594](https://doi.org/10.1016/j.disopt.2020.100594)
- Ayodele: penalty weights that are too small lead to infeasible solutions being returned, "while values that are too large may lead to slower convergence"; proposes static penalty-weight methods for permutation problems. [LIT-VERIFIED, abstract only] — [arXiv:2206.11040](https://arxiv.org/abs/2206.11040), EvoCOP 2022, doi:10.1007/978-3-031-04148-8_11
- Mirkarimi et al.: quadratic penalties introduce large energy scales and density that can degrade quantum annealing and QAOA performance. [LIT-VERIFIED, abstract] — [arXiv:2404.05467](https://arxiv.org/abs/2404.05467)
- Montañez-Barrera et al. report QAOA (p = 1) success probabilities dropping sharply when extra slack qubits enlarge the search space (e.g. 0.02% vs 0.227% for a 4-city TSP). [LIT-VERIFIED via ar5iv] — [arXiv:2211.13914](https://arxiv.org/abs/2211.13914)

### Inferences
**Coefficients [DERIVED].** Variables indexed by eligible pairs `e = (i,j)`. Minimise
`H(x) = Σ_{(i,j)∈E} h_ij x_ij + Σ_{e<f} J_ef x_e x_f`, constant `Σ_j U_j` dropped (`F = H + Σ_j U_j` on feasible strings).

- Linear: `h_ij = w_j t_ij − U_j + λ c_i`.
- Quadratic, for distinct variables `(a,j)` and `(b,k)`:
  - same ambulance, different calls (`a = b`, `j ≠ k`): `J = P_A`;
  - different ambulances, same call (`a ≠ b`, `j = k`): `J = P_C + λ g_ab`;
  - different ambulances, different calls: `J = λ g_ab`.
- `c_i`, `g_ab` as in Section 4 (`g_ab = 0` if no zone is covered exactly by `{a,b}`). All `J ≥ 0`; only linear terms are negative.
- Sign check: attractive assignments have `h < 0`; every penalty and every coverage coupling is positive (raises energy when both bits are 1). Constraint directions: both families are "≤ 1", enforced by pairwise products within a row (ambulance) or column (call).

**Ising form for QAOA [DERIVED + COMPUTED].** With `x_k = (1 − z_k)/2`: `J^Z_kl = J_kl/4`, `h^Z_k = −h_k/2 − (1/4) Σ_{l≠k} J_kl`, offset `= Σ_k h_k/2 + Σ_{k<l} J_kl/4`. Verified on all 256 bitstrings of the main instance (offset 247.0; max `|h^Z|` = 126, max `|J^Z|` = 32.5).

**Provable sufficient penalty [DERIVED].** Let `f(x)` be the objective polynomial (everything except penalties) and `V(x) = Σ_i C(D_i,2) + Σ_j C(s_j,2)`, single weight `P = P_A = P_C`.
- Claim: if `c_i, g_ab ≥ 0` and `P > M := max_{(i,j)∈E} (U_j − w_j t_ij)`, every infeasible `x` has strictly higher energy than some feasible `x'`, so the QUBO minimiser is the constrained optimum.
- Proof: take infeasible `x`; pick a 1-bit `(i,j)` belonging to a violated group. Clearing it lowers `V` by at least 1 (it was paired with at least one other 1-bit in that group). The objective changes by `−(w_j t_ij − U_j) − λ(c_i + Σ_b g_ib D_b) ≤ U_j − w_j t_ij ≤ M`, since the coverage part can only decrease. So energy changes by at most `M − P < 0`. Repeat until `V = 0`.
- Looser, data-independent form: `P > max_j U_j`.
- With Ishikawa/MEXCLP gadgets or mixed-sign coverage, the monotonicity step fails; add the largest possible gadget gain to `M` or verify by enumeration.

**Why not a huge P [DERIVED from the cited statements].** (1) QAOA's cost unitary is `exp(−iγH)`; if penalty terms are 10–100× the objective terms, the γ range in which objective differences produce distinguishable phases is tiny while penalty phases wrap around many times, giving a rugged, rapidly oscillating parameter landscape. (2) After normalising `H` to a fixed scale, objective differences shrink in proportion to `1/P`, so the optimiser sees an almost flat landscape among feasible states. (3) On hardware, coefficient precision and noise amplify this. These are the mechanisms behind Glover's "overwhelm" and Mirkarimi's "large energy scales"; I did not find a source in this session that quantifies them for a problem like this one.

**Normalisation [DESIGN].** Divide all coefficients by a single positive scale (e.g. `max(|h^Z|, |J^Z|)`) before building the QAOA circuit; this does not change the argmin, only the γ scale. Report energies in original units by recomputing from raw data (Section 9), never by un-scaling a sampled expectation value. Main instance at λ = 20, P = 100: `|h|` from 10 to 90, `J` from 12 to 130 — ratio of largest to smallest nonzero coefficient about 13.

**Enumeration results [COMPUTED, main instance, 256 bitstrings, 27 feasible, 229 infeasible].**

| λ | P | min feasible H | min infeasible H | infeasible strictly above? |
|---|---|---|---|---|
| 20 | 50 | −132 | −139 | no |
| 20 | 57 | −132 | −132 | tie (fails strictness) |
| 20 | 58 | −132 | −131 | yes |
| 20 | 97 | −132 | −92 | yes |
| 20 | 100 | −132 | −89 | yes (gap 43) |
| 0 | 60 | −166 | −169 | no |
| 0 | 63 | −166 | −166 | tie |
| 0 | 64 | −166 | −165 | yes |
| 0 | 97 | −166 | −132 | yes |
| 0 | 100 | −166 | −129 | yes (gap 37) |

- Smallest penalty at which no infeasible bitstring is at or below the best feasible one: any `P > 57` at λ = 20 and any `P > 63` at λ = 0 (smallest integers 58 and 64). The provable bound is 96; the looser one 120.
- At `P = 97` (and at 96.0001 for λ = 0) the stronger property also held by enumeration: every infeasible string is strictly dominated by a feasible string obtained by clearing some of its bits.
- The threshold depends on λ (it ranged from 15 to 63 across the sweep). Recommendation: set `P` from the provable bound (e.g. `P = 100` here), not from a per-instance tuned threshold, because the threshold itself can only be found by solving the problem.

### Gaps
- Verma & Lewis's actual bounds were not read; only that they bound the penalty scalar via maximal gain from violation. Do not attribute the specific bound above to them — it is my derivation in the spirit of Lucas's `B < A` argument.
- No QAOA runs were performed; the statement that large P hurts QAOA rests on the cited qualitative sources plus reasoning, not on my own experiment.

---

## 8. Worked numerical examples

### Takeaway
A fully specified 3-ambulance, 4-call, 4-zone instance (8 qubits) and a 2×3 hand instance (5 qubits) are given; in both, the QUBO global minimum over all bitstrings equals the constrained optimum recomputed from raw data. At λ = 0 the optimum equals greedy nearest-available; at λ = 20 it differs.

### Cited Findings
- Jagtenberg et al. give a small example region in which "the 'closest idle' dispatch strategy must be suboptimal", motivating the comparison against a nearest-available baseline. [LIT-VERIFIED, manuscript Sec. 6] — [Jagtenberg et al. 2017 manuscript](https://ir.cwi.nl/pub/24632/24632A.pdf)

### Inferences
All numbers below are synthetic illustration data chosen by me [DESIGN]; all results are [COMPUTED] by enumeration.

**Main instance (3 ambulances × 4 calls).** A1 is ALS; A2, A3 are BLS. C1 and C2 require ALS.

Travel time `t_ij` (minutes; "–" = ineligible, no variable created):

| | C1 (ALS, w=4) | C2 (ALS, w=3) | C3 (w=2) | C4 (w=1) |
|---|---|---|---|---|
| A1 (ALS) | 6 | 9 | 10 | 14 |
| A2 (BLS) | – | – | 4 | 15 |
| A3 (BLS) | – | – | 7 | 12 |

`τ = 30` min → `U = (120, 90, 60, 30)`, `Σ U = 300`. Zones (threshold `T` implicit in `N_z`):

| Zone | `N_z` | `d_z` (calls/h) |
|---|---|---|
| Z1 | {A1} | 0.3 |
| Z2 | {A1, A2} | 0.6 |
| Z3 | {A2, A3} | 1.5 |
| Z4 | {A3} | 0.2 |

→ `c = (0.3, 0, 0.2)`, `g_12 = 0.6`, `g_23 = 1.5`, `g_13 = 0`. Weights: `λ = 20`, `P_A = P_C = P = 100`.

Variables (8 qubits), order `x_0..x_7` = (A1,C1), (A1,C2), (A1,C3), (A1,C4), (A2,C3), (A2,C4), (A3,C3), (A3,C4).

Objective coefficients `w_j t_ij − U_j`: −96, −63, −40, −16, −52, −15, −46, −18.
Linear `h` (adds `λ c_i`: +6 for A1, 0 for A2, +4 for A3): **−90, −57, −34, −10, −52, −15, −42, −14**.
Quadratic `J` (22 nonzero):
- 100 (same ambulance): (0,1) (0,2) (0,3) (1,2) (1,3) (2,3) (4,5) (6,7);
- 100 (same call, `g = 0`): (2,6) (3,7);
- 112 (same call, A1–A2: 100 + 20·0.6): (2,4) (3,5);
- 130 (same call, A2–A3: 100 + 20·1.5): (4,6) (5,7);
- 12 (A1–A2, different calls): (0,4) (0,5) (1,4) (1,5) (2,5) (3,4);
- 30 (A2–A3, different calls): (4,7) (5,6).

Results at λ = 20:
- 256 bitstrings, 27 feasible, 229 infeasible. QUBO energy + 300 equals raw-data cost on all 27 feasible strings (max difference 0).
- Constrained optimum: `x = 10000010` → A1→C1, A3→C3; `H* = −132`, `F* = 168` = weighted response 38 + unserved 120 (C2, C4) + 20 × 0.5 uncovered.
- Global QUBO minimum over all 256 strings = −132 (same string). Lowest infeasible: `11000010`, H = −89.
- Runner-up: A1→C1, A2→C3, H = −130. Third: A1→C1, A2→C3, A3→C4, H = −114.

At λ = 0: optimum `10001001` → A1→C1, A2→C3, A3→C4; `H* = −166`, `F* = 134` (response 44, unserved 90 for C2). Global QUBO minimum = −166. Coverage left: 2.6 calls/h uncovered (nothing covered).

Greedy nearest-available (calls in descending priority, nearest eligible idle unit): C1→A1 (6 min), C2→none (A1 taken), C3→A2 (4 min), C4→A3 (12 min). Identical to the λ = 0 optimum.

Greedy vs coverage-aware optimum at λ = 20:

| | Greedy / λ=0 optimum | Coverage-aware optimum |
|---|---|---|
| Assignment | A1→C1, A2→C3, A3→C4 | A1→C1, A3→C3 |
| Calls served | 3 | 2 (C4, w=1, deferred) |
| Weighted response | 44 | 38 |
| C3 response time | 4 min | 7 min |
| Unserved penalty | 90 | 120 |
| Uncovered demand | 2.6 calls/h | 0.5 calls/h |
| Total cost F (λ=20) | 186 | 168 |

Difference: 18 cost units; the gain comes from keeping A2 idle (protecting Z2 and Z3) at the price of deferring the lowest-priority call and 3 extra minutes for C3.

**Variant B (same ambulances and zones, calls C1 and C3 only — no deferral involved), 4 qubits.** Greedy and λ = 0 optimum: A1→C1, A2→C3 (weighted response 32, uncovered 0.9). λ = 20 optimum: A1→C1, **A3**→C3 (weighted response 38, uncovered 0.5), F = 48 vs greedy's 50. The coverage-aware choice sends the second-nearest unit: +3 minutes for C3 (+6 weighted minutes) to keep 0.4 calls/h covered. Switch occurs at λ = 15 (observed between 14.9 and 15.1). QUBO minimum equals constrained optimum at both λ (16 bitstrings, 7 feasible).

**Hand-checkable instance (2 ambulances × 3 calls), 5 qubits.** `w = (3, 2, 1)`, `τ = 20` → `U = (60, 40, 20)`, `Σ U = 120`. Times: A1: 5, 8, 6; A2: –, 4, 9 (A2 ineligible for C1). Zones: Za {A1} 0.5; Zb {A1,A2} 1.0; Zc {A2} 0.4 → `c = (0.5, 0.4)`, `g_12 = 1.0`. `λ = 10`, `P = 50`.
Variables: `x_0..x_4` = (A1,C1), (A1,C2), (A1,C3), (A2,C2), (A2,C3).
`w t − U`: −45, −24, −14, −32, −11. `h` (+5 for A1, +4 for A2): **−40, −19, −9, −28, −7**.
`J`: 50 on (0,1) (0,2) (1,2) (3,4); 60 on (1,3) (2,4) (same call: 50 + 10); 10 on (0,3) (0,4) (1,4) (2,3).

All 10 feasible assignments (hand check: `H = Σ h + 10` if both ambulances are used):

| x | Assignment | H | F = H + 120 |
|---|---|---|---|
| 10010 | A1→C1, A2→C2 | −40 − 28 + 10 = **−58** | 62 |
| 10000 | A1→C1 | −40 | 80 |
| 10001 | A1→C1, A2→C3 | −37 | 83 |
| 00010 | A2→C2 | −28 | 92 |
| 00110 | A1→C3, A2→C2 | −27 | 93 |
| 01000 | A1→C2 | −19 | 101 |
| 01001 | A1→C2, A2→C3 | −16 | 104 |
| 00100 | A1→C3 | −9 | 111 |
| 00001 | A2→C3 | −7 | 113 |
| 00000 | none | 0 | 120 |

Raw check of the optimum: response 3·5 + 2·4 = 23; unserved C3 = 20; uncovered 0.5 + 1.0 + 0.4 = 1.9, ×10 = 19; total 62. Lowest infeasible strings at P = 50: `11000` (−9), `10110` (−7), `10011` (−5). Provable bound for this instance: P > 45. Enumerated threshold at λ = 10: P > 4.5 (very low because the coverage couplings already penalise most double assignments) — an example of why tuned thresholds should not be trusted across instances. At λ = 0 the optimum is the same assignment (F = 43) and equals greedy; for λ ≥ 23 the optimum becomes A1→C1 only (C2, w = 2, deferred; switch algebraically at 32/1.4 = 22.86).

### Gaps
- Instances are synthetic and tiny; they demonstrate correctness of the algebra, not operational value.
- QAOA was not run on them (out of scope for this note).

---

## 9. Decoding and validation

### Takeaway
Fix one variable order (the sorted eligible-pair list), map variable `k` to qubit `k`, and read Qiskit count keys right-to-left. Validate every sample independently from raw data; reject infeasible samples and report the feasibility rate rather than repairing silently.

### Cited Findings
- Qiskit: "When displaying or interpreting a list of bits (or qubits) as a string, bit n−1 is the leftmost bit, and bit 0 is the rightmost bit"; e.g. an X on qubit 1 of two qubits gives counts key `'10'`. Circuit diagrams draw qubit 0 at the top. [LIT-SECONDARY: quoted from the search tool's rendering of the official guide; page not fetched directly] — [IBM Quantum docs, Bit ordering](https://quantum.cloud.ibm.com/docs/guides/bit-ordering)
- Glover et al.: generated solutions "can always be checked for feasibility". [LIT-VERIFIED] — [arXiv:1811.11538](https://arxiv.org/abs/1811.11538)

### Inferences
**Decoding rule [DESIGN].**
1. Build `E_list` = eligible pairs sorted by (ambulance index, call index); variable `k` ↔ `E_list[k]` ↔ qubit `k`. Auxiliary qubits (if any) come after all `x` qubits.
2. For a Qiskit counts key `s` of length `n` (all qubits measured into a same-order classical register): `x_k = int(s[n − 1 − k])`, i.e. reverse the string first.
3. Assignment = `{ E_list[k] : x_k = 1 }`; discard auxiliary bits.
- [COMPUTED] Main-instance optimum in variable order is `10000010`; the corresponding Qiskit key is `01000001`. Reading the key without reversing would decode as (A1,C2) and (A3,C4) — a feasible but wrong assignment, so this bug would not be caught by feasibility checks alone.
- Guard: a unit test that prepares a known basis state (e.g. X on qubit 0 only) and confirms the decoder returns `E_list[0]`. Custom classical-register mappings change the rule.

**Independent validation checklist [DESIGN]** (uses raw tables `t`, `w`, `U`, eligibility, zones — never the QUBO matrix):
1. Every selected pair is in `E` (capability, availability, optional `t ≤ T_max`).
2. Each ambulance appears in at most one selected pair.
3. Each call appears in at most one selected pair.
4. Recompute weighted response `Σ w_j t_ij`, unserved penalty `Σ_{unserved} U_j`.
5. Recompute coverage zone by zone: zone uncovered iff no *remaining* ambulance is in `N_z`; sum `d_z`.
6. `F = (4) + λ·(5)`; compare with QUBO energy + `Σ U_j` — must agree for feasible samples (agreement was exact on all feasible strings in my checks).
7. Policy rules (Section 11), e.g. no top-priority call left unserved while an eligible ambulance stays idle.
8. Compare `F` against the exact classical optimum; report optimality gap and whether the sample *is* the optimum.

**Infeasible samples [DESIGN, reasoning mine].** Default: reject, count, and report (a) the fraction of feasible shots and (b) the probability of the optimal string. If a repair is used, it must be deterministic, documented, applied identically to every method, and reported separately from raw results. Silent repair biases comparisons because the repair step is itself a classical optimiser: it converts arbitrary bitstrings into good assignments, so it can make a near-uniform sampler look competent, hides penalty mis-tuning, and inflates success probability relative to a classical baseline that received no such help. Energies of infeasible strings are not costs and must not enter averages reported as "objective value".

### Gaps
- The Qiskit guide was not fetched directly; wording is from the search summary. Version-specific primitives (Sampler V2 `BitArray`, etc.) may expose bits differently — check against the installed version.

---

## 10. Exact classical benchmark and complexity

### Takeaway
Benchmark with a linearised 0–1 program (valid for any cover-set size) or plain enumeration. The assignment part alone is polynomial; with pair-coverage terms the general problem is NP-hard (my reduction from Independent Set), but at prototype size it is trivial — 27 feasible assignments in the main instance — so no quantum advantage can be claimed.

### Cited Findings
- Kuhn's Hungarian method solves the assignment problem; it was later shown to be of polynomial complexity. [LIT-SECONDARY, search summary of INFORMS biography; bibliographic data verified] — [Kuhn 1955](https://doi.org/10.1002/nav.3800020109)
- Sahni & Gonzalez, "P-Complete Approximation Problems", J. ACM 23(3):555–565 (1976): quadratic assignment is among the problems whose approximation is also hard; surveys credit it with NP-hardness of QAP. [LIT-SECONDARY] — [doi:10.1145/321958.321975](https://doi.org/10.1145/321958.321975)
- Densest-k-subgraph is NP-hard because maximum clique reduces to it. [LIT-SECONDARY, search summary of survey] — ["A Survey on the Densest Subgraph Problem and Its Variants", arXiv:2303.14467](https://arxiv.org/abs/2303.14467)
- Megiddo, Zemel & Hakimi, "The maximum coverage location problem", SIAM J. Algebraic Discrete Methods 4(2):253–261 (1983). [Bibliographic data verified only] — [Megiddo's publication list](https://theory.stanford.edu/~megiddo/bio.html)
- Glover et al. treat the quadratic assignment problem as a QUBO application (Sec. 5.4). [LIT-VERIFIED, section heading] — [arXiv:1811.11538](https://arxiv.org/abs/1811.11538)

### Inferences
**Benchmark model [DESIGN/DERIVED]** (same objective `F` as the QUBO, no penalties):

`min Σ_{(i,j)∈E} w_j t_ij x_ij + Σ_j U_j (1 − Σ_{i∈E^j} x_ij) + λ Σ_z d_z v_z`
subject to
- `Σ_{j∈E_i} x_ij ≤ 1` for all `i`;
- `Σ_{i∈E^j} x_ij ≤ 1` for all `j`;
- `v_z ≥ Σ_{i∈N_z} D_i − (|N_z| − 1)` for all `z` with `N_z ≠ ∅`, where `D_i = Σ_{j∈E_i} x_ij`;
- `x_ij ∈ {0,1}`, `0 ≤ v_z ≤ 1`.

Since `d_z ≥ 0` and we minimise, `v_z` settles at `max(0, Σ D_i − |N_z| + 1) = Π_{i∈N_z} D_i`; this standard product linearisation is exact for any `|N_z|`, so the benchmark also covers the cubic case. For CP-SAT, scale `d_z`, `λ`, `w_j t_ij` to integers (e.g. ×10 or ×100). Equivalent 0–1 quadratic form for `|N_z| ≤ 2`: replace the last term by `λ(Σ c_i D_i + Σ g_ab D_a D_b)`. At prototype size, direct enumeration of feasible matchings is the simplest exact solver and is what I used.

**Complexity [DERIVED].**
- λ = 0: maximum-weight bipartite matching with rectangular, incomplete cost matrix — polynomial (Hungarian / min-cost flow).
- Approach A (linear `c_i`): still an assignment problem (add `λ c_i` to each cost) — polynomial.
- Approach B: objective contains `Σ g_ab D_a D_b`, products between *different ambulances'* decisions. Structurally this is a quadratic semi-assignment-type objective (each ambulance chooses one call or "stay") with additional per-call capacity constraints.
- NP-hardness sketch (mine, not from a source): given a graph `G` and integer `m`, create one ambulance per vertex, one zone with `d = 1` and `N_z = {a,b}` per edge, and `m` identical calls eligible for all ambulances with equal times and `U` large enough that exactly `m` ambulances are dispatched. The optimal loss is the number of edges inside the dispatched set, which is 0 iff `G` has an independent set of size `m`. Independent Set is NP-complete, so the coverage-augmented problem is NP-hard even with `|N_z| ≤ 2`. With arbitrary `|N_z|`, choosing which units to keep is a maximal-covering selection.
- Honest statement: NP-hard in the worst case as fleet size grows, but for 3 ambulances/4 calls there are 27 feasible assignments and brute force is instantaneous; real dispatch instances (tens of units, a handful of simultaneous calls) are also easy for MILP/CP-SAT. The prototype can demonstrate *correct encoding and decoding*, not speed-up.

### Gaps
- I did not find and read a source proving NP-hardness of the maximal covering location problem or of the quadratic semi-assignment problem; the search confirmed only bibliographic data and QAP/densest-k-subgraph hardness via summaries. The NP-hardness claim for the Q-Rescue model rests on my own reduction sketch and should be labelled as such.
- The Hungarian method's complexity bound (commonly O(n^3)) was not verified from a source this session.

---

## 11. Safety rules: hard vs soft

### Takeaway
Capability/availability eligibility must be structural (no variable). At-most-one constraints are penalty-encoded but must be enforced by post-hoc validation with rejection. Priority protection ("never defer a top-priority call for coverage") must be a hard rule outside the QUBO weights. Response time and coverage are the only soft terms.

### Cited Findings
- Andersson & Värbrand apply preparedness-based dispatch only to priority 2–3 calls; priority 1 always gets the closest available ambulance. [LIT-SECONDARY] — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Jagtenberg et al.'s heuristic always sends "an ambulance that will reach the incident in time, if possible", using coverage only to choose among those; the authors still expect decision makers to prefer closest-idle because of the response-time tail. [LIT-VERIFIED] — [Jagtenberg et al. 2017 manuscript](https://ir.cwi.nl/pub/24632/24632A.pdf)
- Montañez-Barrera et al. show penalty encodings can leave constraint-violating states below the optimum (worst case position 7 of 2^20), i.e. penalties alone do not guarantee feasibility of what is returned. [LIT-VERIFIED via ar5iv] — [arXiv:2211.13914](https://arxiv.org/abs/2211.13914)

### Inferences
| Rule | Treatment | Justification [DESIGN] |
|---|---|---|
| Capability (ALS vs BLS), unit availability, max allowable response time | **Hard, structural**: no variable for ineligible pairs | Cannot be violated by any sample; saves qubits |
| One call per ambulance; one ambulance per call | Penalty with provable `P`, **plus hard post-hoc validation and rejection** | A heuristic sampler returns non-ground states; the penalty shapes the distribution but does not filter it |
| Top-priority calls never deferred in favour of coverage | **Hard**: pre-assign them classically (closest eligible) and remove from the QUBO, or validate post hoc; additionally cap `λ` via `λ(c_i + Σ_b g_ib) < U_j − w_j t_ij` | [COMPUTED] in the main instance, λ > 180 leaves the w = 4 call unserved; even λ = 20 defers the w = 1 call. This behaviour is created purely by weights and must not be left to tuning |
| Response-time minimisation | Soft objective | Trade-off quantity |
| Residual coverage | Soft objective, applied only to lower-priority decisions | Mirrors the cited practice of restricting coverage-aware dispatch to non-urgent calls |
| Output of the quantum routine | Advisory only; fall back to exact classical/greedy result if validation fails | A simulator-based student prototype must not be presented as a dispatch decision system |

- Deferral must be shown explicitly in any demo ("call C4 left for next round") rather than hidden inside an objective value.

### Gaps
- No regulatory or clinical dispatch standard (e.g. response-time targets by acuity) was researched here; the priority-protection rule follows the cited OR papers' practice, not a verified clinical guideline.
