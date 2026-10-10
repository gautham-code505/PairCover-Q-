# India EMS policy context, Tamil Nadu 108 research dataset, and Q-HACK INDIA 2026 rules (for Q-Rescue)

Research date: 9 October 2026. Verification labels used throughout:

- **[FULL-RAW]** = I retrieved the source itself and read its raw text (HTML or PDF text extracted locally). Quotes are verbatim.
- **[FULL-SUMMARY]** = the full page was fetched, but I read it through an automated page-reading tool that returns a summary. Facts are from the full page; wording in quotation marks may not be character-exact and should be re-checked before being quoted in a submission.
- **[SNIPPET]** = seen only in a search-result snippet; the source was not opened.
- **[UNVERIFIED]** = could not be confirmed from any source I reached.

Most important caveat up front: **the official NAS 2026 guidelines PDF could not be opened** (nhm.gov.in refused/timed out on every attempt, no Wayback copy exists). Everything below about its contents comes from press coverage, not from the document. No page or section numbers can be given.

---

## 1. National Ambulance Services (NAS) Operational Guidelines: current version, title, date, official PDF, related documents

### Takeaway
The current document is the "Operational Guidelines on National Ambulance Services (NAS), 2026", launched 29 June 2026 by the Union Health Minister; the official PDF is hosted on nhm.gov.in but I could not open it, so its title page, page count and internal date are unverified from the primary source. Press coverage calls it the "first" comprehensive national framework, yet NAS itself has existed under NHM since 2012 with ALS/BLS population norms, so "first" refers to a consolidated operational guideline, not to the scheme.

### Cited Findings
- Official PDF location (URL returned by search, titled "NAS guidline June 2026"): https://nhm.gov.in/New-Update-2025-26/NAS-Guidline/NAS-guidline-June-2026.pdf. **Not opened**: direct fetch returned `ECONNREFUSED`, curl over HTTPS and HTTP timed out, the Wayback Machine availability API returned no snapshot, and a proxy reader returned only metadata. [SNIPPET for existence; contents UNVERIFIED] — [NHM PDF](https://nhm.gov.in/New-Update-2025-26/NAS-Guidline/NAS-guidline-June-2026.pdf)
- A proxy reader reported a "Published time" header of 7 Aug 2026 for that PDF URL. This is probably a file/crawl timestamp, not the document date. Weak evidence only. [UNVERIFIED as a document date] — [NHM PDF](https://nhm.gov.in/New-Update-2025-26/NAS-Guidline/NAS-guidline-June-2026.pdf)
- Title as reported: "Operational Guidelines on National Ambulance Services (NAS), 2026"; released 29 June 2026 by Union Health Minister J. P. Nadda at the 16th Conference of the Central Council of Health & Family Welfare, New Delhi. [FULL-SUMMARY] — [ETV Bharat, 29 Jun 2026](https://www.etvbharat.com/en/bharat/national-ambulance-services-guidelines-2026-set-uniform-standards-for-emergency-care-across-india-enn26062906951)
- Same title and launch by Nadda; described as laying down "for the first time, a comprehensive national framework". Article dated 1 July 2026. [FULL-SUMMARY] — [Outlook India](https://www.outlookindia.com/healthcare-spotlight/centre-rolls-out-first-national-framework-to-standardise-ambulance-services)
- Issuer given as MoHFW; PIB release cited as PRID 2279073. The PIB page returned HTTP 403 to me, so the official press release text is **not verified**. [FULL-SUMMARY for the secondary article; PIB UNVERIFIED] — [The Policy Edge](https://www.policyedge.in/p/health-ministry-releases-national-ambulance-services-guidelines-2026); [PIB link (403)](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2279073&reg=3&lang=1)
- NAS as a scheme predates 2026: MoHFW parliamentary answers state NAS was introduced in 2012 under NHM and operates in 36 States/UTs; NHM-MIS (June 2024) fleet: 15,283 BLS, 3,918 PTV, 3,044 ALS. [SNIPPET] — [Rajya Sabha answer, 11 Mar 2025](https://rsdebate.nic.in/bitstream/123456789/759010/1/PQ_267_11032025_U1385_p391_p392.pdf); [MoHFW press release](https://mohfw.gov.in/press-info/8546)
- Dial 108 vs Dial 102: 108 is "predominantly an emergency response system" for critical care, trauma and accident victims; 102 is basic patient transport mainly for pregnant women and children. [SNIPPET] — [Rajya Sabha answer, 5 Dec 2023](https://rsdebate.nic.in/bitstream/123456789/745837/1/PQ_262_05122023_U258_p352_p353.pdf)

### Inferences
- Disagreement to document: press says "first comprehensive national framework" (2026); parliamentary answers show NAS norms (ALS per 5 lakh, BLS per 1 lakh) existed long before. These are compatible if the 2026 document is the first consolidated *operational guideline*; I could not confirm whether the 2026 PDF says it supersedes anything.
- The filename says "June 2026", matching the 29 June 2026 launch. Treat "June 2026" as the publication month, pending a check of the PDF itself.

### Gaps
- Exact title-page wording, page count, publishing division (NHM / NHSRC), table of contents, and any "supersedes" clause: not verifiable because the PDF was unreachable from this environment. Someone on an Indian network should open the PDF directly.
- I did not locate or open older standalone documents (earlier NHM ambulance/ERS guidance, AIS-125 text, NHSRC EMS documents). Their existence is implied by parliamentary answers but no URL was verified.

---

## 2. What the guidelines say on dispatch, GPS, GIS, traffic, demand, positioning, hospitals, referral, response times, norms, ALS/BLS

### Takeaway
Per press coverage only, the 2026 guidelines recommend Integrated Command and Dispatch Centres with GPS tracking, "intelligent dispatch", GIS mapping (including bed availability) and data-driven deployment using call trends, traffic and hotspots. No numeric response-time target or population norm from the 2026 document could be verified; the only verified-in-official-source norms are the older NHM ones seen in parliamentary snippets.

### Cited Findings

Stated (in secondary coverage of the 2026 guidelines; none verified against the PDF, no page numbers available):
- Integrated Command and Dispatch Centres (ICDCs) with digital call management, structured triage protocols, "intelligent dispatch mechanisms" and real-time monitoring dashboards. [FULL-SUMMARY] — [Outlook India](https://www.outlookindia.com/healthcare-spotlight/centre-rolls-out-first-national-framework-to-standardise-ambulance-services); [ETV Bharat](https://www.etvbharat.com/en/bharat/national-ambulance-services-guidelines-2026-set-uniform-standards-for-emergency-care-across-india-enn26062906951)
- Purpose of intelligent dispatch described as dispatching "the nearest available ambulance more quickly". [FULL-SUMMARY] — [ETV Bharat](https://www.etvbharat.com/en/bharat/national-ambulance-services-guidelines-2026-set-uniform-standards-for-emergency-care-across-india-enn26062906951)
- GPS-enabled ambulance/fleet tracking. [FULL-SUMMARY] — [ETV Bharat](https://www.etvbharat.com/en/bharat/national-ambulance-services-guidelines-2026-set-uniform-standards-for-emergency-care-across-india-enn26062906951)
- GIS-based mapping of hospitals, referral centres, ambulance stations, accident-prone areas, bed availability and critical-care facilities, to help identify the nearest appropriate facility and route ambulances. [FULL-SUMMARY] — [Outlook India](https://www.outlookindia.com/healthcare-spotlight/centre-rolls-out-first-national-framework-to-standardise-ambulance-services)
- Deployment to be evidence/data-driven using call patterns, referral trends, traffic density, accident hotspots, geography and population, to "position ambulances where they are most needed"; deployment "rather than administrative norms alone". [FULL-SUMMARY] — [ETV Bharat](https://www.etvbharat.com/en/bharat/national-ambulance-services-guidelines-2026-set-uniform-standards-for-emergency-care-across-india-enn26062906951); [The Policy Edge](https://www.policyedge.in/p/health-ministry-releases-national-ambulance-services-guidelines-2026)
- All ambulances must comply with AIS-125. [FULL-SUMMARY] — [Outlook India](https://www.outlookindia.com/healthcare-spotlight/centre-rolls-out-first-national-framework-to-standardise-ambulance-services)
- Phased integration of ambulance services with the national emergency number 112. [FULL-SUMMARY] — [Outlook India](https://www.outlookindia.com/healthcare-spotlight/centre-rolls-out-first-national-framework-to-standardise-ambulance-services)
- Coverage also lists ambulance categorisation, equipment and drugs, HR norms, training, infection prevention, maintenance, quality assurance, grievance redressal. [FULL-SUMMARY] — [Outlook India](https://www.outlookindia.com/healthcare-spotlight/centre-rolls-out-first-national-framework-to-standardise-ambulance-services)

Older NHM norms (official parliamentary answers, not the 2026 PDF):
- One ALS ambulance per 5 lakh population and one BLS per 1 lakh population. [SNIPPET] — [MoHFW press release](https://mohfw.gov.in/press-info/8546); [Rajya Sabha answer, 11 Mar 2025](https://rsdebate.nic.in/bitstream/123456789/759010/1/PQ_267_11032025_U1385_p391_p392.pdf)
- Additional ambulances may be supported where utilisation exceeds 4 trips/day (or 120 km) in dense areas, or 3 trips/day (or 80 km) in hilly areas. [SNIPPET] — [Lok Sabha answer](https://eparlib.nic.in/bitstream/123456789/956165/1/AU5611.pdf) (snippet did not make clear which of several parliamentary PDFs carried this sentence; verify before citing)
- BLS = transport for patients not needing ventilatory support or cardiac monitoring; ALS = equipped for ventilatory support and cardiac monitoring. [SNIPPET] — [Rajya Sabha answer, 5 Dec 2023](https://rsdebate.nic.in/bitstream/123456789/745837/1/PQ_262_05122023_U258_p352_p353.pdf)

Response-time targets:
- ETV Bharat, Outlook and Policy Edge all mention "response time benchmarks" but **give no number**. [FULL-SUMMARY] — [ETV Bharat](https://www.etvbharat.com/en/bharat/national-ambulance-services-guidelines-2026-set-uniform-standards-for-emergency-care-across-india-enn26062906951)
- A training-institute blog claims a 20-minute target, possibly 10 minutes in congested urban areas. Low-reliability, not confirmed by any official source. [SNIPPET, UNVERIFIED] — [OC Academy blog](https://www.ocacademy.in/blogs/national-ambulance-guidelines-india-standards/)
- For comparison (a state contract, not national policy): a CAG audit of Karnataka's 108 cites targets of 20 minutes average urban and 30 minutes average rural. [SNIPPET] — [CAG report](https://cag.gov.in/uploads/icisa_it_reports/f081103b45fccc4748d202e6c6ea7fbe-06245a65d635d22-75261345.pdf)

### Inferences
- Clearly **stated** (per press): intelligent dispatch, GPS tracking, GIS mapping incl. bed availability, data-driven positioning using call trends/traffic/hotspots.
- Only **implied**: "dynamic redeployment" or "relocation" in the operations-research sense. No article uses "dynamic deployment", "redeployment" or "coverage"; the wording is about planning where to station ambulances. Q-Rescue should say its coverage-aware assignment is *consistent with the direction of* the guidelines, not that the guidelines require it.
- **Absent from everything I read**: "computer-aided dispatch" as a term, AVL, any optimisation method, any explicit rule on trading response time against future coverage, numeric response-time targets, and explicit inter-facility-transfer decision rules (only "referral centres" and "referral patterns" are mentioned).

### Gaps
- No verbatim quote with page/section number can be supplied for any topic, because the PDF was unreachable. All quotation-marked phrases above are from news articles read through a summarising tool.
- 2026 numeric response-time targets (urban/rural/hilly), 2026 ambulance-to-population ratios, and the 2026 list of ambulance categories: not found in any source opened.

---

## 3. TNHSP anonymised "108 Ambulance" research dataset: existence, documentation, access

### Takeaway
Yes, it exists and is officially documented: tnhsp.org has a "108 Ambulance — Data Download Request Form" page that describes a curated, anonymised research version and lists its fields; access is through a Google Form. The page does **not** state time coverage, row count, file format, licence text or review process.

### Cited Findings
All from the raw HTML of the official page, downloaded 9 Oct 2026 (HTTP 200). [FULL-RAW] — [TNHSP 108 dataset page](https://www.tnhsp.org/pages/view/108_Application)
- Page heading: "108 Ambulance", sub-heading "Data Download Request Form". It sits under a site menu "Datasets" with two entries, "108" and "TAEI" (the TAEI page is at https://www.tnhsp.org/pages/view/TAEI_Application; not opened).
- Verbatim: "The 108 Ambulance Services dataset for Tamil Nadu is maintained for internal monitoring and administrative purposes and is not intended for direct public access."
- Verbatim: "To facilitate research, analytical assessments, and policy formulation, a curated and anonymized version of the dataset has been prepared. This version preserves essential analytical attributes while ensuring that no individual case can be identified, enabling responsible public and non-commercial use."
- Documented fields with one-line descriptions (verbatim): Case_ID "Unique identification number for each ambulance case"; Emergency / IFT "Emergency or inter-facility transfer indicator"; Caller District "District where the call originated"; Caller Taluk "Taluk of call origin"; is_critical "Patient critical condition status"; triage "Priority classification"; Victim_age; Victim_gender; Vehicle_District "Ambulance mapped district"; Ambulance_Number "Registration number of ambulance"; Vehicle Type "ALS / BLS category"; Emergency Type "Primary classification"; EM sub Type; Assigned by ERO "Assigned by Emergency Response Officer"; Changed Hospital Name "Updated hospital (if changed)"; Source Hospital "Referral hospital (IFT)"; Admission Hospital "Final admitted hospital"; Hospital_Type "Government / Private / Medical College"; Standard Remarks.
- "Date & Time Fields" (names only, no descriptions): Call Date (dd/mm/yyyy); Case Assigned Time; Base Start Time; Scene Arrival Time; Scene Departure Time; Hospital Reach Time; Hospital Start Time; Base Reach Time; Case Closing Date & Time.
- "Odometer (ODO) Readings": Base Start (ODO); Scene (ODO); Hospital (ODO); Base Reach (ODO).
- "Staff & System Details": EMT ID; Pilot ID; Close_BY (App/Web); Reason for IFT Referral; Sub-category of IFT Referral.
- "Distance (KM)": BS(KM) Base to Scene; SH(KM) Scene to Hospital; HB(KM) Hospital to Base; B2B(KM) Total distance.
- "Time Duration (HMS)": CW Call Waiting; WB Waiting at Base; BS Base to Scene; Scene Time at Scene; SH Scene to Hospital; Hospital Time at Hospital; HB Hospital to Base; BB Base to Base.
- "Police & Fire Involvement": Police Calls; Police Remarks; Fire Calls; Fire Remarks.
- "Operational & Classification" (names only, **no descriptions**): Day/Night Shift; EME ID; Is First Aid; Level; EMT Summary; AVD/UAD; Area; Date; Hour; Start Time; Response Time; Benchmark; RTNM; Emergency Type - New.
- Access: a sidebar "Dataset" with two links labelled "Traning 1 Dataset" and "Traning 2 Dataset" (spelling as on page). Both point to the same Google Form ID: https://docs.google.com/forms/d/e/1FAIpQLSdm0PjdwobBkfwckS4UcTBpG3mHt5I9ZnQK1ArV_PITcbYKqg/viewform (the first link uses the `/alreadyresponded` suffix). I did **not** open or submit the form.
- Contact on page: pdtnhsp@gmail.com; Tel 044-24340057, 044-24335993; Project Director, TNHSP, 3rd Floor, DMS Annex New Building, 359 Anna Salai, Teynampet, Chennai 600006.

### Inferences
- Geographic resolution is **district and taluk for the caller, district for the vehicle**. No latitude/longitude, block, village, pincode or base-station field is listed.
- The label "Training 1 / Training 2 Dataset" suggests two extract files (possibly sample or model-training splits). What each contains is not documented.
- "Anonymised" coexists with listed fields such as Ambulance_Number, EMT ID, Pilot ID and hospital names; whether these are masked in the released file is not stated.

### Gaps
- Time coverage (years/months), number of records, file format (CSV/XLSX), file size: **not stated on the page**.
- Access conditions beyond "responsible public and non-commercial use": no licence, citation requirement, ethics/IRB requirement, approval turnaround or data-use agreement is shown on the page. These may be inside the Google Form, which I did not open.
- Meaning of undocumented fields (Level, AVD/UAD, Area, Benchmark, RTNM, Start Time, Emergency Type - New) is unknown. Do not assume.
- I did not check tn.data.gov.in, data.gov.in or tnhealth.tn.gov.in for a mirror; none surfaced in searches.

---

## 4. Sufficiency of documented variables for Q-Rescue; what is absent

### Takeaway
On paper the dataset supports response/travel-time estimation and taluk-level demand counts by emergency type, and (unexpectedly) documents vehicle type and triage. It does not document any coordinates, GPS traces, traffic, bed capacity, live ambulance status or base locations, so geographic coverage and future-availability effects must be modelled at taluk/district level or simulated.

### Cited Findings

Source for every "TNHSP page" row: https://www.tnhsp.org/pages/view/108_Application [FULL-RAW]. "Documented" means the field name is listed on the page; it has **not** been confirmed in an actual downloaded file.

| Variable | Source evidence (URL + quote/section) | Actual availability | Proposed use in Q-Rescue | Limitations |
|---|---|---|---|---|
| Case identifier | TNHSP page: "Case_ID: Unique identification number for each ambulance case" | Verified present (documented) | Row key; de-duplication | Anonymised; cannot link to outside records |
| Emergency vs inter-facility transfer | TNHSP page: "Emergency / IFT: Emergency or inter-facility transfer indicator" | Verified present (documented) | Filter to emergencies; model IFT as competing load on fleet | Coding values not documented |
| Call date | TNHSP page, Date & Time Fields: "Call Date (dd/mm/yyyy)"; also "Date", "Hour" | Verified present (documented) | Daily/hourly demand counts | A distinct call-received *timestamp* is not named; only date, "Hour", and an undefined "Start Time" |
| Call-received time (exact) | TNHSP page lists "Hour" and "Start Time" without description | Undocumented-unknown | Start of response interval | Cannot assume "Start Time" is call pickup |
| Call waiting duration | TNHSP page, Time Duration (HMS): "CW – Call Waiting" | Verified present (documented) | Call-centre delay component | Start/end definition not given |
| Dispatch / assignment time | TNHSP page: "Case Assigned Time" | Verified present (documented) | Dispatch decision timestamp; replay point for assignment policy | Format and timezone not documented |
| Base start time | TNHSP page: "Base Start Time"; "WB – Waiting at Base" | Verified present (documented) | Chute time (assignment to wheels rolling) | Assumes ambulance started from base; not stated for diverted vehicles |
| At-scene arrival / departure | TNHSP page: "Scene Arrival Time", "Scene Departure Time", "Scene – Time at Scene" | Verified present (documented) | Response time; on-scene service time distribution | None documented beyond names |
| Hospital arrival / departure | TNHSP page: "Hospital Reach Time", "Hospital Start Time", "Hospital – Time at Hospital" | Verified present (documented) | Transport time; hospital turnaround time | None documented beyond names |
| Return to base / case close | TNHSP page: "Base Reach Time", "Case Closing Date & Time", "BB – Base to Base" | Verified present (documented) | Total busy time per case, i.e. how long an ambulance is unavailable (core of the "lost future coverage" term) | Vehicle may be reassigned before reaching base; not documented |
| Response time (pre-computed) | TNHSP page, Operational & Classification: "Response Time", "Benchmark", "RTNM" | Verified present (documented name); definition undocumented | Validation target for simulated response times | Start/stop definition unknown; "Benchmark" and "RTNM" undefined |
| Travel distances | TNHSP page, Distance (KM): "BS(KM) – Base to Scene", "SH(KM)", "HB(KM)", "B2B(KM) – Total distance"; plus four ODO readings | Verified present (documented) | Fit speed = distance/time by area and hour; build taluk-to-taluk travel-time estimates | Odometer-based, per trip; not a road-network matrix |
| Incident location, district | TNHSP page: "Caller District: District where the call originated" | Verified present (documented) | Demand zone (coarse) | Caller location, not necessarily incident location |
| Incident location, taluk | TNHSP page: "Caller Taluk: Taluk of call origin" | Verified present (documented) | Demand node in QUBO; coverage zones | Finest documented resolution |
| Incident latitude/longitude | TNHSP page: no such field listed | Verified absent from documentation | none | Must use taluk centroids or synthetic points |
| Urban/rural/tribal class | TNHSP page lists "Area" with no description | Undocumented-unknown | Possible stratifier | Meaning of "Area" is a guess; do not assume |
| Ambulance home area | TNHSP page: "Vehicle_District: Ambulance mapped district" | Verified present (documented), district only | Fleet per district; supply side of coverage | District is too coarse for station-level coverage |
| Ambulance base/station coordinates | TNHSP page: no such field listed | Verified absent from documentation | none | Bases must be assumed (e.g. taluk HQ / hospitals) or inferred loosely from BS(KM) |
| Ambulance identity | TNHSP page: "Ambulance_Number: Registration number of ambulance" | Verified present (documented) | Reconstruct each vehicle's busy/idle timeline from historical cases | May be masked in the anonymised file; unknown |
| Vehicle type | TNHSP page: "Vehicle Type: ALS / BLS category" | Verified present (documented) | Capability constraint (ALS for critical cases) | Only ALS/BLS named; neonatal, 4WD, bikes not mentioned |
| Triage priority / criticality | TNHSP page: "triage: Priority classification"; "is_critical: Patient critical condition status"; "Level" | Verified present (documented) | Priority weights in objective | Category scheme undocumented |
| Emergency type | TNHSP page: "Emergency Type: Primary classification", "EM sub Type", "Emergency Type - New" | Verified present (documented) | Demand forecasting by type; service-time by type | Category list not documented |
| Destination hospital | TNHSP page: "Admission Hospital: Final admitted hospital"; "Changed Hospital Name"; "Source Hospital"; "Hospital_Type: Government / Private / Medical College" | Verified present (documented) | Empirical destination-choice probabilities per taluk | Names only; no coordinates, no capability data |
| Hospital bed capacity / availability | TNHSP page: no such field listed | Verified absent from documentation | none | Must be simulated or omitted |
| Live ambulance status / availability at dispatch | TNHSP page: no status field; "AVD/UAD" listed but undefined | Undocumented-unknown (not directly present) | Can be *reconstructed* approximately from each vehicle's case timestamps | Reconstruction misses breakdowns, shift gaps, non-case movements |
| Live GPS traces / AVL | TNHSP page: no such field listed | Verified absent from documentation | none | Positions between events must be simulated |
| Real-time traffic | TNHSP page: no such field listed | Verified absent from documentation | none | Use empirical speed by hour/day from BS and SH legs as a proxy |
| Shift | TNHSP page: "Day/Night Shift" | Verified present (documented) | Time-of-day stratifier | none documented |
| Patient age/gender | TNHSP page: "Victim_age", "Victim_gender" | Verified present (documented) | Not needed for dispatch optimisation | Leave unused to minimise privacy exposure |
| Time coverage, record count, format | TNHSP page: not stated | Undocumented-unknown | Determines train/test split | Must be learned from the file after access |

### Inferences
- Response-time estimation: feasible from documented timestamps and durations (Case Assigned → Scene Arrival; BS duration and BS km).
- Demand forecasting: feasible at taluk x hour x emergency-type granularity, if time coverage is long enough (unknown).
- Geographic coverage: only at taluk/district granularity. True station-level coverage cannot be computed because base coordinates and incident coordinates are not documented.
- Three variables the project brief expected to be absent are in fact documented: vehicle type, triage priority, and (district-level only) ambulance home area.

Evaluable from historical records versus must be simulated:

- **From historical records (if the file matches the documentation):** response-time and travel-time distributions by taluk/hour; service, hospital-turnaround and total busy-time distributions; arrival rates by taluk, hour and emergency type; ALS/BLS mix per case; share of IFT load; empirical destination-hospital patterns; an approximate per-vehicle busy/idle timeline.
- **Must be simulated or assumed:** ambulance positions between events; base-station locations; taluk-to-taluk travel-time matrix for counterfactual assignments (historical data only shows the assignment actually made); what would have happened under a different assignment (all counterfactual outcomes); real-time traffic; hospital bed availability and diversion; coverage loss after a dispatch; vehicle breakdowns and crew shifts.

### Gaps
- No sample file was obtained, so none of the "verified present" entries is confirmed in real data; field completeness and masking are unknown.
- Whether a counterfactual evaluation is statistically defensible with taluk-level geography was not assessed.

---

## 5. Published studies using TN 108 / GVK EMRI data; fallback public EMS datasets

### Takeaway
I found no published ambulance-location or dispatch-optimisation study built on Tamil Nadu 108 call records. Existing work is descriptive (obstetric transport, COVID-period maternal care, rural utilisation survey). Open US dispatch datasets are the realistic fallback if TNHSP access is slow.

### Cited Findings
- Madras Christian College report for the TNHSRP Operational Research Programme, "Challenges of Rural People in Effective Utilisation of 108 Emergency Ambulance Services in Tamil Nadu – An Empirical Study" (Chinna Muthu, Kalyani, Vijay Devanesan; February 2022). Survey/interview based; fleet and response figures are cited from the TNEMS-TNHSP web dashboard, not from case-level records. [FULL-RAW, PDF text extracted locally] — [MCC/TNHSRP report hosted at IIT Madras CTaP](https://hss.iitm.ac.in/ctap/wp-content/uploads/2023/01/108-Final-Report.pdf)
- "Transport of pregnant women and obstetric emergencies in India: an analysis of the '108' ambulance service system data": used 108 call-centre data from six states for 2013–14. [SNIPPET; PMC page blocked by a browser check] — [PMC5073462](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5073462/)
- "Interfacility transfer of pregnant women using publicly funded emergency call centre-based ambulance services": cross-sectional analysis of service logs from five Indian states. [SNIPPET] — [PMC5734264](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5734264/)
- A counterfactual analysis of maternal care in Tamil Nadu during the pandemic used 108 control-centre call-register data and states the fleet was increased to 1,300 after the first COVID wave. [SNIPPET; full text blocked] — [PMC10513313](https://pmc.ncbi.nlm.nih.gov/articles/PMC10513313/)
- GVK EMRI cardiac-call study across 11 states (not TN-specific). [SNIPPET] — [J Soc Health Diabetes 2016](https://thieme-connect.de/products/ejournals/abstract/10.4103/2321-0656.187999?lang=en)
- Indian comparator: Delhi ambulance location optimisation with origin–destination travel-time variability (TRB 2020). [SNIPPET] — [NITC/PSU paper](https://nitc.trec.pdx.edu/sites/default/files/TRB%202020%20-%20PSU%20-%20Ambulance%20Location%20Optimization%20Incorporating%20O-D%20Travel%20Time%20Variability-%20A%20Case%20Study%20of%20Delhi.pdf)
- Indian open-data lead: IUDX "ambulance stories" for Chandigarh. [SNIPPET; contents not checked] — [IUDX Chandigarh](https://ambulancestories.iudx.org.in/chandigarh/)

Fallback public datasets (all [SNIPPET]; dataset pages not opened, variable lists from search summaries):
- NYC "EMS Incident Dispatch Data" (FDNY EMS CAD; incident creation to closure, resource assignment; exact location withheld and aggregated to broader geography; CSV/JSON). Portal ID reported as 76xm-jjuj. — [data.gov catalog entry](https://catalog.data.gov/dataset/ems-incident-dispatch-data)
- San Francisco "Fire Department and Emergency Medical Services Dispatched Calls for Service" (one row per unit response: call number, unit ID, call type, disposition, time intervals; address as intersection/call box; updated daily). Portal ID reported as nuek-vuh3. — [data.gov catalog entry](https://catalog.data.gov/dataset/fire-department-and-emergency-medical-services-dispatched-calls-for-service)
- "Seattle Real Time Fire 911 Calls" (address, datetime, incident type, latitude, longitude, incident number; no unit timestamps). Portal ID reported as kzjm-xkqj. — [data.gov catalog entry](https://catalog.data.gov/dataset/seattle-real-time-fire-911-calls)

### Inferences
- San Francisco is the strongest fallback for Q-Rescue because it is unit-level with multiple timestamps and approximate locations; Seattle gives coordinates but no response intervals; NYC gives intervals but coarse geography.
- A taluk-level QUBO study on the TNHSP extract would appear to be novel relative to what I found, but my literature search was shallow (two queries), so do not claim "first".

### Gaps
- Variables actually available to the PMC studies could not be read (PMC blocked automated access).
- Montgomery County PA 911 data: no official URL verified; I know it mainly as a Kaggle upload, so it is omitted rather than cited.
- No Google Scholar / IEEE search was run for "108 ambulance" optimisation papers.

---

## 6. Published performance facts for Tamil Nadu 108

### Takeaway
Best-sourced figures: fleet of 1,237 ambulances (1,044 BLS, 124 ALS, 65 neonatal, 4 VVIP convoy) plus 41 first-responder bikes around late 2021; average response time about 13–14.5 minutes statewide in 2021–2023, about 7 minutes in metro. More recent figures (1,330 ambulances; 10 min 14 s) exist only in undated or secondary snippets.

### Cited Findings
- Fleet 1,237: 1,044 BLS (84.40%), 124 ALS (10.02%), 65 NLS (5.25%), 4 VVIP convoy; plus 41 First Responder Bikes. District table dated November 2021; source given as TNEMS-TNHSP dashboard. [FULL-RAW, report p. 46–47] — [MCC/TNHSRP report, Feb 2022](https://hss.iitm.ac.in/ctap/wp-content/uploads/2023/01/108-Final-Report.pdf)
- Response time "reduced from 0:18:09 during the financial year 2017-2018 to 0:14:24 during the financial year 2020-2021"; urban 0:12:51 vs rural 0:15:19; 78% of metro, 62% urban, 61% rural and 51% tribal cases under 10 minutes. [FULL-RAW, report p. 53–54] — [MCC/TNHSRP report](https://hss.iitm.ac.in/ctap/wp-content/uploads/2023/01/108-Final-Report.pdf)
- Average response time (minutes, as printed) 2021-22 → to 23 July 2023: overall 13.51 → 13.13; tribal 17.24 → 15.33; rural 14.53 → 13.41; urban 12.17 → 11.41; metro 7.38 → 7.13 (6.54 in 2022-23). Figures attributed to GVK EMRI officials; article updated 31 Jul 2023. [FULL-SUMMARY] — [DT Next](https://www.dtnext.in/news/tamilnadu/overall-response-time-of-108-ambulances-drops-in-last-one-year-727237)
- Operator says it tracks response time weekly and revises accident hotspots monthly. This is the only evidence found of hotspot-based positioning in TN practice. [FULL-SUMMARY] — [DT Next](https://www.dtnext.in/news/tamilnadu/overall-response-time-of-108-ambulances-drops-in-last-one-year-727237)
- 930 ambulances statewide, 50 in Greater Chennai, more than 15,000 calls a day (undated interview with TNHSP Project Director; clearly older than the 2021 fleet figure). [SNIPPET] — [Citizen Matters](https://citizenmatters.in/interview-uma-maheswari-tamil-nadu-health-systems-108-ambulance/)
- 1,330 ambulances (Health Minister statement, undated in snippet). [SNIPPET] — [The News Minute](https://www.thenewsminute.com/amp/story/tamil-nadu/ambulance-disrupts-eps-rally-aiadmk-chief-accuses-dmk-of-planned-disturbance)
- World Bank, 2014: urban within 15 minutes, rural within 21 minutes. [SNIPPET] — [World Bank feature](https://www.worldbank.org/en/news/feature/2014/03/10/saving-one-life-every-30-minutes)
- October 2015 monthly report: 596,278 calls received, 579,884 answered, 83,815 cases transported. Hosted on Scribd, not an official site. [SNIPPET] — [Scribd copy](https://www.scribd.com/document/858968061/Emri-Oct-2015)

### Inferences
- Conflict: 2020-21 statewide average is 14:24 in the MCC report but one search summary quoted 14:48 for 2021 from another commentary. Different year definitions likely; use the report figure with its page reference.
- DT Next figures are printed with a decimal point (e.g. 13.51). They may be minutes.seconds rather than decimal minutes; the article does not say.

### Gaps
- No 2025-26 Tamil Nadu Health Department policy note was located, so there is no official current fleet size, call volume or response time for 2025–2026.
- The "10 minutes 14 seconds" statewide figure could not be traced to an official source.

---

## 7. Q-HACK INDIA 2026: official page, Round 1 deadline, deliverables, criteria, rules

### Takeaway
Official site is quantumweek.tech (QuantumRIT, Ramaiah Institute of Technology, Bengaluru; IBM Qiskit Fall Fest programme). The Round 1 deadline of **10 October 2026, 11:59 PM IST** is confirmed on the submission page and on the Tally submission form, but an older "7 October" date still appears in search snippets and, reportedly, in the site FAQ. Round 1 requires four items, not just an abstract: slides, demo video, prototype, GitHub repo.

### Cited Findings
- Round 1 closes 10 October 2026, 11:59 PM. Required: (1) idea presentation, max 10 slides, PPT/PDF, official Canva template; (2) demo video, max 3 minutes, showing prototype and circuit execution, narrated by real team members, no AI avatars or text-to-speech; (3) prototype as web/mobile app, Jupyter notebook with runnable quantum circuits, or simulation/quantum algorithm/hybrid application; (4) GitHub repository with README, setup instructions, documented source. Teams must pick one track. All links must be publicly viewable. Support: quantumrit@msrit.edu. [FULL-SUMMARY] — [Submission page](https://quantumweek.tech/hackathon/submission)
- Submission form titled "Q-HACK INDIA 2026 Round 1 Project Submission": deadline 10 October 2026, 11:59 PM IST; only the Team Lead submits; PPT template https://canva.link/b51hvxu95kmz95f; team-size options 3 or 4. [FULL-SUMMARY] — [Tally form](https://tally.so/r/RGppj9)
- Timeline: Round 1 opens 27 Sep 2026; Round 1 deadline 10 Oct 2026 11:59 PM; top 30 announced 12 Oct 2026; Round 2 virtual build sprint with mentorship 12–29 Oct; Grand Finale 30 Oct (remote build) and 31 Oct (in person, MSRIT Bengaluru). [FULL-SUMMARY] — [Hackathon page](https://quantumweek.tech/hackathon)
- Judging weights: Technical Implementation 30%, Quantum Relevance 20%, Originality & Innovation 20%, Problem Significance 10%, Potential Impact 10%, Presentation & Clarity 10%. Identical on both pages. [FULL-SUMMARY] — [Hackathon page](https://quantumweek.tech/hackathon); [Submission page](https://quantumweek.tech/hackathon/submission)
- Tracks: Quantum Biotech & Chemistry; Quantum Security & Cryptography; Quantum AI & Software; Open Quantum Innovation. Teams define their own problem. [FULL-SUMMARY] — [Hackathon page](https://quantumweek.tech/hackathon)
- Teams of 3–4 students, no solo entries, inter-institute and cross-branch teams allowed, finalists must attend in person. Prize pool Rs 1,00,000 (50,000 / 30,000 / 10,000 / 10,000). [FULL-SUMMARY] — [Hackathon page](https://quantumweek.tech/hackathon); [FAQ](https://quantumweek.tech/faq)
- Tools: any quantum frameworks, open-source libraries, classical simulators and hybrid tools are allowed. No rule requiring real quantum hardware was found. [FULL-SUMMARY] — [Hackathon page](https://quantumweek.tech/hackathon)
- AI rule: submissions that are mostly unverified AI-generated content without working code or substantive human effort "will be directly rejected". [FULL-SUMMARY] — [Submission page](https://quantumweek.tech/hackathon/submission)
- Organiser and context: QuantumRIT, student-led community at Ramaiah Institute of Technology; part of Quantum Week 2026 (27–31 Oct) and IBM Qiskit Fall Fest; mentors available 10–29 Oct; finale jury 31 Oct. [FULL-SUMMARY] — [Mentor call form](https://tally.so/r/q42Zx2); [Quantum Week home](https://quantumweek.tech)
- Devfolio registration and team formation described as mandatory, with Devfolio team details used to verify eligibility. [SNIPPET of the Tally form; not reproduced in my full fetch of the form] — [Tally form](https://tally.so/r/RGppj9)

Conflicts found:
- Deadline: search-engine snippets of the same Tally form show "7 October 2026, 11:59 PM IST"; the form as fetched on 9 Oct shows 10 October. The hackathon page reader also noted the site FAQ gives 7 Oct (and top-30 on 10 Oct). Most likely an extension from 7 to 10 October with stale text left behind. — [Tally form](https://tally.so/r/RGppj9); [Hackathon page](https://quantumweek.tech/hackathon)
- Prototype: the submission page lists a prototype as a required deliverable, while the FAQ says a working prototype is not required in Round 1 and only the idea, logic and feasibility must be shown. — [Submission page](https://quantumweek.tech/hackathon/submission); [FAQ](https://quantumweek.tech/faq)

### Inferences
- Q-Rescue fits "Open Quantum Innovation" or "Quantum AI & Software"; a Qiskit QAOA notebook on a simulator is explicitly an accepted prototype format.
- With 30% on technical implementation and 20% on quantum relevance, a runnable QUBO/QAOA notebook with an honest classical baseline matters more than slide polish.
- Given the deadline conflict, the team should treat 10 Oct 11:59 PM IST as correct but submit early and confirm with quantumrit@msrit.edu.

### Gaps
- The specific Devfolio hackathon URL for Q-HACK INDIA was not found; the site links only to devfolio.co generically.
- No explicit statement on simulators versus real hardware beyond "classical simulators allowed"; the site says environment guidelines will accompany problem statements, which I did not find.
- No plagiarism policy, code-freeze rule or pre-existing-code rule was found.
- I did not open the Canva template, so required slide headings are unverified beyond "problem, solution, tech stack, architecture, roadmap".
