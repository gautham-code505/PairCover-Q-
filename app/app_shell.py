"""
Shared pieces of the PairCover-Q app shell: session state, the method runners every page
uses, and the page header (title, scenario picker, theme switch, settings).

Pages live in app/app_pages/ and are registered with st.navigation in app/main.py.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

import custom_emergency as ce
import ui_components as ui
from app.result_adapter import get_scenario, run_exact, run_greedy, run_method, run_qaoa

SCENARIOS = {
    "scenario_2": "Coverage demo · 6 qubits",
    "scenario_1": "Validation case · 5 qubits",
}

# Page files, used for st.switch_page and as the navigation's source of truth.
PAGES = {
    "home": "app_pages/home.py",
    "console": "app_pages/console.py",
    "custom": "app_pages/your_emergency.py",
    "lab": "app_pages/quantum_lab.py",
    "results": "app_pages/results.py",
    "evidence": "app_pages/evidence.py",
    "method": "app_pages/method.py",
}


def init_state() -> None:
    ss = st.session_state
    ss.setdefault("pq_results", [])
    ss.setdefault("pq_failures", [])
    ss.setdefault("scenario_id", "scenario_2")


def current_scenario() -> dict[str, Any]:
    return get_scenario(st.session_state["scenario_id"])


def set_active(scen: dict[str, Any]) -> None:
    """The scenario that buttons on the current page act on."""
    st.session_state["_active_scenario"] = scen


def _active() -> dict[str, Any]:
    return st.session_state.get("_active_scenario") or current_scenario()


def backend_run(method_name: str, scen: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Run one method on one scenario with the verified backend."""
    sid = scen["scenario_id"]
    if str(sid).startswith(ce.SCENARIO_ID):
        return ce.run_custom(method_name, scen, params)
    m = method_name.lower()
    if "nearest" in m or "greedy" in m:
        return run_greedy(sid)
    if "exact" in m or "classical" in m:
        return run_exact(sid)
    if "qaoa" in m or "quantum" in m:
        return run_qaoa(sid, p=int(params.get("p", 1)), seed=int(params.get("seed", 10)),
                        maxiter=int(params.get("maxiter", 100)), shots=int(params.get("shots", 1000)))
    return run_method(method_name, sid, **params)


def run_methods(method_names: list[str], params: dict[str, Any] | None = None,
                scen: dict[str, Any] | None = None) -> str | None:
    """Run methods in order, keep every result, make the last one current. Returns its key."""
    ss = st.session_state
    scen = scen or _active()
    last_key = None
    for m in method_names:
        ok, res = ui.run_with_loading(f"Running {m}", backend_run, m, scen, params or {},
                                      failures_state=ss, method=m, scenario_id=scen["scenario_id"])
        if ok and res:
            ui.retain_result(ss, res)
            last_key = res.get("experiment", {}).get("run_id") or res["method"]
    if last_key:
        ss["current_run_key"] = last_key
        # Widgets that remember an older run would otherwise override the new one.
        for k in ("dc_select_run", "ce_select_run", "ql_run"):
            ss.pop(k, None)
    return last_key


def on_run(method_name: str, params: dict[str, Any]) -> None:
    if run_methods([method_name], params):
        st.rerun()


def on_compare(method_names: list[str], params: dict[str, Any] | None = None) -> None:
    if run_methods(list(method_names), params):
        st.rerun()


# --------------------------------------------------------------------------- #
# Page header
# --------------------------------------------------------------------------- #

def theme_switch_html() -> str:
    mode = ui.theme_mode()
    links = "".join(
        f"<a href='{href}' target='_self' class='{'on' if mode == key else ''}' "
        f"aria-pressed='{str(mode == key).lower()}' title='{tip}'>{label}</a>"
        for key, label, href, tip in (
            ("light", "☀", "?embed_options=light_theme", "Light theme (reloads the app)"),
            ("dark", "☾", "?embed_options=dark_theme", "Dark theme (reloads the app)"))
    )
    return f"<div class='theme-switch compact' role='group' aria-label='Colour theme'>{links}</div>"


def page_header(title: str, subtitle: str, *, scenario_picker: bool = False, eyebrow: str = "") -> None:
    """Title block on the left; scenario picker, theme switch and settings on the right."""
    ss = st.session_state
    left, mid, right = st.columns([2.2, 1.3, 0.75], vertical_alignment="center")
    with left:
        st.markdown(
            f'<div class="page-head">'
            f'{f"<div class=page-eyebrow>{eyebrow}</div>" if eyebrow else ""}'
            f'<h1 class="page-title">{title}</h1><p class="page-sub">{subtitle}</p></div>',
            unsafe_allow_html=True)
    with mid:
        if scenario_picker:
            keys = list(SCENARIOS)
            choice = st.selectbox("Scenario", keys, index=keys.index(ss["scenario_id"]),
                                  format_func=lambda k: SCENARIOS[k], key="scenario_pick",
                                  label_visibility="collapsed",
                                  help="Coverage demo: the 6-qubit example where nearest-available breaks a backup pair. "
                                       "Validation case: the 5-qubit hand-checked example.")
            if choice != ss["scenario_id"]:
                ss["scenario_id"] = choice
                st.rerun()
    with right:
        c1, c2 = st.columns([1.2, 1], vertical_alignment="center")
        c1.markdown(theme_switch_html(), unsafe_allow_html=True)
        with c2.popover("⚙", help="Settings"):
            st.markdown("**Session**")
            st.caption(f"{len(ss['pq_results'])} runs kept in this browser session.")
            if st.button("Clear run history", key="clear_history", use_container_width=True):
                ss["pq_results"], ss["pq_failures"] = [], []
                ss.pop("current_run_key", None)
                st.rerun()
            st.markdown("**About this app**")
            st.caption("Synthetic data, noiseless quantum simulation, no quantum advantage claimed. "
                       "Theme switching reloads the app.")
