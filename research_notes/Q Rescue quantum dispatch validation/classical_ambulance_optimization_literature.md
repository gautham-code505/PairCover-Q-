# Classical (non-quantum) OR/ML literature on ambulance dispatch, relocation and coverage — adversarial notes for Q-Rescue

Notes compiled 9 October 2026. Verification legend used throughout:

- **[FT]** = full text (or author preprint full text) read for this note.
- **[ABS]** = only abstract / bibliographic record / publisher landing page accessed.
- **[SEC]** = content taken from a secondary restatement in another paper that I did read (named each time).
- **[CR]** = DOI resolved against the Crossref API on 9 Oct 2026 (authors, title, journal, volume, pages matched).
- **[MEM]** = standard textbook statement from my own background knowledge, NOT checked against the original text in this session. Treat as unverified until someone opens the paper.

Headline verdict for the judge-proofing exercise: **"dispatch that accounts for the future coverage/preparedness lost when an ambulance leaves its area" is an established classical idea, published at least since 2007 (Andersson & Värbrand), re-examined in 2011–2017 (Lee; Jagtenberg et al.), and still an active line in 2020–2026 (Carvalho et al. 2020; Guigues et al. 2022/2024/2026). Batch assignment of several ambulances to several queued calls as an assignment problem is also published (Lee 2014). Q-Rescue cannot claim either idea as new.**

---

## 1. Coverage and location models: original definitions, objectives, assumptions

### Takeaway
The six foundational models all exist exactly as the brief names them and their DOIs resolve. The MEXCLP marginal term d_i(1-q)q^(k-1) is verified from a full-text restatement and is already used, verbatim, as a "future coverage" proxy in real-time dispatch and relocation heuristics (Jagtenberg et al. 2015, 2017).

### Cited Findings

**Bibliographic verification (all [CR])**
- Toregas, Swain, ReVelle & Bergman (1971), "The Location of Emergency Service Facilities", Operations Research 19(6):1363–1373. Peer-reviewed article. [ABS] — [doi:10.1287/opre.19.6.1363](https://doi.org/10.1287/opre.19.6.1363)
- Church & ReVelle (1974), "The maximal covering location problem", Papers of the Regional Science Association 32(1):101–118. Peer-reviewed article. [ABS] — [doi:10.1007/BF01942293](https://doi.org/10.1007/BF01942293)
- Gendreau, Laporte & Semet (1997), "Solving an ambulance location model by tabu search", Location Science 5(2):75–88. Peer-reviewed article. [ABS] — [doi:10.1016/S0966-8349(97)00015-6](https://doi.org/10.1016/S0966-8349(97)00015-6)
- Daskin (1983), "A Maximum Expected Covering Location Model: Formulation, Properties and Heuristic Solution", Transportation Science 17(1):48–70. Peer-reviewed article. [ABS] — [doi:10.1287/trsc.17.1.48](https://doi.org/10.1287/trsc.17.1.48)
- ReVelle & Hogan (1989), "The Maximum Availability Location Problem", Transportation Science 23(3):192–200. Peer-reviewed article. [ABS] — [doi:10.1287/trsc.23.3.192](https://doi.org/10.1287/trsc.23.3.192)
- Larson (1974), "A hypercube queuing model for facility location and redistricting in urban emergency services", Computers & Operations Research 1(1):67–95. Peer-reviewed article. [ABS] — [doi:10.1016/0305-0548(74)90076-8](https://doi.org/10.1016/0305-0548(74)90076-8)
- Batta, Dolan & Krishnamurthy (1989), "The Maximal Expected Covering Location Problem: Revisited", Transportation Science 23(4):277–287 — the standard critique of MEXCLP's assumptions. [ABS] — [doi:10.1287/trsc.23.4.277](https://doi.org/10.1287/trsc.23.4.277)

**MEXCLP (Daskin 1983) — formula verified from a full-text restatement [SEC, FT of the restating paper]**
- Jagtenberg, Bhulai & van der Mei (2015) restate MEXCLP as follows: each ambulance is unavailable with a pre-determined probability q ("busy fraction"), "implicitly assumed" to be the same for all vehicles regardless of position; q "can be estimated by dividing the expected load of the system by the total number of available ambulances". For a node i with demand d_i within range of k ambulances, expected covered demand is E_k = d_i(1 − q^k), and "the marginal contribution of the kth ambulance to this expected value is E_k − E_{k−1} = d_i(1 − q)q^{k−1}" (attributed to Daskin). — [Jagtenberg et al. 2015 author preprint, CWI](https://ir.cwi.nl/pub/23338/23338B.pdf)
- Same source, MEXCLP integer program: maximize Σ_{i∈V} Σ_{k=1..p} d_i(1−q)q^{k−1} y_ik subject to Σ_{j∈W_i} x_j ≥ Σ_k y_ik for all i; Σ_j x_j ≤ |A|; x_j ∈ ℕ; y_ik ∈ {0,1}, where y_ik = 1 iff node i is within range of at least k ambulances, x_j = number of vehicles at base j, W_i = bases within the time threshold T of i. No ordering constraint y_ih ≥ y_ik is needed "since E_k − E_{k−1} is decreasing in k". — [Jagtenberg et al. 2015 preprint](https://ir.cwi.nl/pub/23338/23338B.pdf)
- Daskin's abstract-level framing: locate servers to maximize expected coverage of demand given that servers may be unavailable; assumptions are a common busy probability and independent server operation. — [RePEc record for Daskin 1983](https://ideas.repec.org/a/inm/ortrsc/v17y1983i1p48-70.html)
- Known weakness: Batta et al. (1989) relaxed those assumptions and report disagreement between MEXCLP-predicted expected coverage and a hypercube-based procedure. [ABS] — [doi:10.1287/trsc.23.4.277](https://doi.org/10.1287/trsc.23.4.277)
- Jagtenberg et al. list the "well-known imperfections": vehicles assumed to operate independently and busy fraction assumed identical for all vehicles; "these limitations also transfer to the dynamic usage of (MEXCLP) coverage". — [Jagtenberg et al. 2015 preprint](https://ir.cwi.nl/pub/23338/23338B.pdf)

**MCLP (Church & ReVelle 1974) — formulation from a secondary survey [SEC]**
- As restated by Tassone & Choudhury (2020, arXiv preprint, not peer-reviewed): maximize Σ_{i∈I} d_i y_i subject to Σ_{j∈J_i} x_j ≥ y_i for all i; Σ_j x_j ≤ p; x_j, y_i ∈ {0,1}; d_i is the weight of demand location i, y_i indicates whether i is covered. — [Tassone & Choudhury 2020, arXiv:2001.05288](https://arxiv.org/abs/2001.05288)

**Double Standard Model (Gendreau, Laporte & Semet 1997) [SEC + ABS]**
- Tassone & Choudhury restate the DSM objective as maximize Σ_i d_i y_i^2 (demand covered at least twice within the small radius), with constraints that every demand point is covered within the large radius, a fraction α of demand is covered within the small radius (Σ_i d_i y_i^1 ≥ α Σ_i d_i), Σ_{j∈J_i} x_j ≥ y_i^1 + y_i^2, and a point cannot be covered twice unless covered once. — [arXiv:2001.05288](https://arxiv.org/abs/2001.05288)
- A second secondary description: the DSM "maximizes the population covered by (at least) two EMS vehicles" and is the first model with two maximum waiting times r1 < r2. — search-result excerpt of [van Barneveld, Bhulai & van der Mei 2016](https://doi.org/10.1016/j.ejor.2015.12.022)
- The original abstract (IAOR record) says only that a double-coverage ambulance location model is proposed with a tabu search heuristic, tested on random and real data. — [IAOR record](https://iaorifors.com/paper/23945)

**LSCM, MALP, hypercube — [MEM] only, flagged**
- LSCM (Toregas et al. 1971) [MEM]: minimize the number of facilities Σ_j x_j subject to every demand point having at least one facility within a maximal service distance/time S (Σ_{j∈N_i} x_j ≥ 1), x_j binary; deterministic, ignores server busyness and demand weights. Not checked against the original text. — [doi:10.1287/opre.19.6.1363](https://doi.org/10.1287/opre.19.6.1363)
- MALP (ReVelle & Hogan 1989) [MEM]: maximize the demand covered within the time standard with reliability at least α; a chance constraint 1 − q^(number of covering servers) ≥ α is converted into a required integer number of covering servers b; MALP I uses a system-wide busy fraction, MALP II uses area-specific busy fractions. Not checked against the original. — [doi:10.1287/trsc.23.3.192](https://doi.org/10.1287/trsc.23.3.192)
- Hypercube (Larson 1974) [MEM]: a spatially distributed multi-server queueing model whose state is the busy/free status vector of N servers (2^N states, hence "hypercube"), with fixed dispatch preference lists per district; outputs include unit workloads, mean travel time and inter-district dispatch fractions; it is a descriptive (evaluation) model, not an optimizer. Not checked against the original. — [doi:10.1016/0305-0548(74)90076-8](https://doi.org/10.1016/0305-0548(74)90076-8)
- Corroboration that the hypercube is still the exact reference for small N: Hua & Zaman (2020) use Larson's hypercube for N = 5 and 10 units, and note that N = 15 would need a 31 × 2^15 = 1,015,808-state Bellman system. [FT] — [arXiv:2010.07513](https://arxiv.org/abs/2010.07513)

### Inferences
- MEXCLP gives Q-Rescue a ready-made, citable, closed-form definition of "future coverage": C(S) = Σ_i d_i (1 − q^{k_i(S)}), with k_i the number of still-idle ambulances within threshold of zone i. Using it is legitimate, but it must be attributed to Daskin (1983) and, in the dispatch setting, to Jagtenberg et al. (2015, 2017). It is not a Q-Rescue invention.
- Any honest write-up must carry over MEXCLP's two assumptions (independent servers, uniform busy fraction) as limitations.

### Gaps
- I did not read the original text of Toregas 1971, Church & ReVelle 1974, Gendreau et al. 1997, Daskin 1983, ReVelle & Hogan 1989 or Larson 1974 (paywalled). LSCM/MALP/hypercube statements above are [MEM]; the report writer should not print their formulas as "verified from the original" without opening the papers.
- Exact DSM constraint set (parameter names r1, r2, α, p_j per site) not confirmed against the 1997 paper.

---

## 2. Dispatch policies that deliberately do NOT send the closest unit in order to protect future coverage

### Takeaway
This is a mature classical sub-literature, not an open niche. Preparedness-based dispatch dates to Andersson & Värbrand (2007); the non-optimality of closest-unit dispatch dates to Carter, Chaiken & Ignall (1972). The best-known quantitative result (Jagtenberg et al. 2017) is double-edged: an MEXCLP-based dispatch rule cut late arrivals by 18% relative to closest-idle but raised mean response time by 37%, and the authors explicitly decline to claim it is practically preferable.

### Cited Findings

**Andersson & Värbrand (2007) — "Decision support tools for ambulance dispatch and relocation"**, Journal of the Operational Research Society 58(2):195–201. Peer-reviewed article. [CR][ABS + SEC] — [doi:10.1057/palgrave.jors.2602174](https://doi.org/10.1057/palgrave.jors.2602174)
- Problem/method: operational dispatch (which ambulance to send) and relocation; relocation objective is "to find new locations for some of the ambulances, to increase the preparedness"; preparedness is "a way of evaluating the ability to serve potential patients with ambulances now and in the future"; tested with a simulation model, reporting reduced patient waiting. — [RePEc abstract](https://ideas.repec.org/a/pal/jorsoc/v58y2007i2d10.1057_palgrave.jors.2602174.html)
- Formal definition as restated by Guigues, Kleywegt & Nascimento (2026) [SEC]: for zone ℓ, ψ_ℓ := (1/λ_ℓ) Σ_{a=1..A_ℓ} γ^a / t^a_ℓ, where the A_ℓ ambulances contributing to zone ℓ are indexed by increasing travel time t^1_ℓ ≤ t^2_ℓ ≤ …, the contribution weights satisfy γ^1 > γ^2 > …, and λ_ℓ is a weight proportional to demand in zone ℓ. — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
- Dispatch rule as restated by Guigues et al. (2022/2024) [SEC, FT of restating paper]: three priority levels; priority-1 calls get the closest available ambulance; for priority 2 and 3 calls "they dispatch the ambulance with expected travel time less than a specified threshold that will result in the least decrease in the minimum preparedness measure over all zones". Queue selection on reassignment is not specified in the original. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Overlap with Q-Rescue: essentially total at the conceptual level (immediate response vs. loss of future area preparedness). Limitation: heuristic; max–min aggregate; simulation only.

**Lee (2011) — "The role of preparedness in ambulance dispatching"**, JORS 62(10):1888–1897. Peer-reviewed. [CR][ABS + SEC] — [doi:10.1057/jors.2010.145](https://doi.org/10.1057/jors.2010.145)
- Abstract-level finding: considering preparedness in dispatching "can provide significant benefits in reducing response time but only when appropriately used". — [RePEc abstract](https://ideas.repec.org/a/pal/jorsoc/v62y2011i10d10.1057_jors.2010.145.html)
- As restated by Guigues et al.: Lee showed the Andersson–Värbrand preparedness rule "resulted in worse performance than the closest-available-ambulance rule", then proposed (i) dispatch the ambulance maximizing min_ℓ ψ_ℓ^{−a} / t^a_e (minimum post-dispatch preparedness divided by travel time to the emergency) and (ii) replacing the minimum by other aggregates (average; Gini-penalized averages). [SEC] — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371); formulas in [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
- Overlap: this is the explicit "balance immediate response against preparedness" trade-off as a single scalar score. Dataset/instances and exact numbers not accessed.

**Lee (2012) — "The role of centrality in ambulance dispatching"**, Decision Support Systems 54(1):282–291. Peer-reviewed. [CR][ABS + SEC] — [doi:10.1016/j.dss.2012.05.036](https://doi.org/10.1016/j.dss.2012.05.036)
- Proposes a "Centrality policy" that prioritizes calls by centrality in addition to closeness. — [IAOR record](https://iaorifors.com/paper/78695)
- Restated rule [SEC]: when an ambulance frees up, choose queued call e* ∈ argmax c_e^w / (1 + t^a_e), c_e a centrality measure (weighted degree, distance or betweenness) of queued call e. — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
- Related: Lee (2013) "Centrality-based ambulance dispatching for demanding emergency situations", JORS 64(4):611–618 [CR][ABS] — [doi:10.1057/jors.2012.72](https://doi.org/10.1057/jors.2012.72)

**Lee (2017) — "A new preparedness policy for EMS logistics"**, Health Care Management Science 20(1):105–114 (online 2015). Peer-reviewed. [CR][ABS + SEC] — [doi:10.1007/s10729-015-9340-4](https://doi.org/10.1007/s10729-015-9340-4)
- Restated rule [SEC]: dispatch the ambulance a minimizing (1 + t^a_e) · ( Σ_ℓ λ_ℓ (1 + min{ t^{a'}_ℓ : a' ∈ A_ℓ \ {a} }) )^w, where w ≥ 0 weighs preparedness against immediate travel time. — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
- Overlap: this is a one-parameter (w) trade-off between immediate response and post-dispatch demand-weighted nearest-remaining-ambulance time — structurally the same "λ-weighted" trade-off Q-Rescue proposes.

**Jagtenberg, Bhulai & van der Mei (2017) — "Dynamic ambulance dispatching: is the closest-idle policy always optimal?"**, Health Care Management Science 20(4):517–531 (online 20 May 2016). Peer-reviewed. [CR][ABS + SEC] — [doi:10.1007/s10729-016-9368-0](https://doi.org/10.1007/s10729-016-9368-0)
- Problem/objective: real-time choice of which idle ambulance to send; primary objective minimize the fraction of arrivals later than a threshold; MDP adaptable to mean response time. Methods: (a) an MDP with a state richer than the number of idle vehicles, tractable for moderate fleets; (b) a scalable heuristic. Result: in simulation of a large Dutch EMS region the heuristic reduces the fraction of late arrivals by 18% vs. closest-idle but increases average response time by 37%; the authors "do not claim" it is practically preferable. — [RePEc abstract](https://ideas.repec.org/a/kap/hcarem/v20y2017i4d10.1007_s10729-016-9368-0.html); [CWI repository record](https://ir.cwi.nl/pub/24632/)
- Heuristic as restated by Guigues et al. [SEC]: for each available ambulance that can reach the call within the threshold, compute the MEXCLP objective of the remaining available ambulances excluding it; dispatch the one leaving the largest MEXCLP value; if none can arrive in time, apply the same criterion over all available ambulances regardless of travel time. Queued calls are served first-come-first-served; idle ambulances return to home base; the MDP assumes each available ambulance is at its home base. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- A book-chapter version ("Optimal Ambulance Dispatching", in Markov Decision Processes in Practice, Springer 2017, pp. 269–291) reports a 13% reduction; do not mix the two figures. [CR][ABS] — [doi:10.1007/978-3-319-47766-4_9](https://doi.org/10.1007/978-3-319-47766-4_9); [RePEc](https://ideas.repec.org/h/spr/isochp/978-3-319-47766-4_9.html)
- Overlap: the heuristic is exactly "choose the ambulance whose departure loses the least future expected coverage" — the single-call special case of Q-Rescue's future-coverage term.

**Carter, Chaiken & Ignall (1972) — "Response Areas for Two Emergency Units"**, Operations Research 20(3):571–594. Peer-reviewed. [CR][ABS + SEC] — [doi:10.1287/opre.20.3.571](https://doi.org/10.1287/opre.20.3.571)
- Described by later authors as the first study of the optimal dispatch rule: a two-unit system in which response areas are characterized for minimizing average response time, i.e. the closest-unit boundary is not automatically optimal. [SEC] — [Hua & Zaman 2020, arXiv:2010.07513](https://arxiv.org/abs/2010.07513); [Guigues et al., arXiv:2203.16371](https://arxiv.org/abs/2203.16371)

**Bandara, Mayorga & McLay (2012, 2014); Mayorga, Bandara & McLay (2013)**
- Bandara et al. (2012), "Optimal dispatching strategies for emergency vehicles to increase patient survivability", Int. J. Operational Research 15(2):195. [CR][SEC] Continuous-time MDP, two priority levels, exponential service times; shows closest-available dispatch is suboptimal for small fleets; assumes no queue (calls arriving when all are busy go to an outside service) and return-to-home-base. — [doi:10.1504/IJOR.2012.048867](https://doi.org/10.1504/IJOR.2012.048867); description from [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Bandara et al. (2014), "Priority dispatching strategies for EMS systems", JORS 65(4):572–587. [CR][SEC] Simulation-evaluated priority-aware heuristic vs. closest-available, objective patient survival probability; a later review notes the optimal policy was found by full enumeration and that "a system with more than four units would take a significant amount of time". — [doi:10.1057/jors.2013.95](https://doi.org/10.1057/jors.2013.95); description from [arXiv:2010.07513](https://arxiv.org/abs/2010.07513)
- Mayorga et al. (2013), "Districting and dispatching policies for emergency medical service systems to improve patient survival", IIE Trans. Healthcare Systems Engineering 3(1):39–56. [CR][SEC] Districting plus four static dispatch policies, two priority levels, no queue. — [doi:10.1080/19488300.2012.762437](https://doi.org/10.1080/19488300.2012.762437)

**McLay & Mayorga (2013) — "A model for optimally dispatching ambulances to emergency calls with classification errors in patient priorities"**, IIE Transactions 45(1):1–24. Peer-reviewed. [CR][ABS] — [doi:10.1080/0740817X.2012.665200](https://doi.org/10.1080/0740817X.2012.665200)
- MDP; objective is long-run average utility defined as expected coverage of truly high-risk patients; compares optimal policies under over-/under-response classification strategies with the myopic closest-unit policy. — [RePEc abstract](https://ideas.repec.org/a/taf/uiiexx/v45y2013i1p1-24.html)
- Companion with equity constraints: McLay & Mayorga (2013), M&SOM 15(2):205–220. [ABS] — [RePEc](https://ideas.repec.org/a/inm/ormsom/v15y2013i2p205-220.html)

**Schmid (2012) — "Solving the dynamic ambulance relocation and dispatching problem using approximate dynamic programming"**, EJOR 219(3):611–621. Peer-reviewed. [CR][ABS + SEC] — [doi:10.1016/j.ejor.2011.10.043](https://doi.org/10.1016/j.ejor.2011.10.043)
- Real data from Vienna; "by deviating from the classical dispatching rules the average response time can be decreased from 4.60 to 4.01 minutes" (≈12.9%); stresses time-dependent travel times and request volumes. — [RePEc abstract](https://ideas.repec.org/a/eee/ejores/v219y2012i3p611-621.html)
- Conflict to note: Guigues et al. describe Schmid's ADP as restricting selection to closest-available and optimizing the reassignment decision (queued calls FCFS), whereas the abstract attributes the gain to "deviating from classical dispatching rules". The report writer should not assert which decision produced the 12.9% without the full text. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)

**Maxwell, Restrepo, Henderson & Topaloglu (2010) — "Approximate Dynamic Programming for Ambulance Redeployment"**, INFORMS Journal on Computing 22(2):266–281. Peer-reviewed. [CR][ABS] — [doi:10.1287/ijoc.1090.0345](https://doi.org/10.1287/ijoc.1090.0345)
- ADP with a parametric value-function approximation for redeployment; tested on EMS systems in two metropolitan areas with gains over static benchmark policies (abstract gives no numbers). A co-author's seminar abstract names Edmonton plus one other city. — [INFORMS page](https://pubsonline.informs.org/doi/fpi/10.1287/ijoc.1090.0345); [Henderson seminar abstract, MIT ORC](https://web.mit.edu/orc/www/archive/seminars/2009s/abs/Henderson_abs.html)
- Follow-up: Maxwell, Henderson & Topaloglu (2013), "Tuning ADP Policies for Ambulance Redeployment via Direct Search", Stochastic Systems 3(2):322–361 — post-decision-state formulation. [CR][ABS] — [doi:10.1287/10-SSY020](https://doi.org/10.1287/10-SSY020)
- Dispatch is closest-available in this line of work (per Guigues et al.); the "future" enters through the value function used for redeployment. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)

**Other directly overlapping works**
- Nasrollahzadeh, Khademi & Mayorga (2018), "Real-Time Ambulance Dispatching and Relocation", M&SOM 20(3):467–480. [CR; content not read] — [doi:10.1287/msom.2017.0649](https://doi.org/10.1287/msom.2017.0649)
- Carvalho, Captivo & Marques (2020), "Integrating the ambulance dispatching and relocation problems to maximize system's preparedness", EJOR 283(3):1064–1080. [CR][ABS] Integrated mathematical model + pilot-method heuristic; objective maximize system coverage using a time-preparedness measure; related thesis uses Lisbon EMS data and benchmarks against closest-available dispatch with return-to-home-base. — [doi:10.1016/j.ejor.2019.11.056](https://doi.org/10.1016/j.ejor.2019.11.056); [RePEc](https://ideas.repec.org/a/eee/ejores/v283y2020i3p1064-1080.html)
- Hua & Zaman (2020 preprint; 2022 Springer proceedings chapter), "Optimal Dispatch in Emergency Service System via Reinforcement Learning": average-cost MDP, post-decision states reduce the state space to 2^N, TD-learning; beats the myopic closest-unit policy, but by "an average of three seconds" of response time. [FT] — [arXiv:2010.07513](https://arxiv.org/abs/2010.07513); [doi:10.1007/978-3-030-75166-1_3](https://doi.org/10.1007/978-3-030-75166-1_3)
- Hua, Wang, Zhang & Zhou (2026, online 11 June 2026), "Near-Optimal Dispatch Policies for Emergency Medical Services", M&SOM. Lagrangian-relaxation dispatch policy with an O(1/θ) optimality gap in a scaling regime; New York City case study; outperforms common benchmarks. [CR][ABS] — [doi:10.1287/msom.2025.0529](https://doi.org/10.1287/msom.2025.0529)
- Guigues, Kleywegt & Nascimento (arXiv 2022, v3 Sept 2024, marked "Submitted to Operations Research"), "Operation of an ambulance fleet under uncertainty": two-stage rolling-horizon stochastic programs for selection and reassignment with queues, heterogeneous ambulances and hospital choice; Rio de Janeiro EMS data (> 2 years); outperforms six literature approaches on penalized response time P(a,c,w) = θ_c·w + 3600·M_ac. Preprint. [FT] — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Guigues, Kleywegt & Nascimento (arXiv Sept 2024, v3 Mar 2026, "Preprint submitted to Computers and Operations Research"), "New Heuristics for the Operation of an Ambulance Fleet under Uncertainty". Preprint. [FT of intro] — [arXiv:2409.09158](https://arxiv.org/abs/2409.09158)
- Guigues, Kleywegt & Nascimento (arXiv 6 May 2026), "Policies for the Operation of an Ambulance Fleet under Uncertainty based on a New Preparedness Metric": new preparedness metric = steady-state expected penalty rate of a per-station continuous-time Markov chain; added to the selection/reassignment objective as Γ·Σ_b ψ̄_b; a linearized version uses marginal changes s⁺/s⁻ of the metric per station; benchmarked against closest-available, Andersson–Värbrand, Lee 2011/2014/2017, Mayorga 2013, Bandara 2014, Jagtenberg 2017 and Carvalho et al. on Rio de Janeiro data (Jan 2016–Feb 2018). Reported: best mean allocation cost for nearly all fleet sizes; offline Markov pre-computation grows from 0.70 s (6 ambulances) to 346,000 s (16 ambulances); online decisions 0.19–4.11 ms. Preprint; [FT via HTML, first ~80% read]. — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)

### Inferences
- Q-Rescue's sentence "risk-aware ambulance assignment that balances immediate emergency response against the loss of future geographic emergency coverage" describes, almost word for word, the Andersson–Värbrand/Lee preparedness line and the Jagtenberg MEXCLP dispatch heuristic. The only defensible novelty is in (a) the solver/encoding (QUBO + QAOA) and possibly (b) a specific batch formulation with a pairwise coverage-interaction term (see Section 9) — and even (b) is close to Lee (2014) and Guigues et al. (2026).
- A judge who knows Jagtenberg (2017) will ask: "Your policy protects coverage — what happens to mean response time?" The published answer is that it can get much worse (+37%). Lee (2011) further shows a naive preparedness rule can underperform closest-idle outright.
- Realistic effect sizes for smarter dispatch are small to moderate: 3 seconds (Hua & Zaman), ~1% more calls served (Marla et al., Section 7), 13–18% fewer late arrivals with a response-time penalty (Jagtenberg), ~13% mean response time (Schmid, combined dispatch + relocation).

### Gaps
- Original equations, instances and numeric tables of Andersson & Värbrand (2007), Lee (2011, 2012, 2017), Bandara et al., McLay & Mayorga, Schmid and Maxwell et al. were not read (paywalled). Formulas above are restatements by Guigues et al.; the γ weights and the exact threshold rule should be confirmed in the 2007 paper before being printed as "the" definition.
- Jagtenberg et al. (2017): fleet size, number of bases and absolute late-arrival percentages for the dispatch paper were not retrieved (only the 18%/37% relative figures).
- Whether the "risk-aware" qualifier in Q-Rescue means CVaR/variance-type risk is undefined by the team; I found CVaR used for equity in a 2025 thesis (Section 7) but did not find a paper titled as risk-averse (CVaR) real-time dispatch. That absence is from a limited search, not evidence of novelty.

---

## 3. Dynamic relocation / redeployment, including 2019–2026 reinforcement learning

### Takeaway
Real-time relocation has a 25-year classical lineage (DDSM 2001, MECRP 2006, DMEXCLP 2015, compliance tables, ADP), and since 2019 a deep-RL branch. A 2023 scoping review found 21 studies, mostly mathematical models, with no study reporting patient outcomes or real-life effects.

### Cited Findings
- Gendreau, Laporte & Semet (2001), "A dynamic model and parallel tabu search heuristic for real-time ambulance relocation", Parallel Computing 27(12):1641–1653. [CR][SEC] The dynamic double standard model (DDSM^t) is solved at each instant a call is registered; its objective maximizes double coverage while relocation costs act as a penalty. — [doi:10.1016/S0167-8191(01)00103-X](https://doi.org/10.1016/S0167-8191(01)00103-X); description from search excerpt of [van Barneveld et al. 2016](https://doi.org/10.1016/j.ejor.2015.12.022)
- Gendreau, Laporte & Semet (2006), "The maximal expected coverage relocation problem for emergency vehicles", JORS 57(1):22–28. [CR; content not read] — [doi:10.1057/palgrave.jors.2601991](https://doi.org/10.1057/palgrave.jors.2601991)
- Jagtenberg, Bhulai & van der Mei (2015), "An efficient heuristic for real-time ambulance redeployment", Operations Research for Health Care 4:27–35. Peer-reviewed; author preprint read. [CR][FT] — [doi:10.1016/j.orhc.2015.01.001](https://doi.org/10.1016/j.orhc.2015.01.001); [preprint](https://ir.cwi.nl/pub/23338/23338B.pdf)
  - DMEXCLP rule: when an ambulance becomes idle, send it to the base w maximizing Σ_{i∈V} d_i(1−q)q^{k(i,w,n)−1}, where k counts idle ambulances (by destination) within threshold of i including the candidate base; decision is taken only when a vehicle becomes idle, so the number of trips equals that of a static policy.
  - Instance: Utrecht region, 19 ambulances, 19 bases, 217 four-digit postal-code demand nodes, d_i = fraction of inhabitants, legal target 15 min with 3 min for call handling → T = 12 min driving. Calls with no idle ambulance go into a first-come-first-served queue.
  - Results: 7.8% late arrivals vs. 9.5% for a benchmark static policy — "a 16.8% relative improvement"; a naive greedy-coverage alternative sometimes performed worse than the static solution.
  - Stated limitations: heuristic, not exact; inherits MEXCLP independence and uniform-busy-fraction assumptions.
- van Barneveld, Bhulai & van der Mei (2016), "The effect of ambulance relocations on the performance of ambulance service providers", EJOR 252(1):257–269. [CR; content not read beyond search excerpt] — [doi:10.1016/j.ejor.2015.12.022](https://doi.org/10.1016/j.ejor.2015.12.022)
- van Barneveld, Bhulai & van der Mei (2017), "A dynamic ambulance management model for rural areas", Health Care Management Science 20(2):165–186. [CR; content not read] — [doi:10.1007/s10729-015-9341-3](https://doi.org/10.1007/s10729-015-9341-3)
- van Buuren, Jagtenberg, van Barneveld, van der Mei & Bhulai (2018), "Ambulance Dispatch Center Pilots Proactive Relocation Policies to Enhance Effectiveness", Interfaces 48(3):235–246 — a real dispatch-centre pilot. [CR; content not read] — [doi:10.1287/inte.2017.0936](https://doi.org/10.1287/inte.2017.0936)
- Alanis, Ingolfsson & Kolfal (2013), "A Markov Chain Model for an EMS System with Repositioning", Production and Operations Management 22(1):216–231 (compliance tables). [CR; content not read] — [doi:10.1111/j.1937-5956.2012.01362.x](https://doi.org/10.1111/j.1937-5956.2012.01362.x)
- Enayati, Mayorga, Rajagopalan & Saydam (2018), "Real-time ambulance redeployment approach to improve service coverage with fair and restricted workload for EMS providers", Omega 79:67–80. [CR; content not read] — [doi:10.1016/j.omega.2017.08.001](https://doi.org/10.1016/j.omega.2017.08.001)
- Ji, Zheng, Wang & Li (2019), "A Deep Reinforcement Learning-Enabled Dynamic Redeployment System for Mobile Ambulances", Proc. ACM IMWUT 3(1):1–20. Peer-reviewed. [CR][ABS] A "deep score network" balances each station's dynamic factors into one score, trained by deep RL; real-data experiments claim gains over baselines. (Note: the fourth author is Li and third is Wang — the brief's "Ji et al. 2019" is correct but do not cite as "Ji, Zheng, Yang".) — [doi:10.1145/3314402](https://doi.org/10.1145/3314402)
- Liu, Li, Zou, Huang & Fu (2020), "Ambulance Dispatch via Deep Reinforcement Learning", SIGSPATIAL '20, pp. 123–126 (4-page short paper). Peer-reviewed short paper. [CR][FT] City gridded, 5-minute windows; each available ambulance is an agent (ambulances of the same centre share a Q-network); method MAQR = multi-agent Q-network with experience replay; simulator calibrated on real data; baselines are random, location-based (nearest request), time-based and request-based allocation plus MAQ without replay; metrics are normalized overall waiting time and normalized request answer rate; MAQR is best on both (best row of Table 2 ≈ 85 normalized waiting time and ≈ 93% answer rate vs. 100 and ≈ 81% for the reference baseline — row labels in the extracted table were misaligned, so treat exact row attribution as unverified). No comparison with OR baselines such as MEXCLP/preparedness rules. — [doi:10.1145/3397536.3422204](https://doi.org/10.1145/3397536.3422204); [author PDF](https://www.cs.ucf.edu/~czou/research/SigSpatial20_Ambulance_Dispatch.pdf)
- Tluli, Badawy, Salem, Hardan, Chauhan & Alinier (2024), "A Dynamic Redeployment System for Mobile Ambulances in Qatar, Empowered by Deep Reinforcement Learning", IWCMC 2024, pp. 980–985. Conference paper. [CR][ABS] A related TRID record reports a 21.55% reduction in average response time versus actual operations on Qatar data (comparison against real operations, not against other algorithms). — [doi:10.1109/IWCMC61514.2024.10592430](https://doi.org/10.1109/IWCMC61514.2024.10592430); [TRID record](https://trid.trb.org/View/2685733)
- Rautenstrauß & Schiffer (arXiv, 14 Mar 2025), "Optimization-Augmented Machine Learning for Vehicle Operations in Emergency Medical Services": learns an online dispatch + redeployment policy by imitating full-information solutions via a combinatorial-optimization-augmented ML pipeline; San Francisco 911 data; mean response time reduced by up to 30% vs. online benchmarks reflecting industry practice; runtime savings up to 87.9% vs. training-time augmentation. Preprint. [ABS] — [arXiv:2503.11848](https://arxiv.org/abs/2503.11848)
- Becker, Kurland, Höglund & Hugelius (2023), "Dynamic ambulance relocation: a scoping review", BMJ Open 13(12):e073394. Peer-reviewed. [CR][ABS] 21 papers included, mostly mathematical models; "no study reported on either positive or negative patient outcomes or real-life chain effects". — [doi:10.1136/bmjopen-2023-073394](https://doi.org/10.1136/bmjopen-2023-073394); [DOAJ record](https://doaj.org/article/a8201c42fce1419d9e5076e23a3a8408)

### Inferences
- RL papers generally benchmark against weak heuristics (random, nearest) and rarely against the OR state of the art; the same criticism would apply to a QAOA demo benchmarked only against closest-idle.
- Relocation and dispatch are routinely treated jointly (Schmid; Carvalho et al.; Guigues et al.; Rautenstrauß & Schiffer). A dispatch-only snapshot is a strictly narrower problem than the current classical frontier.

### Gaps
- DDSM/MECRP objective functions not verified against the original papers.
- I did not find, in this search, a 2025–2026 peer-reviewed deep-RL ambulance paper with a head-to-head comparison against DMEXCLP/ADP; several 2024–2025 items are theses or preprints (Qatar University thesis; Princeton thesis; SSRN preprint by John & Ahsun 2025, [doi:10.2139/ssrn.5311633](https://doi.org/10.2139/ssrn.5311633), title only).
- BMJ Open full text returned HTTP 403; only the abstract-level conclusions are recorded.

---

## 4. Batch / simultaneous-call assignment, mass-casualty dispatch, handling of unserved or queued calls

### Takeaway
Yes — assigning several ambulances to several waiting calls as an assignment problem is published (Lee 2014), and optimization models that jointly assign ambulances to a new call plus queued calls with "at most one ambulance per call / at most one call per ambulance" constraints and a preparedness term in the objective exist (Guigues et al. 2022–2026). Mass-casualty dispatch is a separate MIP literature.

### Cited Findings
- Lee (2014), "Role of Parallelism in Ambulance Dispatching", IEEE Transactions on Systems, Man, and Cybernetics: Systems 44(8):1113–1122. Peer-reviewed. [CR][SEC] — [doi:10.1109/TSMC.2013.2296280](https://doi.org/10.1109/TSMC.2013.2296280)
  - Restated by Guigues et al. (2026): solves one assignment problem over available and busy ambulances and queued calls, maximizing Σ c_e^w x_{a,e} / (1 + t^a_e) subject to one-to-one constraints. — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
  - Restated by Guigues et al. (2024/2026): "a rule that takes both available and busy ambulances into account when making ambulance dispatch decisions". — [arXiv:2409.09158](https://arxiv.org/abs/2409.09158)
- Guigues et al. (2026) selection problem: variables x(a,i) assign ambulances to the new call and to queued calls and y(a,b) send ambulances to stations; each station-based ambulance serves at most one emergency, each emergency gets at most one ambulance; preparedness enters the objective as Γ·Σ_b ψ̄_b; "Version 1 is nonlinear", "Version 2 linearizes it" via per-station marginal changes. Calls may be deliberately left in the queue. — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
- Guigues et al. (2022/2024) on how the literature treats unserved calls: "many existing models ignore the possibility of a queue of waiting emergencies"; Bandara et al. and Mayorga et al. assume an outside service handles calls when all ambulances are busy (no queue); Li & Saydam (2016) assume the call is lost; Jagtenberg et al. (2015, 2017) and Schmid (2012) use a first-come-first-served queue; Lee (2011) sends a newly freed ambulance to the closest queued call. Their own models carry explicit queue flow-balance constraints and a per-period penalty for each call waiting in queue. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Repoussis, Paraskevopoulos, Vazacopoulos & Hupert (2016), "Optimizing emergency preparedness and resource utilization in mass-casualty incidents", EJOR 255(2):531–544. Peer-reviewed. [CR][ABS] MIP for combined ambulance dispatching, patient-to-hospital assignment and treatment ordering; hierarchical objectives (overall response time, total flow time); hypothetical scenario with up to 150 trauma patients. — [doi:10.1016/j.ejor.2016.05.047](https://doi.org/10.1016/j.ejor.2016.05.047); accepted manuscript at [City Research Online](https://openaccess.city.ac.uk/id/eprint/19862/)
- Chang, Chen, Lee & Chang (2025; online 18 Mar 2024), "Stochastic ambulance dispatching and routing in mass casualty incident under road vulnerability", JORS 76(1):34–60. Peer-reviewed. [CR][ABS] Two-stage stochastic mixed-integer nonlinear program maximizing the expected number of survivors; sample average approximation + column-generation heuristic. — [doi:10.1080/01605682.2024.2325051](https://doi.org/10.1080/01605682.2024.2325051); [RePEc](https://ideas.repec.org/a/taf/tjorxx/v76y2025i1p34-60.html)
- Sudtachat, Mayorga & McLay (2014), "Recommendations for dispatching emergency vehicles under multitiered response via simulation", International Transactions in Operational Research 21(4):581–617. Peer-reviewed. [CR][ABS] Multiple-unit dispatch to multiple call priorities; objective survival probability of life-threatening patients; priority-aware dispatch beats closest-unit. — [doi:10.1111/itor.12083](https://doi.org/10.1111/itor.12083)
- A KAIST thesis notes that dispatching multiple ambulances to an MCI potentially leads "to significant capacity loss for future EMS demands" and couples dispatch quantity with relocation of idle units. Thesis; [ABS]. — [KAIST repository](https://dspace.kaist.ac.kr/handle/10203/222083?mode=full)
- Aldossary & Coates (2019) coordinate several simultaneous MCIs (ambulance-to-casualty and casualty-to-hospital allocation with hospital capacities) using a neighbourhood search. Conference chapter; [ABS]. — [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-030-34960-8_15)

### Inferences
- A batch assignment with only a linear cost per (ambulance, call) pair is the classical linear assignment problem — polynomially solvable (Hungarian/auction algorithms). A judge will reasonably ask why a quantum heuristic is needed for a problem that is in P. The batch formulation becomes hard (quadratic semi-assignment–like) only when the objective has genuine interaction terms between different ambulances' departures (see Section 9).
- Unserved calls: literature offers four conventions (FCFS queue; lost call; external responder; explicit queue variables with waiting penalties). Q-Rescue must state which one it uses; a hard "every call must be served" constraint is infeasible whenever calls outnumber idle ambulances, so a penalized "unserved" slack per call is the standard device.

### Gaps
- Lee (2014) original text not read; the assignment formulation is a restatement. I did not find a paper explicitly framing routine (non-MCI) simultaneous dispatch as a generalized assignment problem (GAP) with capacity; absence is from a limited search.
- No source was found (in this search) quantifying how often truly simultaneous calls occur in routine EMS, which determines whether a "batch" is realistic outside MCIs or queue build-up.

---

## 5. Survey papers that anchor the review

### Takeaway
Three surveys in the brief verify cleanly; 2022–2026 additions are a 2022 deployment review, a 2022 emergency-management ML/OR review, and the 2023 BMJ Open scoping review. I found no dedicated 2024–2026 peer-reviewed survey of ML/RL for ambulance dispatch.

### Cited Findings
- Brotcorne, Laporte & Semet (2003), "Ambulance location and relocation models", EJOR 147(3):451–463. [CR; content not read] — [doi:10.1016/S0377-2217(02)00364-8](https://doi.org/10.1016/S0377-2217(02)00364-8)
- Aringhieri, Bruni, Khodaparasti & van Essen (2017), "Emergency medical services and beyond: Addressing new challenges through a wide literature review", Computers & Operations Research 78:349–368. [CR; content not read] — [doi:10.1016/j.cor.2016.09.016](https://doi.org/10.1016/j.cor.2016.09.016)
- Bélanger, Ruiz & Soriano (2019), EJOR 272(1):1–23. [CR][ABS] Reviews static location briefly and concentrates on tactical/operational decisions (location, relocation, dispatching) and their interaction; highlights uncertainty, dynamism, equity and patient medical outcomes. — [doi:10.1016/j.ejor.2018.02.055](https://doi.org/10.1016/j.ejor.2018.02.055); [RePEc](https://ideas.repec.org/a/eee/ejores/v272y2019i1p1-23.html); earlier open working paper [CIRRELT-2015-28](https://www.cirrelt.ca/DocumentsTravail/CIRRELT-2015-28.pdf)
- Reuter-Oppermann, van den Berg & Vile (2017), "Logistics for Emergency Medical Service systems", Health Systems 6(3):187–208. [CR; content not read] — [doi:10.1057/s41306-017-0023-x](https://doi.org/10.1057/s41306-017-0023-x)
- Neira-Rodado, Escobar-Velasquez & McClean (2022), "Ambulances Deployment Problems: Categorization, Evolution and Dynamic Problems Review", ISPRS Int. J. Geo-Information 11(2):109. [CR][ABS] Identifies gaps in forecasting, simulation, heterogeneous fleets, robustness and real-time solution speed. — [doi:10.3390/ijgi11020109](https://doi.org/10.3390/ijgi11020109)
- Mukhopadhyay, Pettet, Vazirizade, Lu, Jaimes, El Said, Baroud, Vorobeychik, Kochenderfer & Dubey (2022), "A Review of Incident Prediction, Resource Allocation, and Dispatch Models for Emergency Management", Accident Analysis & Prevention 165:106501. [CR][ABS] Frames the field as "spatio-temporal decision making under uncertainty" across prediction, detection, allocation and dispatch. — [doi:10.1016/j.aap.2021.106501](https://doi.org/10.1016/j.aap.2021.106501); [arXiv:2006.04200](https://arxiv.org/abs/2006.04200)
- Becker et al. (2023) scoping review — see Section 3. — [doi:10.1136/bmjopen-2023-073394](https://doi.org/10.1136/bmjopen-2023-073394)
- Tassone & Choudhury (2020), "A Comprehensive Survey on the Ambulance Routing and Location Problems" — arXiv preprint (not peer-reviewed), useful for restated formulations only. [FT partial] — [arXiv:2001.05288](https://arxiv.org/abs/2001.05288)
- A Winter Simulation Conference 2022 tutorial covers simulation for real-time dispatching, ED selection and redeployment. [title/abstract only] — [WSC 2022 paper](https://informs-sim.org/wsc22papers/019.pdf)

### Inferences
- The surveys consistently present "dispatching rules other than closest-idle" and "preparedness" as standard categories; citing Bélanger et al. (2019) is the simplest way to show the team knows this.

### Gaps
- Contents of Brotcorne (2003), Aringhieri (2017), Reuter-Oppermann (2017) not read; only their existence and bibliographic data are verified.
- No 2024–2026 survey specific to ML/RL ambulance dispatch was found.

---

## 6. Emergency demand forecasting: methods, realistic accuracy, baselines, India

### Takeaway
Fine-grained ambulance demand is extremely sparse (96–99.6% of 1 km² cell-hours have zero calls), so city-wide hourly volume is forecastable with classical time-series models while zone-hour counts are mostly noise; improvements of recent deep models over the "MEDIC" historical-average industry baseline are real but modest (≈10% MSE at 2.5 km × 8 h). I found no peer-reviewed Indian spatio-temporal ambulance-demand forecasting study.

### Cited Findings
- Channouf, L'Ecuyer, Ingolfsson & Avramidis (2007), "The application of forecasting techniques to modeling emergency medical system calls in Calgary, Alberta", Health Care Management Science 10(1):25–45. [CR][SEC] ARMA-type time-series models of total call volume in Calgary; using call volumes of previous hours improves hourly forecasts. — [doi:10.1007/s10729-006-9006-3](https://doi.org/10.1007/s10729-006-9006-3); description from [arXiv:1606.05363](https://arxiv.org/abs/1606.05363) and [arXiv:2306.04994](https://arxiv.org/abs/2306.04994)
- Matteson, McLean, Woodard & Henderson (2011), "Forecasting emergency medical service call arrival rates", Annals of Applied Statistics 5(2B). [CR][SEC] Hourly factor model for call arrival rates. — [doi:10.1214/10-AOAS442](https://doi.org/10.1214/10-AOAS442)
- Setzler, Saydam & Park (2009), "EMS call volume predictions: A comparative study", Computers & Operations Research 36(6):1843–1851. [CR][SEC] MLP with time-of-day, day-of-week, month and season inputs on discretized space-time; per Zhou it "fails to improve the accuracy over the industry practice". — [doi:10.1016/j.cor.2008.05.010](https://doi.org/10.1016/j.cor.2008.05.010); description from [arXiv:1606.05363](https://arxiv.org/abs/1606.05363)
- Zhou, Matteson, Woodard, Henderson & Micheas (2015), "A Spatio-Temporal Point Process Model for Ambulance Demand", JASA 110(509):6–15 (time-varying Gaussian mixture, Toronto). [CR][SEC] — [doi:10.1080/01621459.2014.941466](https://doi.org/10.1080/01621459.2014.941466)
- Zhou & Matteson (2015 preprint), "Predicting Ambulance Demand: a Spatio-Temporal Kernel Approach" (Toronto). Preprint. — [arXiv:1507.00364](https://arxiv.org/abs/1507.00364)
- Zhou & Matteson (2016), "Predicting Melbourne ambulance demand using kernel warping", Annals of Applied Statistics 10(4):1977–1996. [CR][ABS] — [doi:10.1214/16-AOAS961](https://doi.org/10.1214/16-AOAS961)
- Zhou (2016 preprint), "Predicting Ambulance Demand: Challenges and Methods". Preprint; read via ar5iv. [FT via summary] — [arXiv:1606.05363](https://arxiv.org/abs/1606.05363)
  - Sparsity: Toronto averages 23 calls/hour and 96% of 1-km² cells have zero calls in any hour; Melbourne averages 37 calls/hour and 99.6% of cells have none.
  - Industry baseline ("MEDIC", Charlotte-Mecklenburg): for a 1-km² cell and hour, average 20 historical counts — same hour over the preceding 4 weeks for the past 5 years; Toronto EMS uses a similar average of 4 counts.
  - Data: Toronto 391,296 priority events 2007–2008; Melbourne 696,975 events 2011–2012; hourly periods; continuous space.
  - Mean negative test log-likelihood (lower is better): Toronto — GMM 6.07–6.15, stKDE 6.10–6.11, naive KDE 6.87, MEDIC 8.64; Melbourne — GMM 7.87–7.96, kernel warping 7.53–7.56, naive KDE 8.14, MEDIC 10.11.
- Rautenstrauß & Schiffer (arXiv June 2023; published 2026), "Ambulance demand prediction via convolutional neural networks", Operations Research, Data Analytics and Logistics 46:200497. [CR][FT of preprint] — [doi:10.1016/j.ordal.2025.200497](https://doi.org/10.1016/j.ordal.2025.200497); [arXiv:2306.04994](https://arxiv.org/abs/2306.04994)
  - Seattle 911 "Medic Response" incidents 2020–2021; 8-hour intervals; 11 × 6 grid of ≈ 2.5 × 2.5 km subregions; external features (weather, events, holidays); 60/20/20 split; MSE loss.
  - "The CNN architecture outperforms the incumbent MLP, Medic method, random forest, and decision tree by 9.83%, 9.98%, 11.26%, and 14.84%" (MSE). Their literature review also notes work showing "simple time series models can outperform more expensive, complex models" for hourly incidents.
- A 2023 survey of spatio-temporal GNNs for urban computing lists ambulance demand prediction as an application area. Preprint/survey. — [arXiv:2303.14483](https://arxiv.org/abs/2303.14483)
- India: the only forecasting-type item found is a 2020 EasyChair preprint (not peer-reviewed) on rising EMS demand across Indian states using cluster analysis and panel regression — state level, not zone-hour. — [EasyChair preprint](https://easychair.org/publications/preprint/ztdv)

### Inferences
- A defensible Q-Rescue demand input is: zone-level Poisson rates estimated as historical averages by zone × hour-of-week (the MEDIC-style baseline), with zones coarse enough (several km², multi-hour windows) to avoid mostly-zero counts. Claiming an accurate fine-grained forecaster would be the fragile part of the pitch; a ~10% MSE gain is what a tuned CNN buys over the historical average at 2.5 km × 8 h.
- Because the "future coverage" term is weighted by d_i, forecast error propagates directly into the dispatch objective; a sensitivity analysis on d_i is expected.

### Gaps
- Original numeric accuracy (MAPE/RMSE) of Channouf (2007), Matteson (2011) and Setzler (2009) was not retrieved; I have only secondary characterizations.
- No peer-reviewed Indian spatio-temporal ambulance call forecasting study was found; no public zone-level 108 call dataset was identified in this search.
- I found no 2024–2026 paper that directly compares a spatio-temporal GNN against an hour-of-week × zone historical average for ambulance calls.

---

## 7. Multi-objective, stochastic and robust ambulance optimization (2020–2026) and Indian-context studies

### Takeaway
Stochastic and distributionally robust location/dispatch models are an active 2022–2026 theme. The strongest Indian study (Marla, Krishnan & Deo, IISE Transactions 2021) reports that changing dispatch policy or reallocating ambulances yields only about 1% more successfully served calls, while base redesign is worth an 8.6% fleet increase — a direct challenge to any Indian-impact claim built on dispatch optimization alone.

### Cited Findings
- Wu, Jiang, Liang & Zhou (2024), "Multi-period distributionally robust emergency medical service location model with customized ambiguity sets", Transportation Research Part E 181:103379. [CR; content not read] — [doi:10.1016/j.tre.2023.103379](https://doi.org/10.1016/j.tre.2023.103379)
- OpenEMS (arXiv 2022): open-source two-stage stochastic and robust optimization for ambulance location and routing on Austin-Travis County EMS data; in simulation the stochastic approach generally gave better mean response time than the robust one, and the robust solution concentrated more ambulances at single stations. Preprint. [ABS] — [arXiv:2201.11208](https://arxiv.org/abs/2201.11208)
- Gago-Carro (doctoral thesis defended December 2025, BCAM/UPV-EHU): distributionally robust framework for travel-time uncertainty compared with stochastic and robust optimization; two-stage 0–1 stochastic MILP for relocation/expansion; hierarchical model using CVaR for equity; validated by discrete-event simulation on Basque public EMS. Thesis announcement; associated paper described as under review. [ABS] — [BCAM announcement](https://www.bcamath.org/eu/node/14031)
- Toro-Díaz, Mayorga, Chanta & McLay (2013), "Joint location and dispatching decisions for Emergency Medical Services", Computers & Industrial Engineering 64(4):917–928 (outside the 2020–2026 window; representative joint model). [CR; content not read] — [doi:10.1016/j.cie.2013.01.002](https://doi.org/10.1016/j.cie.2013.01.002)
- Guigues et al. (2022–2026) two-stage stochastic programs and multi-attribute cost (response time × urgency + ambulance/crew suitability penalty) — see Sections 2 and 4. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Chang et al. (2025) two-stage stochastic MINLP for MCI dispatch — see Section 4. — [doi:10.1080/01605682.2024.2325051](https://doi.org/10.1080/01605682.2024.2325051)

**India**
- Marla, Krishnan & Deo (2021; online 24 Sept 2020), "Managing EMS systems with user abandonment in emerging economies", IISE Transactions 53(4):389–406. Peer-reviewed. [CR][ABS] Models caller abandonment/wait tolerance; calibrated on a major Indian metropolitan city where 81.3% of calls were served without abandonment; modifying dispatch policies or reallocating ambulances gives "relatively small gains in successfully served calls (around 1%)"; redesigning bases with the current fleet is equivalent to an 8.6% fleet increase at current bases. — [doi:10.1080/24725854.2020.1802086](https://doi.org/10.1080/24725854.2020.1802086); [ISB research directory](https://www.isb.edu/faculty-and-research/research-directory/managing-ems-systems-with-user-abandonment-in-emerging-economies)
- Delhi: TRB 2020 presentation (IIT Delhi / Portland State), "Ambulance Location Optimization Incorporating O-D Travel Time Variability: A Case Study of Delhi", using Delhi CATS call records Jan–Jul 2018; slides report the optimized system can reach 92% double coverage in 9 min and that existing sites are concentrated in the city centre. Conference presentation (not a journal article). — [TRB 2020 slides](https://nitc.trec.pdx.edu/sites/default/files/TRB%202020%20-%20PSU%20-%20Ambulance%20Location%20Optimization%20Incorporating%20O-D%20Travel%20Time%20Variability-%20A%20Case%20Study%20of%20Delhi.pdf)
- Karnataka: a CAG performance audit (2014-15 to 2018-19) found the 108 target (20 min urban / 30 min rural on average) was achieved in only 72% of cases. Government audit report. — [CAG report chapter](https://cag.gov.in/webroot/uploads/download_audit_report/2020/5.Chapter%20II-05fd1cdd9ce5711.66448512.pdf); press summary at [The News Minute](https://www.thenewsminute.com/article/108-ambulances-failed-reach-50-patients-within-time-karnataka-cag-139331)
- Tamil Nadu: press report of GVK EMRI figures — 108 response time 13.51 min in 2021-22 and 13.13 min to July 2023. News article (not peer-reviewed). — [DT Next](https://www.dtnext.in/news/tamilnadu/overall-response-time-of-108-ambulances-drops-in-last-one-year-727237)
- Prayagraj: a 2022 SPA Bhopal thesis proposes simulation-based ambulance relocation optimization. Thesis; [title/abstract only]. — [SPA Bhopal repository](https://dspace.spab.ac.in/handle/123456789/1881)

### Inferences
- In the Indian context the binding constraints documented are fleet size, base locations, abandonment and traffic — not the dispatch rule. An honest Q-Rescue pitch should frame dispatch optimization as a marginal lever and cite Marla et al.
- "Risk-aware" in the classical literature usually means chance constraints (MALP), distributionally robust sets, or CVaR; Q-Rescue should say which, or drop the adjective.

### Gaps
- I found no peer-reviewed dispatch/location optimization study specific to Chennai or Bengaluru 108 operations. A claim that GPS-based dispatch cut response times 12–15% in Chennai/Kolkata appeared only in a coaching-site summary and could not be traced to a primary source; do not use it.
- Multi-objective (Pareto) ambulance papers from 2020–2026 were not individually verified in this search; this sub-question is under-covered.
- Contents of Wu et al. (2024) not read.

---

## 8. Evaluation practice: metrics, baselines, what counts as a fair comparison

### Takeaway
The field evaluates policies by discrete-event simulation over long call streams calibrated on real data, reporting the fraction of calls reached within a threshold and mean response time (increasingly survival- or priority-weighted), against closest-idle dispatch with return-to-home-base as the minimum baseline; strong papers also benchmark against preparedness/MEXCLP heuristics and report both metrics because they trade off.

### Cited Findings
- Fraction of late arrivals (threshold T) is the primary KPI in the Dutch line of work: 15-minute legal target with 12 minutes of driving in Utrecht; results reported as observed fractions of late arrivals from simulation. — [Jagtenberg et al. 2015 preprint](https://ir.cwi.nl/pub/23338/23338B.pdf)
- Both metrics must be reported: the same policy improved late arrivals by 18% and worsened mean response time by 37%. — [Jagtenberg et al. 2017, RePEc abstract](https://ideas.repec.org/a/kap/hcarem/v20y2017i4d10.1007_s10729-016-9368-0.html)
- EMSs commonly measure specific quantiles of the empirical response-time distribution; survival to hospital admission/discharge often decreases with response time, but response time is not equally important for all emergency types, motivating a penalized response time θ_c·w + 3600·M_ac. — [Guigues et al., arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Survival-probability objectives: Erkut, Ingolfsson & Erdoğan (2008), "Ambulance location for maximum survival", Naval Research Logistics 55(1):42–58 — add a survival function decreasing in response time to covering models, arguing covering models "do not adequately differentiate between consequences of different response times"; tested on Edmonton. [ABS] — [doi:10.1002/nav.20267](https://doi.org/10.1002/nav.20267); [Bilkent repository record](https://repository.bilkent.edu.tr/items/4a6a9c32-4d4e-4830-8e67-63b172a0550d)
- McLay & Mayorga (2010), "Evaluating emergency medical service performance measures", Health Care Management Science 13(2):124–136. [bibliographic only] — [RePEc](https://ideas.repec.org/a/kap/hcarem/v13y2010i2p124-136.html)
- Baselines actually used: closest-available + home base (Portuguese practice, Carvalho thesis); static MEXCLP solution (Jagtenberg 2015); closest/home/random station rules with 4.60/4.61/5.12 min baselines (Schmid, per seminar slides); nine literature policy families (Guigues 2026); "online benchmarks reflecting industry practice" (Rautenstrauß & Schiffer 2025); actual historical operations (Qatar). — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421); [RePEc, Schmid](https://ideas.repec.org/a/eee/ejores/v219y2012i3p611-621.html); [arXiv:2503.11848](https://arxiv.org/abs/2503.11848); [TRID](https://trid.trb.org/View/2685733)
- Statistical care: Guigues et al. report whether differences are statistically significant and separate "basic" from roll-out versions of competitor policies, attributing part of their gain to look-ahead shared with roll-out. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Evidence gap acknowledged by the field: no relocation study reported patient outcomes or real-life chain effects. — [Becker et al. 2023](https://doi.org/10.1136/bmjopen-2023-073394)
- Computational reporting: Guigues et al. (2026) report online decision times of 0.19–4.11 ms and offline pre-computation up to 346,000 s; Guigues et al. (2024/2026) state each decision is computed "in a few seconds". — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421); [arXiv:2409.09158](https://arxiv.org/abs/2409.09158)

### Inferences
A fair comparison for Q-Rescue, by the standards of this literature, needs all of the following:
- The same objective solved by an exact classical solver (MILP/brute force) on the same instances, so that QAOA solution quality is reported as an optimality gap — this isolates "solver" from "model".
- The model itself compared, in a rolling discrete-event simulation with Poisson (or historical) arrivals, service/transport times and a queue, against closest-idle and against at least one classical coverage-aware rule (Jagtenberg-style MEXCLP dispatch or Lee's preparedness ratio).
- Both fraction-within-threshold and mean (and tail) response time, by priority class, with confidence intervals over many replications.
- Wall-clock decision time including QUBO construction and circuit execution, against the millisecond-scale classical heuristics above.
A single hand-built snapshot in which the coverage-aware assignment "looks better" is an illustration, not an evaluation.

### Gaps
- McLay & Mayorga (2010) content not read. Specific survival functions (e.g., the cardiac-arrest logistic forms used by Erkut et al.) were not retrieved, so no formula is recorded here.

---

## 9. Critical point: can a single static assignment snapshot support a claim about "dynamic" future coverage? Is the future-coverage term linear, quadratic or higher-order?

### Takeaway
A one-shot batch assignment can legitimately contain a *proxy* for future impact (the literature does exactly this with preparedness, MEXCLP marginal coverage, and value-function approximations), but it cannot by itself support the word "dynamic" or any claim of improved outcomes — that requires rolling simulation. Mathematically, the MEXCLP coverage-loss term is exactly linear for a single dispatch, acquires genuine pairwise (quadratic) terms as soon as two dispatched ambulances cover a common zone, and is of higher order in general; the classical literature avoids the nonlinearity by auxiliary variables (Daskin's y_ik) or by linearizing with marginals.

### Cited Findings
- How the literature embeds the future in a one-shot decision:
  - Scalar preparedness after removing the candidate ambulance, traded against travel time (max of min_ℓ ψ_ℓ^{−a} / t^a_e; or (1+t^a_e)·(…)^w). — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
  - MEXCLP objective of the remaining idle fleet, recomputed for each candidate. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
  - Value-function approximation / ADP (Maxwell et al. 2010; Schmid 2012) and post-decision-state TD learning (Hua & Zaman 2020). — [doi:10.1287/ijoc.1090.0345](https://doi.org/10.1287/ijoc.1090.0345); [doi:10.1016/j.ejor.2011.10.043](https://doi.org/10.1016/j.ejor.2011.10.043); [arXiv:2010.07513](https://arxiv.org/abs/2010.07513)
  - Two-stage stochastic look-ahead in which the current decision is first-stage and sampled future calls form the second stage. — [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- The literature states the distinction explicitly: Jagtenberg et al. call MEXCLP "static" planning and describe marginal coverage as "an idea that originated in static ambulance planning" reused inside a dynamic policy; the policy is then evaluated by simulating the region over time. — [Jagtenberg et al. 2015 preprint](https://ir.cwi.nl/pub/23338/23338B.pdf)
- A coverage proxy can mislead: a naive greedy-coverage relocation rule was sometimes worse than the static solution, and Andersson–Värbrand's preparedness dispatch was shown by Lee (2011) to underperform closest-available. — [Jagtenberg et al. 2015 preprint](https://ir.cwi.nl/pub/23338/23338B.pdf); [arXiv:2203.16371](https://arxiv.org/abs/2203.16371)
- Nonlinearity is recognized and handled classically: Guigues et al. (2026) present a nonlinear "Version 1" of the preparedness-augmented selection problem and a linearized "Version 2" built from marginal changes of the metric per station. — [arXiv:2605.05421](https://arxiv.org/abs/2605.05421)
- MEXCLP is kept linear by auxiliary binaries y_ik with decreasing coefficients d_i(1−q)q^{k−1}. — [Jagtenberg et al. 2015 preprint](https://ir.cwi.nl/pub/23338/23338B.pdf)

### Inferences (my own derivation — not taken from a paper; the report writer should present it as analysis, and it should be re-checked independently)
Let x_{a,e} ∈ {0,1} assign idle ambulance a to call e, with Σ_e x_{a,e} ≤ 1. Define z_a = Σ_e x_{a,e} (1 if a leaves) — linear in x. Let N_i be the idle ambulances within threshold of zone i and k_i = |N_i|. Remaining MEXCLP coverage is Σ_i d_i (1 − q^{k_i − m_i}) with m_i = Σ_{a∈N_i} z_a. Writing ρ = (1−q)/q:

- Coverage loss L(z) = Σ_i d_i q^{k_i} [ Π_{a∈N_i} (1 + ρ z_a) − 1 ].
- First-order (linear) coefficient of z_a: Σ_{i: a∈N_i} d_i (1−q) q^{k_i−1} — exactly Daskin's marginal coverage of the k_i-th ambulance.
- Second-order coefficient of z_a z_b (a ≠ b): Σ_{i: a,b∈N_i} d_i (1−q)^2 q^{k_i−2} > 0 — losing two ambulances that cover the same zone costs more than the sum of the two single losses (diminishing returns of coverage). Check: for m_i = 2, q^{k−2} − q^k = 2(1−q)q^{k−1} + (1−q)^2 q^{k−2}.
- Order-m coefficient: d_i (1−q)^m q^{k_i−m} for every m-subset of N_i.

Consequences:
1. **One call, one dispatch** (the Jagtenberg/Lee setting): exactly one z_a = 1, so the "future coverage" term is a per-ambulance constant — purely **linear**. The whole problem is an argmin over ambulances; no optimization hardness and no QUBO needed.
2. **Batch with linear costs only** (travel time + first-order coverage loss): a **linear assignment problem**, polynomially solvable. A QUBO/QAOA formulation of this adds nothing computationally.
3. **Batch with exact MEXCLP loss**: polynomial of degree min(batch size, max_i k_i) in z, hence in x. Because z_a z_b = Σ_e Σ_e' x_{a,e} x_{b,e'}, the second-order truncation is **naturally quadratic** in the assignment variables (a quadratic semi-assignment structure). It is *exact* only if no zone is covered by three or more of the dispatched ambulances; otherwise cubic and higher terms exist and must be either dropped (stated as an approximation, with error bounded by the omitted coefficients), reduced with ancilla qubits, or replaced by Daskin-style y_ik variables whose linking inequalities need slack bits in a QUBO.
4. Note that ρ = (1−q)/q > 1 whenever q < 0.5, so higher-order coefficients are not small relative to lower-order ones for realistic busy fractions; the truncation is justified by geometry (few co-covering ambulances dispatched in one batch), not by coefficient decay.
5. **Preparedness (Andersson–Värbrand)**: with rank-dependent weights γ^1 > γ^2 > … the contribution of an ambulance depends on which closer ambulances remain (sorting), and the dispatch rule uses a min over zones — neither is polynomial of low degree; with a constant γ and a sum (not min) over zones it collapses to a linear term Σ_a (1 − z_a)/t_{aℓ}. Lee (2017)'s "nearest remaining ambulance" term is min-of-remaining, which expands as Σ_k t_(k)(1 − z_(k)) Π_{j<k} z_(j) — higher-order.

What Q-Rescue can and cannot honestly say:
- Can say: "a one-shot batch assignment with a look-ahead penalty equal to the MEXCLP expected-coverage loss (Daskin 1983; Jagtenberg et al. 2017), whose pairwise interaction terms make the objective quadratic." The quadratic interaction in a multi-call batch is the one place where a non-trivially-hard structure appears, and it is the most defensible technical hook.
- Cannot say: "dynamic", "optimizes future coverage", or "improves response" on the basis of a snapshot. The future term is a static, myopic-plus-one-step proxy under MEXCLP's independence and uniform-busy-fraction assumptions; it ignores when ambulances return, relocation, and call arrival timing. Demonstrating benefit requires embedding the snapshot solver in a rolling simulation and comparing with closest-idle and a classical coverage-aware rule on both threshold and mean response metrics.
- Scale honesty: instances with n ambulances × m calls need n·m (plus slack) binary variables; at sizes reachable by QAOA demonstrations, exhaustive search or a MILP solver returns the optimum essentially instantly, so the claim can only be about formulation and feasibility of the encoding, not speed or quality advantage. (This last sentence is an inference; quantum-side evidence is another researcher's scope.)

### Gaps
- I did not find a classical paper that writes the multi-dispatch MEXCLP loss as an explicit quadratic (pairwise) expansion in assignment variables; the derivation above is mine. Not finding it in a limited search does not establish that it is unpublished — submodular/quadratic treatments of expected coverage are common in facility location, and the team should search specifically ("quadratic semi-assignment", "submodular coverage dispatch") before claiming the expansion as a contribution.
- The magnitude of the error from truncating at second order on realistic geometries is unknown without numerical experiments.

---

## 10. Scope and limits of this search

### Takeaway
This is a targeted verification pass, not a systematic review: roughly 30 web searches/fetches plus Crossref DOI checks on 9 October 2026, with most pre-2018 journal articles accessible only at abstract level.

### Cited Findings
- DOIs marked [CR] were resolved through the Crossref REST API and matched on authors, title, journal, volume and pages. — [Crossref API](https://api.crossref.org/)
- Full texts actually read (at least the relevant sections): Jagtenberg et al. 2015 preprint; Guigues et al. arXiv:2203.16371 v3; Guigues et al. arXiv:2605.05421 (HTML, first ~80%); introduction of arXiv:2409.09158; Liu et al. 2020; Hua & Zaman 2020; Rautenstrauß & Schiffer arXiv:2306.04994; part of Tassone & Choudhury 2020; Zhou 2016 (via summary of the ar5iv page). — [arXiv](https://arxiv.org/)

### Inferences
- Statements tagged [SEC] depend on the accuracy of the restating authors (chiefly Guigues, Kleywegt & Nascimento and Jagtenberg et al.) and, in two cases, on an automated summary of an HTML page; formulas for Andersson–Värbrand, Lee 2011/2012/2014/2017 should be confirmed against the originals before appearing in a final report as exact.
- Statements tagged [MEM] (LSCM, MALP, hypercube descriptions) are from background knowledge and are the least verified items in these notes.

### Gaps
- Not accessed in full: every paywalled original listed as [ABS] or "content not read", including all six foundational location papers, Andersson & Värbrand 2007, all Lee papers, Jagtenberg et al. 2017 (journal version), Maxwell 2010, Schmid 2012, McLay & Mayorga 2013, Bandara 2014, the three anchor surveys, and Becker et al. 2023 (HTTP 403).
- Databases not searched directly: Scopus, Web of Science, Google Scholar citation chaining, IEEE Xplore, PubMed. Non-English literature was not searched.
- Under-covered topics: multi-objective (Pareto) ambulance models 2020–2026; Indian city-specific studies; 2025–2026 deep-RL papers beyond those listed; fire/police dispatch analogues; ride-hailing dispatch literature (which has extensive batch-matching work that may contain closely related formulations).
- No claim is made that the literature has been exhaustively searched; in particular, "I did not find X" statements above describe this search only.
