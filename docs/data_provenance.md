# Data Provenance & Source Inventory Audit

**Project:** PairCover-Q (Q-Rescue) — Quantum-Assisted Emergency Resource Allocation  
**Audit Date:** October 10, 2026  
**Status:** All Active Optimizers Use Explicit Synthetic Benchmark Scenarios  

---

## 1. Executive Summary & Inventory

This document provides a strict, verifiable accounting of all data sources, datasets, and scenarios referenced across the PairCover-Q repository.

### Inventory Summary

| Category | Item | Present in Repository? | Consumed by Optimizer? | Details |
| :--- | :--- | :---: | :---: | :--- |
| **Real EMS Data** | TNHSP "108 Ambulance" Dataset | **No** (0 records) | **No** | Access is gated behind an official data-request application form. No public download link exists. |
| **Real Registry Data** | TAEI Trauma Registry Dataset | **No** (0 records) | **No** | Gated behind an institutional data-request application. No public download link exists. |
| **Synthetic Scenario 1** | 5-qubit Hand-Checkable Case | **Yes** (`scenario.py`) | **Yes** | 2 ambulances ($A_1, A_2$), 3 calls ($C_1, C_2, C_3$), 5 binary variables. Used for mathematical regression testing. |
| **Synthetic Scenario 2** | 6-qubit PairCover-Q Demo | **Yes** (`scenario2.py`) | **Yes** | 3 residual ambulances ($A_1, A_2, A_3$), 2 calls ($C_2, C_3$), 6 binary variables. Models mutual backup penalty ($\lambda g_{12} = 10$). |
| **Official EMS Aggregate Stats** | Tamil Nadu State Fleet Aggregates | **Documented in Notes** | **No** (Contextual only) | Cites the MCC/TNHSRP February 2022 report (1,237 ambulances statewide: 84.4% BLS, 10.0% ALS, 5.2% NLS). |

> **Scientific Disclosure:** No real-world ambulance CAD records, patient identifiers, or municipal GPS tracking data are present in or consumed by the optimization engines in this repository. All dispatch calculations are executed on explicitly defined synthetic benchmarks.

---

## 2. Official Data Sources Investigated

### 2.1 Tamil Nadu Health System Project — 108 Ambulance Dataset
- **Official Portal:** [https://tnhsp.org/pages/view/108_Application](https://tnhsp.org/pages/view/108_Application)
- **Status as of October 10, 2026:** Verified active via HTTP.
- **Access Mechanism:** The page states that a curated and anonymized research dataset exists for non-commercial research, but access requires submitting a formal **"Data Download Request Form"** via an embedded Google Form link.
- **Direct Download Available:** **No.** There is no direct public link to a CSV, SQLite, Parquet, or JSON archive.
- **Documented Fields (from Official Portal Description):**
  - **Identifiers:** `Case_ID` (unique incident identifier).
  - **Classification:** `Emergency / IFT` (emergency call vs. inter-facility transfer), `Emergency Type`, `EM sub Type`, `triage`, `is_critical`, `Level`.
  - **Temporal Fields:** `Call Date (dd/mm/yyyy)`, `Date`, `Hour`, `Start Time`, `CW – Call Waiting`, `Case Assigned Time`, `Base Start Time`, `WB – Waiting at Base`, `Scene Arrival Time`, `Scene Departure Time`, `Scene – Time at Scene`, `Hospital Reach Time`, `Hospital Start Time`, `Base Reach Time`, `Case Closing Date & Time`.
  - **Spatial & Fleet:** `Caller District`, `Caller Taluk`, `Vehicle_District`, `Ambulance_Number`, `Vehicle Type (ALS/BLS)`, `Area`.
  - **Operational Distances:** `BS(KM) – Base to Scene`, `SH(KM) – Scene to Hospital`, `HB(KM) – Hospital to Base`, `B2B(KM) – Base to Base total distance`, `Response Time`, `Benchmark`.
- **Known Data Limitations:**
  - **No Precise GPS Coordinates:** The dataset documents caller origin at the taluk level and ambulance base at the district level; no exact latitude/longitude coordinates are documented.
  - **Single Dispatched Vehicle Recorded:** Records reflect which vehicle was *historically dispatched*, but not the locations or candidate travel times of *all other available fleet units* at that exact decision epoch.

### 2.2 Tamil Nadu Accident & Emergency Care Initiative (TAEI) Trauma Registry
- **Official Portal:** [https://tnhsp.org/pages/view/TAEI_Application](https://tnhsp.org/pages/view/TAEI_Application)
- **Status as of October 10, 2026:** Verified active via HTTP.
- **Access Mechanism:** Formal data download request form for approved academic/clinical research.
- **Direct Download Available:** **No.**
- **Documented Fields:** Patient arrival time, mechanism of injury, injury severity score (ISS), trauma center admission timestamps, outcome status.
- **Role in Project:** Serves as a potential clinical source for tuning severity priority weights ($w_j$) in trauma dispatch, but does not provide vehicle dispatch matrices.

---

## 3. The "Missing Input Problem" in Historical EMS Data

A common misunderstanding in emergency dispatch optimization is assuming that historical ambulance run records can be directly plugged into an optimization algorithm:

```text
Historical Record:
[Incident C1] -> Ambulance A1 arrived in 8 minutes.

What the QUBO / Optimizer Actually Needs:
Decision Epoch at t = 10:45 AM:
- Travel time A1 -> C1: ? min
- Travel time A2 -> C1: ? min
- Travel time A3 -> C1: ? min
- Travel time A1 -> C2: ? min
- Travel time A2 -> C2: ? min
- Travel time A3 -> C2: ? min
- Idle/busy status of A1, A2, A3 at t = 10:45 AM: ?
```

### Why Historical Response Times Do Not Equal Optimizer Inputs:
1. **Unselected Counterfactuals:** Historical data only records $t_{\text{dispatched}, c}$. It never records the travel time of unselected ambulances $t_{u, c}$ ($u \ne \text{dispatched}$).
2. **Missing All-Pairs Travel-Time Matrix:** A mathematical matching engine requires an $m \times n$ matrix of candidate response times for every available unit to every pending call.
3. **Fleet State Reconstruction:** To optimize real dispatch, an external simulation or AVL (Automatic Vehicle Location) feed must reconstruct the state of every unit in the fleet at each decision epoch.

Therefore, PairCover-Q explicitly distinguishes:
- **Historical Records:** Used strictly for demand forecasting, response time distribution fitting, and priority weight calibration.
- **Optimizer Input Matrix:** Derived from road-network travel time matrices (e.g. OSRM / OpenStreetMap) or calibrated synthetic topologies.

---

## 4. Local CSV Upload & Validation Architecture

To facilitate future ingestion when official TNHSP data or open emergency records (e.g., Seattle 911, London Ambulance Service) are obtained, the repository provides a local validation workflow in `src/qrescue/data/validator.py`:

1. **Schema Mapping & Detection:** Automatically detects available columns across common naming conventions:
   - Call timestamp (`Call_Date`, `Call Date`, `timestamp`, `call_time`)
   - Triage priority (`triage`, `priority`, `criticality`, `severity`)
   - Case type (`Emergency Type`, `incident_type`, `call_type`)
   - Fleet unit type (`Vehicle Type`, `unit_type`, `als_bls`)
   - Response duration (`Response Time`, `response_time_min`, `duration`)
   - Travel distance (`Distance`, `BS(KM)`, `distance_km`)
2. **Data Integrity Checks:**
   - Detects malformed date formats and invalid timestamp order (e.g., scene arrival before assignment).
   - Identifies missing critical values and negative durations.
   - Calculates empirical quantiles (min, median, p90, max) on genuine observed response times.
3. **Privacy & Security Boundaries:**
   - Private CSV files are excluded from Git via `.gitignore` (`data/raw/`, `data/uploads/`, `*.csv`).
   - The UI displays descriptive distributions only and strictly forbids claiming that historical observations represent real-time dispatch state without matrix imputation.

---

## 5. Steps Required to Obtain and Integrate Official Data

For future project phases or research continuations seeking official Tamil Nadu data:

1. **Submit Institutional Data Request:** Complete the official Google Form on `https://tnhsp.org/pages/view/108_Application` stating research affiliation, purpose, and commitment to anonymized data governance.
2. **Institutional Review & Approval:** Await clearance from the Project Director, TNHSP (`pdtnhsp@gmail.com`).
3. **Data Ingestion via Local Validator:** Place approved CSVs in `data/raw/` (ignored by git). Run the schema validator:
   ```bash
   python -m qrescue.data.validator data/raw/tnhsp_108_sample.csv
   ```
4. **Synthetic Matrix Imputation:** Use taluk centroids and road-network distance engines (OSRM / OpenRouteService) to generate counterfactual travel times $t_{u, c}$ before invoking the QUBO or QAOA solvers.
