"""Pure presentation helpers for PairCover-Q (no Streamlit, Plotly or backend imports).

Everything here reshapes or formats values the backend already produced so the
UI can display them. Nothing here optimises, samples, evaluates feasibility or
recomputes an objective. The few derived figures (shares, best-of-N, differences
against a reference) are returned with explicit "derived" semantics so the UI
can label them.

Importable without any third-party package, so it is unit-testable anywhere.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

# --------------------------------------------------------------------------- #
# Vocabulary
# --------------------------------------------------------------------------- #

RESULT_KEYS = (
    "scenario_id", "method", "assignments", "unserved_calls",
    "weighted_response_cost", "coverage_penalty", "objective_value",
    "feasible", "runtime_seconds", "experiment",
)
NUMERIC_KEYS = ("weighted_response_cost", "coverage_penalty", "objective_value", "runtime_seconds")

#: Names for the different "numbers that look like cost". The UI never merges them.
QUANTITIES = {
    "raw_objective": (
        "Raw objective",
        "Physical dispatch cost of ONE concrete, feasible assignment: weighted response cost "
        "+ coverage penalty. This is `objective_value` in a result."),
    "qubo_energy": (
        "QUBO energy",
        "Value of the penalised QUBO for a bitstring. Infeasible bitstrings carry constraint "
        "penalties, so it is not a dispatch cost."),
    "expected_energy": (
        "Expected energy ⟨H⟩",
        "Statevector expectation of the cost Hamiltonian (+ offset) at the optimizer's "
        "parameters. An average over the whole quantum state, not the cost of any one assignment."),
    "sampled_mean_energy": (
        "Sampled mean energy",
        "Average QUBO energy over measured shots. Shot-noise dependent."),
    "surrogate": (
        "Penalised surrogate objective",
        "QUBO energy shifted by the backend's constant so it is comparable with the raw "
        "objective on feasible states. Still penalised for infeasible states."),
}

KIND_LABELS = {
    "classical_exact": ("Classical · exact", "info"),
    "classical_heuristic": ("Classical · heuristic", "info"),
    "qaoa_sampled": ("QAOA · simulated, sampled", "violet"),
    "qaoa_statevector": ("QAOA · exact statevector", "violet"),
}

HISTORY_QUANTITIES = {
    "expected_qubo_energy": "Expected QUBO energy ⟨H⟩ + offset",
    "surrogate": "Penalised surrogate objective",
    "raw_objective": "Raw objective",
    "unspecified": "Value (quantity not specified by backend)",
}

_LEGACY_HISTORY_KEYS = ("energy_history", "cost_history", "convergence", "objective_history")
_COUNT_KEYS = ("counts", "measurement_counts")


# --------------------------------------------------------------------------- #
# Value coercion and formatting
# --------------------------------------------------------------------------- #

def to_py(value: Any) -> Any:
    """Recursively convert numpy scalars/arrays and mappings to plain Python."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {k: to_py(v) for k, v in value.items()}
    if hasattr(value, "tolist"):  # numpy arrays and numpy scalars
        try:
            return to_py(value.tolist())
        except Exception:  # noqa: BLE001
            return str(value)
    if isinstance(value, (list, tuple, set, frozenset)):
        return [to_py(v) for v in value]
    return value


def is_number(value: Any) -> bool:
    value = to_py(value)
    return isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isnan(value)


def as_float(value: Any) -> float | None:
    """Float or None. NaN and non-numerics become None; ±inf is preserved."""
    value = to_py(value)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return None if math.isnan(value) else value


def as_bool(value: Any) -> bool | None:
    """Tri-state boolean: True / False / None (unknown)."""
    value = to_py(value)
    return value if isinstance(value, bool) else None


def fmt_num(value: Any, digits: int = 2, suffix: str = "") -> str:
    v = as_float(value)
    if v is None:
        return "—"
    if math.isinf(v):
        return "∞" if v > 0 else "−∞"
    return f"{v:,.{digits}f}{suffix}"


def fmt_pct(value: Any, digits: int = 1) -> str:
    v = as_float(value)
    return "—" if v is None else f"{100 * v:.{digits}f}%"


def fmt_seconds(value: Any) -> str:
    v = as_float(value)
    if v is None:
        return "—"
    if 0 < v < 0.001:
        return "< 1 ms"  # sub-millisecond classical runs must not read as "0 ms"
    return f"{v * 1000:.0f} ms" if v < 1 else f"{v:.2f} s"


def fmt_feasible(value: Any) -> str:
    b = as_bool(value)
    return "✔ feasible" if b is True else "✖ infeasible" if b is False else "? unknown"


# --------------------------------------------------------------------------- #
# Result normalisation / validation
# --------------------------------------------------------------------------- #

def validate_result(result: Any) -> list[str]:
    """Problems with a result dict versus the documented schema (empty = OK)."""
    if not isinstance(result, Mapping):
        return [f"Result must be a mapping, got {type(result).__name__}."]
    problems = [f"Missing key: {k}" for k in RESULT_KEYS if k not in result]
    for k in NUMERIC_KEYS:
        if result.get(k) is not None and as_float(result[k]) is None:
            problems.append(f"{k} is not numeric ({type(result[k]).__name__}).")
    if result.get("feasible") is not None and as_bool(result["feasible"]) is None:
        problems.append("feasible is not a boolean.")
    for k in ("assignments", "unserved_calls"):
        if result.get(k) is not None and not isinstance(to_py(result[k]), list):
            problems.append(f"{k} is not a list.")
    if result.get("experiment") is not None and not isinstance(to_py(result["experiment"]), dict):
        problems.append("experiment is not a dict.")
    return problems


def normalize_result(result: Mapping[str, Any]) -> dict[str, Any]:
    """Defensive copy with plain-Python types and None for anything missing.

    Never invents a value: absent metrics stay ``None`` (rendered as "—").
    """
    r = to_py(result) if isinstance(result, Mapping) else {}
    exp = r.get("experiment")
    return {
        "scenario_id": None if r.get("scenario_id") is None else str(r["scenario_id"]),
        "method": "unknown" if r.get("method") is None else str(r["method"]),
        "assignments": r.get("assignments") if isinstance(r.get("assignments"), list) else [],
        "unserved_calls": r.get("unserved_calls") if isinstance(r.get("unserved_calls"), list) else [],
        "weighted_response_cost": as_float(r.get("weighted_response_cost")),
        "coverage_penalty": as_float(r.get("coverage_penalty")),
        "objective_value": as_float(r.get("objective_value")),
        "feasible": as_bool(r.get("feasible")),
        "runtime_seconds": as_float(r.get("runtime_seconds")),
        "experiment": exp if isinstance(exp, dict) else {},
        "_problems": validate_result(result),
    }


def normalize_results(results: Iterable[Any] | None) -> tuple[list[dict[str, Any]], list[str]]:
    """Normalise a list; returns (usable results, per-result problem strings)."""
    good, issues = [], []
    for i, r in enumerate(results or []):
        if not isinstance(r, Mapping):
            issues.append(f"Result #{i + 1}: not a mapping, skipped.")
            continue
        n = normalize_result(r)
        if n["_problems"]:
            issues.append(f"Result #{i + 1} ({n['method']}): " + "; ".join(n["_problems"]))
        good.append(n)
    return good, issues


def normalize_assignments(assignments: Sequence[Any] | None,
                          travel_times: Mapping[Any, Any] | None = None) -> list[dict[str, Any]]:
    """(ambulance, call) pairs or dicts → rows. Travel time only if supplied."""
    rows = []
    for item in to_py(assignments) or []:
        if isinstance(item, Mapping):
            amb = item.get("ambulance_id", item.get("ambulance", item.get("amb")))
            call = item.get("call_id", item.get("call"))
            tt = item.get("travel_time", item.get("response_time"))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            amb, call, tt = item[0], item[1], None
        else:
            continue
        if tt is None and travel_times:
            tt = travel_times.get((amb, call))
        rows.append({"ambulance": amb, "call": call, "travel_time": as_float(tt)})
    return rows


# --------------------------------------------------------------------------- #
# Provenance: classical result vs sampled QAOA result
# --------------------------------------------------------------------------- #

def provenance(result: Mapping[str, Any]) -> dict[str, Any]:
    """Classify how a result was produced. Prefers ``experiment['kind']``.

    Falls back to inference from experiment keys / method name and says so
    (``inferred=True``) so the UI can mark it.
    """
    exp = (to_py(result.get("experiment")) or {}) if isinstance(result, Mapping) else {}
    kind = exp.get("kind")
    if kind in KIND_LABELS:
        label, tone = KIND_LABELS[kind]
        return {"kind": kind, "label": label, "tone": tone, "inferred": False, "is_qaoa": kind.startswith("qaoa")}
    method = str(result.get("method", "")).lower() if isinstance(result, Mapping) else ""
    if any(k in exp for k in ("final_params", "sampled_feas_rate", "sv_feas_rate")) or "qaoa" in method:
        return {"kind": "qaoa_sampled", "label": "QAOA · simulator (inferred)", "tone": "violet",
                "inferred": True, "is_qaoa": True}
    if any(w in method for w in ("brute", "exact", "classical", "nearest", "greedy")):
        return {"kind": "classical", "label": "Classical (inferred)", "tone": "info",
                "inferred": True, "is_qaoa": False}
    return {"kind": "unspecified", "label": "Method type unspecified", "tone": "info",
            "inferred": True, "is_qaoa": False}


# --------------------------------------------------------------------------- #
# Retaining results / failures (works with st.session_state or any MutableMapping)
# --------------------------------------------------------------------------- #

def _run_identity(result: Mapping[str, Any]) -> tuple:
    exp = result.get("experiment") if isinstance(result.get("experiment"), Mapping) else {}
    if exp.get("run_id") is not None:
        return ("run", str(exp["run_id"]))
    return ("latest", str(result.get("scenario_id")), str(result.get("method")))


def retain_result(state: MutableMapping, result: Mapping[str, Any],
                  key: str = "pq_results", max_items: int = 500) -> list[dict[str, Any]]:
    """Store a result: replaces an earlier run with the same identity, else appends.

    Identity is ``experiment['run_id']`` when present (keeps every seed/run),
    otherwise ``(scenario_id, method)`` (keeps only the latest). Stored values
    are plain Python so they survive reruns and JSON export.
    """
    clean = to_py(result)
    items = [r for r in state.get(key, []) if _run_identity(r) != _run_identity(clean)]
    items.append(clean)
    state[key] = items[-max_items:]
    return state[key]


def make_failure(method: str, scenario_id: str | None, error: BaseException | str,
                 stage: str | None = None) -> dict[str, Any]:
    """Failure record for a computation that raised. Contains no metrics."""
    return {
        "method": str(method), "scenario_id": None if scenario_id is None else str(scenario_id),
        "error_type": type(error).__name__ if isinstance(error, BaseException) else "Error",
        "message": str(error) or (type(error).__name__ if isinstance(error, BaseException) else "Unknown error"),
        "stage": stage, "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def retain_failure(state: MutableMapping, failure: Mapping[str, Any],
                   key: str = "pq_failures", max_items: int = 50) -> list[dict[str, Any]]:
    state[key] = (list(state.get(key, [])) + [dict(failure)])[-max_items:]
    return state[key]


def latest_by_method(results: Sequence[Mapping[str, Any]], scenario_id: str | None = None) -> list[Mapping[str, Any]]:
    """Last result per method (for one scenario if given), in first-seen order."""
    out: dict[str, Mapping[str, Any]] = {}
    for r in results:
        if scenario_id is not None and r.get("scenario_id") != scenario_id:
            continue
        out.pop(r["method"], None)
        out[r["method"]] = r
    return list(out.values())


# --------------------------------------------------------------------------- #
# Derived comparisons (display-only; callers must label as derived)
# --------------------------------------------------------------------------- #

def best_feasible(results: Sequence[Mapping[str, Any]]) -> tuple[list[str], float | None]:
    """(methods tied for lowest feasible finite objective, that objective)."""
    cand = [(r["objective_value"], r["method"]) for r in results
            if r.get("feasible") is True and r.get("objective_value") is not None
            and math.isfinite(r["objective_value"])]
    if not cand:
        return [], None
    best = min(v for v, _ in cand)
    return [m for v, m in cand if math.isclose(v, best, rel_tol=1e-9, abs_tol=1e-12)], best


def aggregate_runs(results: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Per (scenario, method): run counts, feasible rate, objective range over FEASIBLE runs only."""
    groups: dict[tuple, list[Mapping[str, Any]]] = {}
    for r in results:
        groups.setdefault((r.get("scenario_id"), r["method"]), []).append(r)
    rows = []
    for (sid, m), rs in groups.items():
        known = [r for r in rs if r.get("feasible") is not None]
        feas = [r for r in rs if r.get("feasible") is True]
        objs = [r["objective_value"] for r in feas
                if r.get("objective_value") is not None and math.isfinite(r["objective_value"])]
        rts = [r["runtime_seconds"] for r in rs if r.get("runtime_seconds") is not None]
        rows.append({
            "scenario_id": sid, "method": m, "runs": len(rs),
            "feasible_runs": len(feas), "known_feasibility_runs": len(known),
            "feasible_rate": len(feas) / len(known) if known else None,
            "objective_min": min(objs) if objs else None,
            "objective_mean": sum(objs) / len(objs) if objs else None,
            "objective_max": max(objs) if objs else None,
            "runtime_mean": sum(rts) / len(rts) if rts else None,
            "provenance": provenance(rs[-1])["label"],
        })
    return rows


def objective_difference(results: Sequence[Mapping[str, Any]], reference_method: str) -> list[dict[str, Any]]:
    """Per scenario: best feasible objective of each method vs the reference method's best feasible."""
    best: dict[tuple, float] = {}
    for r in results:
        o = r.get("objective_value")
        if r.get("feasible") is True and o is not None and math.isfinite(o):
            k = (r.get("scenario_id"), r["method"])
            best[k] = min(best.get(k, o), o)
    rows = []
    for (sid, m), o in best.items():
        ref = best.get((sid, reference_method))
        if m == reference_method or ref is None:
            continue
        rows.append({"scenario_id": sid, "method": m, "objective": o, "reference": ref,
                     "abs_diff": o - ref, "pct_diff": None if ref == 0 else 100.0 * (o - ref) / abs(ref)})
    return rows


# --------------------------------------------------------------------------- #
# QAOA experiment accessors (all read-only views of backend values)
# --------------------------------------------------------------------------- #

def energy_summary(exp: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Rows for the energy/objective glossary: only quantities the backend supplied."""
    spec = [
        ("initial_qubo_energy", "expected_energy", "Initial expected energy"),
        ("final_qubo_energy", "expected_energy", "Final expected energy"),
        ("final_surrogate_objective", "surrogate", "Final expected surrogate"),
        ("sampled_mean_qubo_energy", "sampled_mean_energy", "Sampled mean energy"),
        ("sampled_mean_surrogate_objective", "surrogate", "Sampled mean surrogate"),
        ("best_cost", "raw_objective", "Best feasible sample · raw objective"),
    ]
    rows = []
    for key, q, label in spec:
        v = as_float(exp.get(key))
        if v is not None:
            rows.append({"label": label, "value": v, "quantity": QUANTITIES[q][0],
                         "meaning": QUANTITIES[q][1], "key": key})
    return rows


def optimizer_status(exp: Mapping[str, Any]) -> dict[str, Any]:
    """Optimizer outcome: status in {'success','failed','unknown'} plus raw message/counts."""
    ok = as_bool(exp.get("success"))
    return {
        "status": "success" if ok is True else "failed" if ok is False else "unknown",
        "message": None if exp.get("message") is None else str(exp["message"]),
        "nfev": as_float(exp.get("nfev")), "maxiter": as_float(exp.get("maxiter")),
    }


def get_history(exp: Mapping[str, Any]) -> dict[str, Any] | None:
    """Recorded optimizer history, or None if the backend did not record one.

    Preferred: ``exp['history'] = {"values": [...], "quantity": ..., "x": ...,
    "running_best": bool, "reference": {"value", "label", "same_quantity"}}``.
    A bare list under a legacy key is accepted but flagged quantity="unspecified".
    The two-point initial/final energies are NOT a history and are never promoted to one.
    """
    h = exp.get("history")
    values, meta = None, {}
    if isinstance(h, Mapping):
        values, meta = h.get("values"), dict(h)
    elif isinstance(h, list):
        values = h
    else:
        for k in _LEGACY_HISTORY_KEYS:
            if isinstance(exp.get(k), list) and exp[k]:
                values = exp[k]
                break
    nums = [as_float(v) for v in (values or [])]
    nums = [v for v in nums if v is not None and math.isfinite(v)]
    if len(nums) < 2:
        return None
    quantity = meta.get("quantity") if meta.get("quantity") in HISTORY_QUANTITIES else "unspecified"
    ref = meta.get("reference") if isinstance(meta.get("reference"), Mapping) else None
    if ref is not None and not (ref.get("same_quantity") is True and as_float(ref.get("value")) is not None):
        ref = None  # never draw a reference of a different/unknown quantity
    return {
        "values": nums, "quantity": quantity, "quantity_label": HISTORY_QUANTITIES[quantity],
        "x_label": {"function_evaluation": "Function evaluation", "iteration": "Optimizer iteration"}.get(
            meta.get("x"), "Step (unit not specified)"),
        "running_best": meta.get("running_best") is True,
        "reference": None if ref is None else {"value": as_float(ref["value"]), "label": str(ref.get("label", "Reference"))},
    }


def outcome_split(exp: Mapping[str, Any]) -> dict[str, float | None] | None:
    """Shares of sampled shots: exact optimum / other feasible / infeasible (derived).

    Needs the backend's ``sampled_feas_rate``; optimum share needs ``optimum_hits`` and ``shots``.
    """
    feas = as_float(exp.get("sampled_feas_rate"))
    if feas is None:
        return None
    shots, hits = as_float(exp.get("shots")), as_float(exp.get("optimum_hits"))
    opt = hits / shots if (shots and hits is not None) else None
    other = feas - opt if opt is not None and feas >= opt else (feas if opt is None else None)
    return {"optimum": opt, "other_feasible": other, "infeasible": max(0.0, 1.0 - feas), "feasible_total": feas}


def decode_bitstring(bitstring: str, variables: Sequence[Sequence[Any]] | None,
                     order: str = "qiskit_little_endian") -> list[tuple[Any, Any]] | None:
    """Map a measured key to its (ambulance, call) pairs — positional presentation only.

    ``qiskit_little_endian`` (the backend's documented convention): key is
    q_{n-1}…q_0, so x_k = key[n-1-k]. ``variable_order``: x_k = key[k].
    Feasibility is NOT assessed here; that belongs to the backend validator.
    """
    s = str(bitstring).replace(" ", "")
    if not variables or len(s) != len(variables) or set(s) - {"0", "1"}:
        return None
    n = len(s)
    idx = (lambda k: n - 1 - k) if order == "qiskit_little_endian" else (lambda k: k)
    return [tuple(variables[k]) for k in range(n) if s[idx(k)] == "1"]


def build_sample_rows(exp: Mapping[str, Any], variables: Sequence[Sequence[Any]] | None = None,
                      order: str | None = None) -> list[dict[str, Any]]:
    """Rows for the measured-sample view, most frequent first.

    Prefers the backend's ``sample_table`` (bitstring, count, feasible, qubo_energy,
    raw_objective, assignments). Falls back to bare ``counts`` — then feasibility
    stays unknown unless ``feasible_bitstrings`` is supplied. Probability is
    count ÷ total of the recorded counts.
    """
    order = order or exp.get("bitstring_order") or "qiskit_little_endian"
    feas_map = exp.get("feasible_bitstrings") if isinstance(exp.get("feasible_bitstrings"), Mapping) else {}
    table = exp.get("sample_table")
    entries: list[dict[str, Any]] = []
    if isinstance(table, list) and table:
        entries = [dict(e) for e in table if isinstance(e, Mapping) and e.get("bitstring") is not None]
    else:
        counts = next((exp[k] for k in _COUNT_KEYS if isinstance(exp.get(k), Mapping) and exp[k]), None)
        entries = [{"bitstring": k, "count": v} for k, v in (counts or {}).items()]
    total = sum(as_float(e.get("count")) or 0.0 for e in entries)
    rows = []
    for e in entries:
        bs = str(e["bitstring"])
        count = as_float(e.get("count"))
        assign = e.get("assignments")
        if not isinstance(assign, list):
            assign = decode_bitstring(bs, variables, order)
        feas = as_bool(e.get("feasible"))
        if feas is None:
            feas = as_bool(feas_map.get(bs)) if feas_map else None
        rows.append({
            "bitstring": bs, "count": count,
            "probability": (count / total) if (count is not None and total) else as_float(e.get("probability")),
            "feasible": feas, "assignments": assign,
            "qubo_energy": as_float(e.get("qubo_energy")), "raw_objective": as_float(e.get("raw_objective")),
        })
    rows.sort(key=lambda r: (r["count"] is None, -(r["count"] or 0)))
    return rows


def format_assignments(pairs: Sequence[Any] | None) -> str:
    """'A1→C2, A3→C3'; '—' when unknown; '∅ (none)' when empty."""
    if pairs is None:
        return "—"
    if not pairs:
        return "∅ (none)"
    return ", ".join(f"{p[0]}→{p[1]}" for p in pairs if isinstance(p, (list, tuple)) and len(p) >= 2)


def get_feasible_rank(objective_value: float | None, landscape: Mapping[str, Any] | None) -> tuple[int | None, int | None]:
    """Returns (rank, total_feasible) based on landscape feasible plans sorted by objective."""
    if objective_value is None or not landscape:
        return None, None
    feasible_list = landscape.get("feasible", [])
    if not feasible_list:
        return None, None
    rank = 1 + sum(1 for item in feasible_list if (as_float(item.get("obj")) or float("inf")) < objective_value - 1e-9)
    return rank, len(feasible_list)


def generate_why_it_changed(cur: Mapping[str, Any] | None, ref: Mapping[str, Any] | None, scenario: Mapping[str, Any]) -> str:
    """
    Constructs a concise narrative explaining what changed between the current run and a reference run.
    Derived dynamically from the two result dictionaries without hardcoding.
    """
    if not cur or not ref or not cur.get("feasible") or not ref.get("feasible"):
        return ""
    
    tt = scenario.get("travel_times", {})
    tau = scenario.get("unserved_time", 20)
    pw = scenario.get("priority_weights", {})
    
    cur_asg = {c: a for a, c in cur.get("assignments", [])}
    ref_asg = {c: a for a, c in ref.get("assignments", [])}
    
    parts = []
    for c in scenario.get("calls", []):
        u_cur = cur_asg.get(c)
        u_ref = ref_asg.get(c)
        if u_cur != u_ref:
            t_cur = tt.get((u_cur, c), tau) if u_cur else tau
            t_ref = tt.get((u_ref, c), tau) if u_ref else tau
            dt = t_cur - t_ref
            w = pw.get(c, 1)
            dw = dt * w
            sg_dt = f"+{dt:g}" if dt > 0 else f"{dt:g}"
            sg_dw = f"+{dw:g}" if dw > 0 else f"{dw:g}"
            cur_desc = f"is served by {u_cur}" if u_cur else "is left unserved"
            ref_desc = f"{u_ref}" if u_ref else "being left unserved"
            parts.append(f"{c} {cur_desc} instead of {ref_desc} ({sg_dt} min, {sg_dw} weighted)")
            
    cur_cov = as_float(cur.get("coverage_penalty")) or 0.0
    ref_cov = as_float(ref.get("coverage_penalty")) or 0.0
    dc = cur_cov - ref_cov

    cur_resp = as_float(cur.get("weighted_response_cost")) or 0.0
    ref_resp = as_float(ref.get("weighted_response_cost")) or 0.0
    dr = cur_resp - ref_resp

    cur_obj = as_float(cur.get("objective_value")) or 0.0
    ref_obj = as_float(ref.get("objective_value")) or 0.0
    dn = cur_obj - ref_obj
    sg_dn = f"+{dn:g}" if dn > 0 else f"{dn:g}"

    if not parts and abs(dn) < 1e-9:
        return f"Same assignment and the same dispatch cost ({cur_obj:g})."

    resp_phrase = ""
    if abs(dr) > 1e-9:
        if dr > 0:
            resp_phrase = f", weighted response cost rises from {ref_resp:g} to {cur_resp:g}"
        else:
            resp_phrase = f", weighted response cost falls from {ref_resp:g} to {cur_resp:g}"

    cov_phrase = ""
    if abs(dc) > 1e-9:
        if dc < 0:
            cov_phrase = f", and the coverage penalty falls from {ref_cov:g} to {cur_cov:g} because a backup unit stays put"
        else:
            cov_phrase = f", and the coverage penalty rises from {ref_cov:g} to {cur_cov:g} because both backup units leave"
    else:
        cov_phrase = f", and coverage penalty stays at {cur_cov:g}"

    changes_str = "; ".join(parts) if parts else "No route changes"
    return f"{changes_str}{resp_phrase}{cov_phrase}. Dispatch cost {ref_obj:g} → {cur_obj:g} ({sg_dn})."


def build_map_svg(scenario: Mapping[str, Any], result: Mapping[str, Any] | None = None,
                  width: int = 680, height: int = 410, animate: bool = True) -> str:
    """
    Renders the exact topological response zone SVG.
    Euclidean distance between nodes equals travel times in minutes.
    When result is None or infeasible, renders candidate routes only (no assignments or dispatched units).
    When result is feasible, renders assigned routes in bold accent and candidate routes dimmed,
    with unit dispatch targets and backup-pair status.
    Includes animated moving vehicle traces and pulsing call nodes when animate is True.
    """
    positions = scenario.get("positions") or scenario.get("layout") or {}
    if not positions:
        return '<svg viewBox="0 0 680 410"><text x="50%" y="50%" text-anchor="middle" fill="#94a5a5">No layout positions</text></svg>'
        
    ambulances = scenario.get("ambulances", [])
    calls = scenario.get("calls", [])
    travel_times = scenario.get("travel_times", {})
    coverage = scenario.get("coverage", {})
    priority_weights = scenario.get("priority_weights", {})
    
    is_feas = result is not None and bool(result.get("feasible"))
    assignments = result.get("assignments", []) if is_feas else []
    by_amb = {a: c for a, c in assignments}
    by_call = {c: a for a, c in assignments}
    
    # Check if this assignment preserved regional backup or incurred a coverage penalty
    cov_penalty = float(result.get("coverage_penalty") or 0.0) if is_feas else 0.0
    has_cov_penalty = cov_penalty > 0.0
    
    pad = 70
    x_coords = [p[0] for p in positions.values()]
    y_coords = [p[1] for p in positions.values()]
    x0, x1 = min(x_coords), max(x_coords)
    y0, y1 = min(y_coords), max(y_coords)
    dx = x1 - x0 if (x1 - x0) > 1e-6 else 1.0
    dy = y1 - y0 if (y1 - y0) > 1e-6 else 1.0
    k = min((width - 2 * pad) / dx, (height - 2 * pad) / dy)
    ox = (width - k * dx) / 2
    oy = (height - k * dy) / 2
    
    def X(n: str) -> float:
        return ox + (positions[n][0] - x0) * k
        
    def Y(n: str) -> float:
        return oy + (positions[n][1] - y0) * k
        
    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Simulated response zone topology">'
    ]
    
    # Grid lines
    g_step = 2 * k
    if g_step > 4:
        gx = ox % g_step
        while gx < width:
            svg_parts.append(f'<line class="grid" x1="{gx:.1f}" y1="0" x2="{gx:.1f}" y2="{height}"/>')
            gx += g_step
        gy = oy % g_step
        while gy < height:
            svg_parts.append(f'<line class="grid" x1="0" y1="{gy:.1f}" x2="{width}" y2="{gy:.1f}"/>')
            gy += g_step
            
    # Backup pair capsule
    cov_pairs = coverage.get("pairs", [])
    for p in cov_pairs:
        a, b, pen = p[0], p[1], p[2]
        if a in positions and b in positions:
            hit = is_feas and (a in by_amb) and (b in by_amb)
            kept = is_feas and not hit
            cap_cls = "cap hit" if hit else ("cap kept" if kept else "cap")
            svg_parts.append(f'<line class="{cap_cls}" x1="{X(a):.1f}" y1="{Y(a):.1f}" x2="{X(b):.1f}" y2="{Y(b):.1f}"/>')
            mid_x = (X(a) + X(b)) / 2
            min_y = min(Y(a), Y(b)) - 38
            lbl_cls = "capt hit" if hit else ("capt kept" if kept else "capt")
            lbl_text = f"backup broken · +{pen:g} penalty" if hit else ("backup preserved · penalty 0" if kept else f"backup pair · +{pen:g} if both leave")
            svg_parts.append(f'<text class="{lbl_cls}" text-anchor="middle" x="{mid_x:.1f}" y="{min_y:.1f}">{lbl_text}</text>')
            
    # Candidate and Assigned Routes
    active_routes = []
    for (a, c), t in travel_times.items():
        if a in positions and c in positions:
            on = is_feas and by_amb.get(a) == c
            if on:
                active_routes.append((a, c, t))
                status_attr = ' data-status="hit"' if has_cov_penalty else ' data-status="kept"'
                cl = " on"
            else:
                status_attr = ""
                cl = " off" if is_feas else ""
            svg_parts.append(f'<line class="ln{cl}"{status_attr} x1="{X(a):.1f}" y1="{Y(a):.1f}" x2="{X(c):.1f}" y2="{Y(c):.1f}"/>')
            lx = X(a) + (X(c) - X(a)) * 0.42
            ly = Y(a) + (Y(c) - Y(a)) * 0.42 + 4
            lbl_str = f"{t:g} min" if on else f"{t:g}"
            svg_parts.append(f'<text class="lt{cl}" text-anchor="middle" x="{lx:.1f}" y="{ly:.1f}">{lbl_str}</text>')
            
    # Animated traces and vehicles along active routes
    if is_feas and animate:
        for a, c, t in active_routes:
            veh_col = "var(--amber)" if has_cov_penalty else "var(--blue)"  # theme tokens; see ui_components._CSS
            # Route trace line
            svg_parts.append(
                f'<line class="ln-trace" x1="{X(a):.1f}" y1="{Y(a):.1f}" x2="{X(c):.1f}" y2="{Y(c):.1f}"/>'
            )
            # Moving ambulance marker
            svg_parts.append(
                f'<g class="veh-marker">'
                f'<circle r="4.5" style="fill:{veh_col};filter:drop-shadow(0 0 4px {veh_col})"/>'
                f'<animateMotion dur="2.6s" repeatCount="indefinite" path="M {X(a):.1f} {Y(a):.1f} L {X(c):.1f} {Y(c):.1f}"/>'
                f'</g>'
            )
            
    # Emergency Calls
    for c in calls:
        if c in positions:
            unserved = is_feas and (c not in by_call)
            c_cls = "c unserved" if unserved else "c"
            pw = priority_weights.get(c, 1)
            st_text = "unserved" if unserved else f"priority ×{pw}"
            
            # Pulsing ring for active emergency calls
            pulse_ring = f'<circle class="call-pulse" cx="{X(c):.1f}" cy="{Y(c):.1f}" r="16"/>' if animate else ""
            
            svg_parts.append(
                f'<g class="{c_cls}">'
                f'{pulse_ring}'
                f'<circle cx="{X(c):.1f}" cy="{Y(c):.1f}" r="16"/>'
                f'<text class="uid" x="{X(c):.1f}" y="{Y(c)+4.5:.1f}">{c}</text>'
                f'<text class="ust" x="{X(c):.1f}" y="{Y(c)+32:.1f}">{st_text}</text></g>'
            )
            
    # Ambulances
    for a in ambulances:
        if a in positions:
            go_call = by_amb.get(a) if is_feas else None
            u_cls = "u go" if go_call else "u"
            st_text = f"to {go_call}" if go_call else ("held" if is_feas else "available")
            svg_parts.append(
                f'<g class="{u_cls}"><rect x="{X(a)-18:.1f}" y="{Y(a)-13:.1f}" width="36" height="26" rx="4"/>'
                f'<text class="uid" x="{X(a):.1f}" y="{Y(a)+4.5:.1f}">{a}</text>'
                f'<text class="ust" x="{X(a):.1f}" y="{Y(a)-20:.1f}">{st_text}</text></g>'
            )
            
    # Scale bar
    scale_len = 5 * k
    svg_parts.append(
        f'<line x1="16" y1="{height-16}" x2="{16+scale_len:.1f}" y2="{height-16}" stroke="var(--ink, #e7eeeb)" stroke-width="2"/>'
        f'<text class="ax" x="{22+scale_len:.1f}" y="{height-12}">5 min scale</text>'
        '</svg>'
    )
    return "".join(svg_parts)


def build_trace_svg(exp: Mapping[str, Any], width: int = 520, height: int = 210) -> str:
    """Renders optimizer trace SVG of expected QUBO energy across function evaluations."""
    h = exp.get("energy_history") or exp.get("history", {}).get("values") or []
    if not h:
        return ""
    ground_e = exp.get("ground_energy")
    if ground_e is None:
        ground_e = exp.get("history", {}).get("reference", {}).get("value")
    if ground_e is None:
        ground_e = min(h)
    l, rr, t, b = 46, 14, 14, 26
    lo = min([ground_e] + list(h))
    hi = max(h)
    rng = (hi - lo) if abs(hi - lo) > 1e-9 else 1.0
    
    def x_fn(i: int) -> float:
        return l + (width - l - rr) * (i / (len(h) - 1) if len(h) > 1 else 0)
        
    def y_fn(v: float) -> float:
        return t + (height - t - b) * (1 - (v - lo) / rng)
        
    pts = " ".join(f"{x_fn(i):.1f},{y_fn(v):.1f}" for i, v in enumerate(h))
    poly_pts = f"{l},{y_fn(lo):.1f} {pts} {x_fn(len(h)-1):.1f},{y_fn(lo):.1f}"
    
    svg = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Expected energy by optimizer evaluation">',
        f'<line class="grid" x1="{l}" y1="{y_fn(hi):.1f}" x2="{width-rr}" y2="{y_fn(hi):.1f}"/>',
        f'<line class="gl" x1="{l}" y1="{y_fn(ground_e):.1f}" x2="{width-rr}" y2="{y_fn(ground_e):.1f}"/>',
        f'<polygon class="trf" points="{poly_pts}"/>',
        f'<polyline class="tr" points="{pts}"/>',
        f'<circle cx="{x_fn(len(h)-1):.1f}" cy="{y_fn(h[-1]):.1f}" r="4" fill="var(--q, #b9a6ff)"/>',
        f'<text class="ax" x="{l-6}" y="{y_fn(hi)+4:.1f}" text-anchor="end">{hi:.1f}</text>',
        f'<text class="ax" x="{l-6}" y="{y_fn(ground_e)+4:.1f}" text-anchor="end">{ground_e:.1f}</text>',
        f'<text class="ax" x="{x_fn(len(h)-1)-8:.1f}" y="{y_fn(h[-1])-9:.1f}" text-anchor="end">final {h[-1]:.2f}</text>',
        f'<text class="ax" x="{l}" y="{height-8}">evaluation 1</text>',
        f'<text class="ax" x="{width-rr}" y="{height-8}" text-anchor="end">{len(h)}</text>',
        f'<text class="ax" x="{width-rr}" y="{y_fn(ground_e)-6:.1f}" text-anchor="end" style="fill:var(--ok, #5fd39a)">exact ground energy</text>',
        '</svg>'
    ]
    return "".join(svg)



# --------------------------------------------------------------------------- #
# Plain-language labels
# --------------------------------------------------------------------------- #

_METHOD_DISPLAY = {
    "Greedy (Priority Nearest)": "Nearest available",
    "Exact Classical Solver": "Exact optimisation",
}


def display_method(method: Any) -> str:
    """Name a method the way the console's method picker does.

    The backend keeps its own method strings (tests and exports rely on them);
    this only changes what a reader sees. QAOA labels already carry their settings.
    """
    name = str(method)
    return _METHOD_DISPLAY.get(name, name)


def landscape_optimum(landscape: Mapping[str, Any] | None) -> float | None:
    """Lowest dispatch cost among all enumerated feasible plans, or None if unknown."""
    rows = (landscape or {}).get("feasible") or []
    vals = [as_float(r.get("obj")) for r in rows]
    vals = [v for v in vals if v is not None]
    return min(vals) if vals else None


def workflow_steps(n_runs: int, has_comparison: bool) -> list[tuple[str, str]]:
    """The console's four steps with a state each: 'done', 'now' or 'todo'."""
    labels = ["Calls arrive", "Choose a method", "Run it", "Compare & see why"]
    if n_runs == 0:
        states = ["done", "now", "todo", "todo"]
    elif not has_comparison:
        states = ["done", "done", "done", "now"]
    else:
        states = ["done", "done", "done", "done"]
    return list(zip(labels, states))


def status_sentence(result: Mapping[str, Any] | None, scenario: Mapping[str, Any]) -> tuple[str, str]:
    """One plain-English sentence about what the shown result did, and a tone for its colour.

    Built only from the result and scenario passed in; returns (tone, html) with tone in
    'idle', 'ok', 'warn' or 'quantum'.
    """
    calls = list(scenario.get("calls", []))
    units = list(scenario.get("ambulances", []))
    if not result:
        return "idle", (f'<span class="k">No decision yet.</span> {len(calls)} calls are waiting and {len(units)} ambulances are free. '
                        'Choose a method on the right and press <b>Run</b>, or compare two methods in one click.')
    name = display_method(result.get("method"))
    exp = result.get("experiment") or {}
    if not result.get("feasible"):
        shots = exp.get("shots")
        return "warn", (f'<span class="k">{name} found no valid plan</span>'
                        f'{f" in {shots:,} shots" if shots else ""}. Nothing was dispatched.')
    asg = list(result.get("assignments") or [])
    sent = ", ".join(f"{a} → {c}" for a, c in asg) or "no ambulance"
    sent_units = {a for a, _ in asg}
    held = [u for u in units if u not in sent_units]
    pairs = (scenario.get("coverage") or {}).get("pairs", [])
    broken = [f"{p[0]}+{p[1]}" for p in pairs if p[0] in sent_units and p[1] in sent_units]
    cost = fmt_num(result.get("objective_value"), 0)
    unserved = list(result.get("unserved_calls") or [])
    parts = [f'<span class="k">{name}</span> sent {sent}']
    if held:
        parts.append(f"kept {', '.join(held)} in reserve")
    if broken:
        parts.append(f"both backup partners {', '.join(broken)} left, so their area lost its backup")
    elif pairs:
        parts.append("every backup pair still has a unit at home")
    if unserved:
        parts.append(f"{', '.join(unserved)} went unserved")
    text = "; ".join(parts) + f". Total cost <b>{cost}</b>."
    if provenance(result)["is_qaoa"]:
        hits, shots = exp.get("best_sample_hits"), exp.get("shots")
        if hits is not None and shots:
            text += f" QAOA saw this plan in {hits} of {shots:,} shots."
        return "quantum", text
    return ("warn" if broken else "ok"), text
