"""Streamlit/Plotly smoke tests for app/ui_components.py.

Skipped automatically unless streamlit and plotly are installed. Fixtures are
SYNTHETIC PRESENTATION FIXTURES - the numbers are arbitrary and are not QAOA
or solver output. These tests have NOT been executed in the authoring
environment (the packages were not installed there).
"""
import os
import sys

import pytest

pytest.importorskip("plotly")
pytest.importorskip("streamlit")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import ui_components as ui  # noqa: E402

FIXTURE_EXP = {  # SYNTHETIC - not real experiment output
    "kind": "qaoa_sampled", "p": 1, "seed": 0, "shots": 100, "success": False, "message": "fixture message",
    "final_qubo_energy": -1.0, "initial_qubo_energy": 2.0, "sampled_feas_rate": 0.5, "sv_feas_rate": 0.6,
    "optimum_hits": 10, "sampled_opt_prob": 0.1, "sv_opt_prob": 0.12, "final_params": [0.1, 0.2],
    "counts": {"000001": 60, "000011": 40},
}
RESULT = {"scenario_id": "S-FIXTURE", "method": "QAOA fixture", "assignments": [("A1", "C2")], "unserved_calls": ["C3"],
          "weighted_response_cost": 1.0, "coverage_penalty": 0.0, "objective_value": 1.0, "feasible": True,
          "runtime_seconds": 0.5, "experiment": FIXTURE_EXP}
SCENARIO = {"scenario_id": "S-FIXTURE", "ambulances": ["A1", "A2", "A3"], "calls": ["C2", "C3"],
            "variables": [("A1", "C2"), ("A1", "C3"), ("A2", "C2"), ("A2", "C3"), ("A3", "C2"), ("A3", "C3")],
            "travel_times": {("A1", "C2"): 4}}


def test_figure_builders_do_not_raise_and_handle_absent_data():
    assert ui.build_assignment_schematic(RESULT, SCENARIO) is not None
    assert ui.build_assignment_schematic({"assignments": [], "unserved_calls": []}, {}) is None
    assert ui.build_exact_vs_sampled_chart({}) is None and ui.build_endpoints_chart({}) is None
    assert ui.build_outcome_chart({"optimum": None, "other_feasible": 0.4, "infeasible": 0.6}) is not None


def test_quantum_lab_renders_with_failed_optimizer_and_no_history():
    from streamlit.testing.v1 import AppTest

    def script():
        import sys
        sys.path.insert(0, "app")
        import ui_components as u
        from test_ui_components_smoke import RESULT, SCENARIO  # noqa
        u.render_quantum_lab([RESULT], SCENARIO)

    at = AppTest.from_function(script, default_timeout=30).run()
    assert not at.exception


# --- All five views, populated / empty / malformed (synthetic fixtures) -------------

def _classical(method="Classical fixture", feasible=True, obj=9.0):
    return {"scenario_id": "S-FIXTURE", "method": method, "assignments": [("A2", "C3")], "unserved_calls": ["C2"],
            "weighted_response_cost": 7.0, "coverage_penalty": 2.0, "objective_value": obj, "feasible": feasible,
            "runtime_seconds": 0.01, "experiment": {}}


_VIEW_CASES = {
    "populated": ([_classical(), RESULT, _classical("Bad", False, float("inf"))], [{"method": "QAOA fixture", "message": "x"}]),
    "empty": ([], []),
    "malformed": ([{"method": "m"}, "junk", None, {"experiment": 5}], []),
}


@pytest.mark.parametrize("case", list(_VIEW_CASES))
def test_every_view_renders_without_exception(case):
    from streamlit.testing.v1 import AppTest

    def script():
        import sys
        sys.path.insert(0, "app")
        sys.path.insert(0, "tests")
        import ui_components as u
        from test_ui_components_smoke import SCENARIO, _VIEW_CASES
        import streamlit as st
        results, failures = _VIEW_CASES[st.query_params.get("case", "populated")]
        scen = None if st.query_params.get("case") == "empty" else SCENARIO
        u.apply_theme()
        for v in u.VIEWS:
            u.render_view_header(v, "S-FIXTURE")
        u.render_overview(scen, results, failures)
        u.render_scenario_builder(scen, ["Classical fixture", "QAOA fixture"], [{"key": "lam", "label": "λ", "type": "float", "default": 10, "min": 0}],
                                  editable=("availability", "priorities"))
        u.render_dispatch_simulator(results, scen)
        u.render_quantum_lab(results, scen)
        u.render_benchmark_analytics(results, failures)

    at = AppTest.from_function(script, default_timeout=60)
    at.query_params["case"] = case
    at.run()
    assert not at.exception, [e.value for e in at.exception]
