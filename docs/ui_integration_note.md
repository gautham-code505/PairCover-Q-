# UI Integration Contract — `app/ui_components.py`

Owner of `app/main.py`: Antigravity. This document is the contract between `main.py` and the UI layer.
`ui_components.py` imports only `streamlit`, `plotly` and `ui_helpers.py` (which is stdlib-only). They never import `qrescue`, so backend edits cannot break them.

```python
import streamlit as st
import ui_components as ui            # NOT `import *`; ui.__all__ is the public API
```

Run from the project root so `.streamlit/config.toml` (dark base theme) is picked up: `streamlit run app/main.py`.

## 1. Responsibilities

| Backend / `main.py` computes | UI only formats and draws |
|---|---|
| QUBO, Ising, QAOA, classical baselines, feasibility (validator), raw objective, response cost, coverage penalty | numbers as given, with units and labels |
| Which sample is "best feasible"; `objective_value` of a QAOA result | highlighting the lowest *feasible* objective among results already supplied (labelled derived) |
| Classification of each measured bitstring as feasible/infeasible; QUBO energy and raw objective per sample | decoding a key into (ambulance, call) pairs by position (presentation) |
| Exact classical optimum, baselines (uniform random etc.), surrogate offset | plotting them if supplied; never deriving them |
| Per-evaluation optimizer history | plotting it if supplied; never reconstructing it |

Rule: **if a value is absent the UI shows “—” or an empty state, never 0 and never a placeholder.**

## 2. Result schema

Every method returns one dict (numpy types are accepted and normalised):

```python
{
  "scenario_id": str, "method": str,
  "assignments": [("A1", "C2"), ...],   # or dicts {ambulance_id, call_id, travel_time?}
  "unserved_calls": ["C3"],
  "weighted_response_cost": float, "coverage_penalty": float,
  "objective_value": float,            # RAW objective of the returned assignment (see §2.2)
  "feasible": bool,                    # from the backend validator
  "runtime_seconds": float,
  "experiment": dict,                  # {} for classical methods
}
```

### 2.1 Distinguishing classical vs sampled QAOA
Set `experiment["kind"]` to one of `classical_exact`, `classical_heuristic`, `qaoa_sampled`, `qaoa_statevector`. If absent, the UI **infers** from the method name / QAOA keys and marks it “(inferred)”.

### 2.2 Which number is which
| Quantity | Where | Meaning |
|---|---|---|
| **Raw objective** | `objective_value`; `experiment["best_cost"]` | physical cost of one feasible assignment = response cost + coverage penalty |
| **Expected energy ⟨H⟩** | `experiment["initial_qubo_energy"]`, `["final_qubo_energy"]` | statevector expectation (+offset); a property of the quantum state, **not** a dispatch cost |
| **Sampled mean energy** | `experiment["sampled_mean_qubo_energy"]` | mean QUBO energy over shots |
| **Penalised surrogate** | `["final_surrogate_objective"]`, `["sampled_mean_surrogate_objective"]` | energy + backend constant; backend must supply the shifted value (UI never adds “+60”) |

For a sampled QAOA result, `objective_value` / `assignments` / `feasible` describe the **best feasible measured sample**. If no sample was feasible: `feasible=False`, `assignments=[]`, `objective_value=None` (or `inf`) — the UI will say so and will not present an expected energy as a plan.

### 2.3 `experiment` keys the UI reads (all optional)
Keys already produced by `scripts/run_qaoa_scenario2.py`: `p, seed, maxiter, shots, scale, success, message, nfev, initial_params, final_params, initial_qubo_energy, final_qubo_energy, sv_feas_rate, sv_opt_prob, sampled_feas_rate, sampled_opt_prob, optimum_hits, best_cost`.

**Requested additions** (not produced today; UI degrades gracefully without them):

| Key | Shape | Enables |
|---|---|---|
| `kind` | see §2.1 | provenance badges without inference |
| `run_id` | str | keep every seed/run in history (otherwise only the latest per scenario+method is kept) |
| `timestamp`, `backend` | str | history column; “Backend” badge (UI never assumes a backend) |
| `history` | `{"values":[…], "quantity":"expected_qubo_energy"\|"surrogate"\|"raw_objective", "x":"function_evaluation"\|"iteration", "running_best":bool, "reference":{"value","label","same_quantity":true}}` | convergence chart. Record inside the `cost_func` closure. A reference line is drawn only if `same_quantity` is true. |
| `sample_table` | `[{bitstring, count, feasible, assignments, qubo_energy, raw_objective}]` | per-sample feasibility, energies, decoded plans (preferred) |
| `counts` + `feasible_bitstrings` | `{key:int}`, `{key:bool}` | fallback; without feasibility flags samples show “Not classified” |
| `bitstring_order` | `"qiskit_little_endian"` (default) \| `"variable_order"` | documents key convention; `x_k = key[n-1-k]` for little-endian, matching `decode_qiskit_bitstring` |
| `optimal_bitstring` | str in the same convention | “★ exact optimum” marker |
| `baselines` | `[{label, feasibility_rate, optimum_probability}]` | reference bars (e.g. uniform-random 13/64) |
| `final_surrogate_objective`, `sampled_mean_*` | float | extra rows in the “Which number is which” table |

Without `history`, the Quantum Lab shows an empty state plus a two-bar *initial → final* chart labelled “not a convergence curve”. Initial/final energies are never promoted to a trace.

### 2.4 Scenario dict (UI-side)
`{"scenario_id", "description", "ambulances": [ids], "calls": [ids], "priority_weights": {call: w}, "travel_times": {(amb, call): minutes}, "variables": [(amb, call), ...]}` — `variables` (the QUBO variable order, e.g. `VARIABLES_2`) is needed only to decode bitstrings.

## 3. Public rendering functions

| Function | Args | Returns |
|---|---|---|
| `apply_theme()` | — | call once after `st.set_page_config` |
| `render_view_header(view, scenario_id=None)` | `view` ∈ `ui.VIEWS` | — |
| `synthetic_data_banner(extra="")` | | — (optional extra banner) |
| `render_overview(scenario, results=None, failures=None, key_prefix="ov")` | | — |
| `render_scenario_builder(scenario, methods, fields=(), default_methods=None, editable=(), key_prefix="sb")` | `fields`: `[{key,label,type: int\|float\|select\|bool,default,min,max,step,options,help}]`; `editable` ⊆ `("availability","priorities")` — only if the backend honours them | `{"run", "methods", "params", "available_ambulances", "priority_weights"}` |
| `render_dispatch_simulator(results, scenario=None, key_prefix="ds")` | | — (tabs: Assignment, Method comparison, Objective definitions) |
| `render_quantum_lab(results, scenario=None, key_prefix="ql")` | list or single result; QAOA runs auto-selected | — |
| `render_benchmark_analytics(results, failures=None, key_prefix="bm")` | | — (tabs: Summary, QAOA diagnostics, Run history) |
| `run_with_loading(label, fn, *a, steps=None, failures_state=None, method=None, scenario_id=None, **kw)` | | `(ok, value_or_exception)`; renders status box / error panel |
| `retain_result(state, result)`, `retain_failure(state, failure)`, `make_failure(method, scenario_id, exc, stage=None)` | `state`: `st.session_state` | updated list |
| Lower-level: `render_assignment_view`, `render_method_comparison`, `render_experiment_history`, `render_failures`, `empty_state`, `error_state`, `callout`, `skeleton`, `loading_state`, `kpi_row`, `badge`, `validate_result`, `build_*` figure builders | | |

Always pass a distinct `key_prefix` if the same function is rendered twice on one page.

## 4. How `main.py` calls each view

```python
st.set_page_config(page_title="PairCover-Q", page_icon="🚑", layout="wide")
ui.apply_theme()
ss = st.session_state
ss.setdefault("pq_results", []); ss.setdefault("pq_failures", [])

scenario = load_scenario()                       # adapter → dict (§2.4); None if unavailable
view = st.sidebar.radio("View", ui.VIEWS)
ui.render_view_header(view, (scenario or {}).get("scenario_id"))
ui.synthetic_data_banner()

if view == "Overview":
    ui.render_overview(scenario, ss["pq_results"], ss["pq_failures"])
elif view == "Scenario Builder":
    sel = ui.render_scenario_builder(scenario, METHODS, FIELDS)
    if sel["run"]:
        for m in sel["methods"]:
            ok, res = ui.run_with_loading(f"Running {m}", backend_run, m, scenario, sel["params"],
                                          failures_state=ss, method=m,
                                          scenario_id=(scenario or {}).get("scenario_id"))
            if ok:
                ui.retain_result(ss, res)        # → ss["pq_results"]
elif view == "Dispatch Simulator":
    ui.render_dispatch_simulator(ss["pq_results"], scenario)
elif view == "Quantum Lab":
    ui.render_quantum_lab(ss["pq_results"], scenario)
else:
    ui.render_benchmark_analytics(ss["pq_results"], ss["pq_failures"])
```

## 5. Failed computations
- Raise from the backend wrapper (any `Exception`); `run_with_loading` shows a red error panel with technical details and stores a failure record (`method, scenario_id, error_type, message, stage, timestamp`).
- Failures carry **no metrics** and are listed on Overview and Benchmark Analytics; they are excluded from every chart and aggregate.
- Do **not** return a half-filled result dict for a crash. Return one only for a run that *completed* but found nothing feasible (`feasible=False`).
- Optimizer non-convergence is not a crash: return the result with `experiment["success"]=False` and `message`; the Quantum Lab shows a red “did not report success” notice and the run stays in history.

## 6. Retaining results
`retain_result(st.session_state, result)` stores plain-Python copies under `pq_results` (≤500). Identity is `experiment["run_id"]` if set (every run kept) else `(scenario_id, method)` (latest replaces earlier). Re-running a method therefore never duplicates rows. Wrap backend calls in `@st.cache_data` only if they are deterministic; otherwise rely on session state.

## 7. Optional metrics
Pass what you have. Missing metric → “—”; missing chart input → empty state naming what was not supplied; non-schema results → collapsed “deviate from schema” warning while renderable ones still display. Never pass placeholder values (0, 1.0, dummy bitstrings) for unavailable metrics.

## 8. Unresolved assumptions
1. Backend adopts the “requested additions” above; today there is no optimizer history and no bitstring counts in the returned dict (counts are computed inside the script but not returned).
2. Parameter names β/γ assume Qiskit `QAOAAnsatz` ordering (mixer first, then cost), as the script documents.
3. `objective_value` for QAOA = raw objective of the best feasible sample (§2.2).
4. Scenario `travel_times` keys are `(ambulance, call)` tuples as in `scenario2.py`.

## 9. Validation
- **Executed:** `pytest tests/test_ui_helpers.py tests/test_ui_components_smoke.py` — pure helpers plus Streamlit `AppTest` rendering of all five views with populated, empty and malformed synthetic fixtures (Streamlit 1.65.0, Plotly 7.1.0). These show the code runs without exceptions; they do **not** verify visual layout.
- **Not executed:** browser rendering (CSS, Plotly interaction, narrow screens, screen readers) and any run against real backend output. Use the checklist in `docs/ui_ux_spec.md` §8.
- Test fixtures are labelled synthetic; their numbers are not QAOA output.
