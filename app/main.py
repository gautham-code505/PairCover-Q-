"""
PairCover-Q — Streamlit Web Application (Q-Rescue).

Emergency-operations analytics console for coverage-aware ambulance dispatch
using QUBO and QAOA, benchmarked against exact classical and greedy algorithms.
"""

from __future__ import annotations

import os
import sys
from typing import Any

# Ensure project root and src/ are on sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
_SRC_DIR = os.path.join(_ROOT_DIR, "src")
for _p in (_ROOT_DIR, _SRC_DIR, _CURRENT_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import ui_components as ui
import custom_emergency as ce
from custom_view import render_custom_emergency

from app.result_adapter import (
    get_scenario,
    run_greedy,
    run_exact,
    run_qaoa,
    run_method
)

# --------------------------------------------------------------------------- #
# Page Setup & Theme
# --------------------------------------------------------------------------- #

st.set_page_config(
    page_title="PairCover-Q | Q-Rescue Console",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

ui.apply_theme()

ss = st.session_state
ss.setdefault("pq_results", [])
ss.setdefault("pq_failures", [])
ss.setdefault("scenario_id", "scenario_2")

# --------------------------------------------------------------------------- #
# Sidebar: Branding, Scenario Selection & Navigation
# --------------------------------------------------------------------------- #

st.sidebar.markdown(
    f"<div style='margin-bottom:0.4rem;'>"
    f"<span style='font-size:1.25rem;font-weight:700;color:var(--accent);'>🚑 PairCover-Q</span>"
    f"<br><span style='font-size:0.75rem;color:var(--muted);'>Quantum Emergency Resource Allocation</span>"
    f"</div>"
    f"<div class='sidebar-status-chip'>"
    f"<span class='sidebar-status-dot'></span>"
    f"<span>Qiskit Aer · Simulator Active</span>"
    f"</div>",
    unsafe_allow_html=True
)

scenario_options = {
    "Scenario 2 (PairCover-Q, 6 Qubits)": "scenario_2",
    "Scenario 1 (Math Validation, 5 Qubits)": "scenario_1"
}

header_scen_map = {
    "Coverage demo · 6 qubits (Scenario 2)": "scenario_2",
    "Validation case · 5 qubits (Scenario 1)": "scenario_1"
}

# Sync callbacks
def _on_sidebar_scen_change() -> None:
    chosen = st.session_state["sidebar_scen_pick"]
    sid = scenario_options[chosen]
    st.session_state["scenario_id"] = sid
    st.session_state["hdr_scen_sel"] = (
        "Coverage demo · 6 qubits (Scenario 2)"
        if sid == "scenario_2"
        else "Validation case · 5 qubits (Scenario 1)"
    )

def _on_header_scen_change() -> None:
    chosen = st.session_state["hdr_scen_sel"]
    sid = header_scen_map[chosen]
    st.session_state["scenario_id"] = sid
    st.session_state["sidebar_scen_pick"] = (
        "Scenario 2 (PairCover-Q, 6 Qubits)"
        if sid == "scenario_2"
        else "Scenario 1 (Math Validation, 5 Qubits)"
    )

default_side = (
    "Scenario 2 (PairCover-Q, 6 Qubits)"
    if ss["scenario_id"] == "scenario_2"
    else "Scenario 1 (Math Validation, 5 Qubits)"
)
default_hdr = (
    "Coverage demo · 6 qubits (Scenario 2)"
    if ss["scenario_id"] == "scenario_2"
    else "Validation case · 5 qubits (Scenario 1)"
)

if "sidebar_scen_pick" not in ss:
    ss["sidebar_scen_pick"] = default_side
if "hdr_scen_sel" not in ss:
    ss["hdr_scen_sel"] = default_hdr

# Light / dark switch. Streamlit applies a theme only on page load, so each option is a
# link that reloads the app with Streamlit's own theme option (this starts a new session).
_mode = ui.theme_mode()
st.sidebar.markdown("<div class='sidebar-section-label'>APPEARANCE</div>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div class='theme-switch' role='group' aria-label='Colour theme'>"
    + "".join(
        f"<a href='{href}' target='_self' class='{'on' if _mode == key else ''}' aria-pressed='{str(_mode == key).lower()}'>{label}</a>"
        for key, label, href in (("light", "☀ Light", "?embed_options=light_theme"),
                                 ("dark", "🌙 Dark", "?embed_options=dark_theme"))
    )
    + "</div>",
    unsafe_allow_html=True,
)
st.sidebar.caption("Switching reloads the app and clears this session's runs. Without a choice, the app follows your device setting.")

st.sidebar.markdown("<div class='sidebar-section-label'>ACTIVE SCENARIO</div>", unsafe_allow_html=True)
selected_label = st.sidebar.selectbox(
    "Active Scenario",
    options=list(scenario_options.keys()),
    key="sidebar_scen_pick",
    on_change=_on_sidebar_scen_change,
    label_visibility="collapsed",
    help="Switch between the 6-qubit residual coverage demonstration and the 5-qubit mathematical validation scenario."
)
ss["scenario_id"] = scenario_options[st.session_state["sidebar_scen_pick"]]

st.sidebar.markdown("<div class='sidebar-section-label'>CONSOLE NAVIGATION</div>", unsafe_allow_html=True)
def _on_main_view_change() -> None:
    # Choosing a main screen leaves any diagnostic tool; otherwise the tool kept
    # covering the page and the main menu appeared to do nothing.
    st.session_state["adv_tool_pick"] = "(None - Main Console)"

view = st.sidebar.radio("Console View", ui.PRIMARY_VIEWS, index=0, key="main_view", on_change=_on_main_view_change)

with st.sidebar.expander("🛠️ Advanced Diagnostic Tools", expanded=False):
    st.caption("Inspect individual secondary modules and standalone analytical tools.")
    adv_tool = st.radio(
        "Diagnostic Tool",
        ["(None - Main Console)", "Overview", "Scenario Builder", "Dispatch Simulator", "Benchmark Analytics"],
        index=0,
        key="adv_tool_pick"
    )

st.sidebar.markdown("---")
st.sidebar.caption(
    "🔬 **Q-HACK INDIA 2026**\n\n"
    "Proof-of-concept modeling for quadratic fleet coverage interactions. "
    "All scenarios use synthetic data and noiseless classical simulation."
)

if st.sidebar.button("Clear Run History", help="Clear all stored results and failures in this session"):
    ss["pq_results"] = []
    ss["pq_failures"] = []
    ss.pop("current_run_key", None)
    st.sidebar.success("Cleared session run history.")

# --------------------------------------------------------------------------- #
# Top Header Bar: Branding, Header Scenario Selector & Simulation Chip
# --------------------------------------------------------------------------- #

scenario = get_scenario(ss["scenario_id"])

h_c1, h_c2, h_c3 = st.columns([1.6, 1.4, 0.6], vertical_alignment="center")
with h_c1:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:2px 0;">'
        f'<span style="font-size:22px;font-weight:700;color:var(--accent);line-height:1.2;">🚑 PairCover-Q</span>'
        f'<span style="font-size:13px;color:var(--muted);">Emergency dispatch & coverage</span>'
        f'</div>',
        unsafe_allow_html=True
    )
with h_c2:
    if view == "🆘 Create Your Emergency":
        st.markdown('<div class="pc-caption" style="margin:0;">Your emergency · synthetic city</div>', unsafe_allow_html=True)
    else:
        st.selectbox(
            "Header Scenario",
            options=list(header_scen_map.keys()),
            key="hdr_scen_sel",
            on_change=_on_header_scen_change,
            label_visibility="collapsed"
        )
with h_c3:
    st.markdown(
        f'<div style="text-align:right;display:flex;align-items:center;justify-content:flex-end;padding:2px 0;">'
        f'<span class="pc-badge synthetic" style="margin:0;">SIMULATION</span>'
        f'</div>',
        unsafe_allow_html=True
    )
st.markdown('<div style="border-bottom:1px solid var(--divider);margin-top:4px;margin-bottom:14px;"></div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Execution Helpers
# --------------------------------------------------------------------------- #

def backend_run(method_name: str, scen: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Backend dispatch runner adapting UI inputs to verified solver execution."""
    sid = scen["scenario_id"]
    if str(sid).startswith(ce.SCENARIO_ID):
        return ce.run_custom(method_name, scen, params)
    m_lower = method_name.lower()
    if "nearest" in m_lower or "greedy" in m_lower:
        return run_greedy(sid)
    elif "exact" in m_lower or "classical" in m_lower:
        return run_exact(sid)
    elif "qaoa" in m_lower or "quantum" in m_lower:
        p_val = int(params.get("p", 1))
        seed_val = int(params.get("seed", 10))
        maxiter_val = int(params.get("maxiter", 100))
        shots_val = int(params.get("shots", 1000))
        return run_qaoa(sid, p=p_val, seed=seed_val, maxiter=maxiter_val, shots=shots_val)
    else:
        return run_method(method_name, sid, **params)

def on_dispatch_run(method_name: str, params: dict[str, Any]) -> None:
    """Dispatches a method run from the Dispatch Console with loading state and history retention."""
    scenario = ss.get("_active_scenario") or globals()["scenario"]
    ok, res = ui.run_with_loading(
        f"Executing {method_name} on {scenario['name']}",
        backend_run,
        method_name,
        scenario,
        params,
        failures_state=ss,
        method=method_name,
        scenario_id=scenario["scenario_id"]
    )
    if ok and res:
        ui.retain_result(ss, res)
        ss["current_run_key"] = res.get("experiment", {}).get("run_id") or res["method"]
        # The console above this button was already drawn from the previous run.
        # Drop the run picker's remembered choice (it would override the new run)
        # and redraw so the zone, cards and ledger show the run that just finished.
        ss.pop("dc_select_run", None)
        ss.pop("ce_select_run", None)
        ss.pop("ql_run", None)
        st.rerun()

def on_dispatch_compare(method_names: list[str], params: dict[str, Any] | None = None) -> None:
    """Run several methods one after another (guided comparison, Scenario Builder) and show the last."""
    scenario = ss.get("_active_scenario") or globals()["scenario"]
    last_key = None
    for m in method_names:
        ok, res = ui.run_with_loading(
            f"Executing {m} on {scenario['name']}",
            backend_run, m, scenario, params or {},
            failures_state=ss, method=m, scenario_id=scenario["scenario_id"]
        )
        if ok and res:
            ui.retain_result(ss, res)
            last_key = res.get("experiment", {}).get("run_id") or res["method"]
    if last_key:
        ss["current_run_key"] = last_key
        ss.pop("dc_select_run", None)
        ss.pop("ce_select_run", None)
        ss.pop("ql_run", None)
        st.rerun()

# --------------------------------------------------------------------------- #
# View Router (4 Primary Areas + Collapsible Advanced Diagnostic Tools)
# --------------------------------------------------------------------------- #

effective_view = adv_tool if adv_tool != "(None - Main Console)" else view

# Reset scroll position when switching primary views
if ss.get("_last_view") != effective_view:
    ss["_last_view"] = effective_view
    import streamlit.components.v1 as _components
    _components.html(
        "<script>window.parent.document.querySelector('section.main')?.scrollTo({top: 0, behavior: 'instant'});</script>",
        height=0
    )

ss["_active_scenario"] = scenario

if effective_view == "🆘 Create Your Emergency":
    # The builder sets the active scenario to the user's situation before its console runs anything.
    def _set_active(scen: dict[str, Any]) -> None:
        ss["_active_scenario"] = scen

    render_custom_emergency(ss, ss["pq_results"], ss["pq_failures"], on_run=on_dispatch_run,
                            on_compare=on_dispatch_compare, set_active=_set_active)

elif effective_view in ("🚑 Dispatch Console", "Dispatch Console"):
    ui.render_dispatch_console(
        scenario=scenario,
        results=ss["pq_results"],
        current_key=ss.get("current_run_key"),
        on_run=on_dispatch_run,
        failures=ss["pq_failures"],
        on_compare=on_dispatch_compare
    )

elif effective_view in ("⚛️ Quantum Lab", "Quantum Lab"):
    ui.render_quantum_lab(
        results=ss["pq_results"],
        scenario=scenario,
        current_key=ss.get("current_run_key"),
        on_run=on_dispatch_run,
        failures=ss["pq_failures"]
    )

elif effective_view in ("📊 Results & Benchmarks", "Results and Benchmarks", "Results & Benchmarks"):
    ui.render_results_and_benchmarks(
        results=ss["pq_results"],
        scenario=scenario,
        failures=ss["pq_failures"]
    )

elif effective_view in ("📘 Method & Data", "Methodology", "Method & Data"):
    ui.render_methodology(
        scenario=scenario
    )

elif effective_view == "Overview":
    ui.render_overview(scenario, ss["pq_results"], ss["pq_failures"])

elif effective_view == "Scenario Builder":
    sel = ui.render_scenario_builder(scenario, ["Nearest available", "Exact optimisation", "QAOA"])
    # The form's Run button used to be ignored; run what was ticked.
    if sel and sel.get("run") and sel.get("methods"):
        on_dispatch_compare(list(sel["methods"]), sel.get("params") or {})

elif effective_view == "Dispatch Simulator":
    ui.render_dispatch_simulator(ss["pq_results"], scenario)

elif effective_view == "Benchmark Analytics":
    ui.render_benchmark_analytics(ss["pq_results"], ss["pq_failures"])

