"""
Tests for PairCover-Q Application Adapter & UI Integration.
Verifies result schema conformity, metric separation, scenario switching,
and honest error/infeasibility handling.
"""

import pytest
from app.result_adapter import (
    get_scenario,
    run_greedy,
    run_exact,
    run_qaoa,
    run_method,
    calculate_scenario1_raw_metrics,
    calculate_scenario2_raw_metrics,
    get_optimal_measurement_key
)
from app.ui_helpers import validate_result, normalize_assignments

def test_get_scenario_metadata():
    """Verify both scenarios provide complete metadata matching the UI specification."""
    s1 = get_scenario("scenario_1")
    assert s1["scenario_id"] == "scenario_1"
    assert len(s1["ambulances"]) == 2
    assert len(s1["calls"]) == 3
    assert len(s1["variables"]) == 5
    assert s1["qubo_offset"] == 120
    assert s1["landscape"]["total_states"] == 32
    assert s1["landscape"]["feasible_count"] == 10
    assert s1["landscape"]["feasibility_rate"] == 10 / 32
    
    s2 = get_scenario("scenario_2")
    assert s2["scenario_id"] == "scenario_2"
    assert len(s2["ambulances"]) == 3
    assert len(s2["calls"]) == 2
    assert len(s2["variables"]) == 6
    assert s2["qubo_offset"] == 60
    assert s2["landscape"]["total_states"] == 64
    assert s2["landscape"]["feasible_count"] == 13
    assert s2["landscape"]["feasibility_rate"] == 13 / 64

def test_scenario_layout_geometry_matches_travel_times():
    """Verify that layout positions have Euclidean distance equal to travel times."""
    import math
    for sid in ("scenario_1", "scenario_2"):
        scen = get_scenario(sid)
        pos = scen["positions"]
        tt = scen["travel_times"]
        for (a, c), expected_time in tt.items():
            xa, ya = pos[a]
            xc, yc = pos[c]
            dist = math.hypot(xa - xc, ya - yc)
            assert abs(dist - expected_time) < 0.02, (
                f"In {sid}, distance({a}, {c}) is {dist:.4f}, expected travel time {expected_time}"
            )

def test_greedy_dispatch_scenario1():
    """Verify Greedy on Scenario 1 yields objective 62 matching ground truth."""
    res = run_greedy("scenario_1")
    assert validate_result(res) == []
    assert res["feasible"] is True
    assert res["objective_value"] == 62.0
    assert res["weighted_response_cost"] is not None
    assert res["coverage_penalty"] is not None
    assert res["objective_value"] == res["weighted_response_cost"] + res["coverage_penalty"]
    assert ('A1', 'C1') in res["assignments"]
    assert ('A2', 'C2') in res["assignments"]
    assert 'C3' in res["unserved_calls"]

def test_greedy_dispatch_scenario2():
    """Verify Greedy on Scenario 2 yields objective 22 (12 response + 10 coverage penalty)."""
    res = run_greedy("scenario_2")
    assert validate_result(res) == []
    assert res["feasible"] is True
    assert res["weighted_response_cost"] == 12.0
    assert res["coverage_penalty"] == 10.0
    assert res["objective_value"] == 22.0
    assert ('A1', 'C2') in res["assignments"]
    assert ('A2', 'C3') in res["assignments"]

def test_exact_solver_scenario1():
    """Verify Exact Solver on Scenario 1 yields objective 62."""
    res = run_exact("scenario_1")
    assert validate_result(res) == []
    assert res["feasible"] is True
    assert res["objective_value"] == 62.0
    assert ('A1', 'C1') in res["assignments"]
    assert ('A2', 'C2') in res["assignments"]

def test_exact_solver_scenario2():
    """Verify Exact Solver on Scenario 2 yields objective 13 (leaves A2 idle)."""
    res = run_exact("scenario_2")
    assert validate_result(res) == []
    assert res["feasible"] is True
    assert res["weighted_response_cost"] == 13.0
    assert res["coverage_penalty"] == 0.0
    assert res["objective_value"] == 13.0
    assert ('A1', 'C2') in res["assignments"]
    assert ('A3', 'C3') in res["assignments"]
    # Ambulance A2 must remain idle
    assigned_ambs = [a for a, c in res["assignments"]]
    assert 'A2' not in assigned_ambs

def test_qaoa_execution_and_schema():
    """Verify QAOA execution adheres to result schema and preserves separate metrics."""
    res = run_qaoa("scenario_2", p=1, seed=10, maxiter=20, shots=100)
    assert validate_result(res) == []
    assert res["scenario_id"] == "scenario_2"
    assert "QAOA" in res["method"]
    assert isinstance(res["feasible"], bool)
    assert res["runtime_seconds"] > 0
    
    exp = res["experiment"]
    assert "depth_p" in exp
    assert "seed" in exp
    assert "feasibility_rate" in exp
    assert "exact_optimum_sample_prob" in exp
    assert "counts" in exp
    assert "energy_history" in exp
    assert "feasible_bitstrings" in exp
    assert "penalized_surrogate_objective" in exp
    
    if res["feasible"]:
        assert res["objective_value"] is not None
        assert res["weighted_response_cost"] is not None
        assert res["coverage_penalty"] is not None
        assert abs(res["objective_value"] - (res["weighted_response_cost"] + res["coverage_penalty"])) < 1e-9
    else:
        # If infeasible, objective_value must NOT be labeled as raw objective
        assert res["objective_value"] is None

def test_infeasible_metrics_handling():
    """Verify that infeasible bitstrings return None for physical metrics and are not fabricated."""
    # Infeasible state with duplicate ambulance: x = [1, 1, 0, 0, 0, 0] (A1-C2 and A1-C3)
    resp, cov, obj, feas = calculate_scenario2_raw_metrics([1, 1, 0, 0, 0, 0])
    assert feas is False
    assert resp is None
    assert cov is None
    assert obj is None

def test_run_method_dispatcher():
    """Verify the unified run_method dispatcher routes correctly."""
    g = run_method("greedy", "scenario_2")
    assert g["method"] == "Greedy (Priority Nearest)"
    assert g["objective_value"] == 22.0
    
    e = run_method("exact", "scenario_2")
    assert e["method"] == "Exact Classical Solver"
    assert e["objective_value"] == 13.0

def test_no_silent_quantum_substitution():
    """Verify QAOA output retains QAOA metadata and does not pretend to be the exact classical solver."""
    q_res = run_qaoa("scenario_2", p=1, seed=42, maxiter=10, shots=100)
    assert "QAOA" in q_res["method"]
    assert q_res["method"] != "Exact Classical Solver"
    assert "depth_p" in q_res["experiment"]
    assert "algorithm" not in q_res["experiment"] or "exhaustive" not in str(q_res["experiment"]["algorithm"])

def test_streamlit_main_app_loads():
    """Verify that app/main.py compiles and runs in Streamlit AppTest without errors."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    app_path = Path(__file__).resolve().parent.parent / "app" / "main.py"
    at = AppTest.from_file(str(app_path), default_timeout=30).run()
    assert not at.exception

def test_streamlit_app_navigation_and_views():
    """Verify navigating through all five views with retained results in session state."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    app_path = Path(__file__).resolve().parent.parent / "app" / "main.py"
    at = AppTest.from_file(str(app_path), default_timeout=30).run()
    assert not at.exception
    
    # Pre-populate session state with greedy and exact results
    g_res = run_greedy("scenario_2")
    e_res = run_exact("scenario_2")
    at.session_state["pq_results"].append(g_res)
    at.session_state["pq_results"].append(e_res)
    
    # Every page opens without errors, with results already in the session.
    for page in ("app_pages/console.py", "app_pages/your_emergency.py", "app_pages/quantum_lab.py",
                 "app_pages/results.py", "app_pages/evidence.py", "app_pages/method.py", "app_pages/home.py"):
        at.switch_page(page).run()
        assert not at.exception, page

    # The header's scenario picker switches to Scenario 1.
    at.switch_page("app_pages/console.py").run()
    at.selectbox(key="scenario_pick").set_value("scenario_1").run()
    assert not at.exception
    assert at.session_state["scenario_id"] == "scenario_1"

def test_run_with_loading_error_handling():
    """Verify that backend exceptions are caught by run_with_loading and recorded in pq_failures."""
    import ui_components as ui
    state = {"pq_failures": []}
    
    def failing_backend():
        raise RuntimeError("Simulated hardware or solver timeout")
        
    ok, exc = ui.run_with_loading(
        "Failing test run",
        failing_backend,
        failures_state=state,
        method="FailingMethod",
        scenario_id="scenario_2"
    )
    assert ok is False
    assert isinstance(exc, RuntimeError)
    assert len(state["pq_failures"]) == 1
    fail = state["pq_failures"][0]
    assert fail["method"] == "FailingMethod"
    assert fail["scenario_id"] == "scenario_2"
    assert "Simulated hardware or solver timeout" in fail["message"]
    assert fail["error_type"] == "RuntimeError"

def test_qaoa_rich_metadata_keys():
    """Verify QAOA experiment payload includes parameters, baselines, and timestamps for UI."""
    res = run_qaoa("scenario_2", p=1, seed=10, maxiter=5, shots=50)
    exp = res["experiment"]
    assert "timestamp" in exp
    assert "scale" in exp
    assert "initial_params" in exp and len(exp["initial_params"]) == 2
    assert "final_params" in exp and len(exp["final_params"]) == 2
    assert "baselines" in exp and len(exp["baselines"]) >= 1
    assert exp["baselines"][0]["feasibility_rate"] == 13 / 64

def test_qaoa_scenario1_baseline_is_ten_of_thirtytwo():
    """Verify Scenario 1 random feasibility baseline is programmatically 10/32."""
    res = run_qaoa("scenario_1", p=1, seed=10, maxiter=5, shots=50)
    exp = res["experiment"]
    assert exp["baselines"][0]["feasibility_rate"] == 10 / 32
    assert exp["baselines"][0]["optimum_probability"] == 1 / 32

def test_optimal_measurement_keys_derived_from_declared_order():
    """Verify optimal bitstrings are derived dynamically from declared variable order and little-endian convention."""
    k1 = get_optimal_measurement_key("scenario_1")
    assert k1 == "01001"
    
    k2 = get_optimal_measurement_key("scenario_2")
    assert k2 == "100001"

def test_prototype_dispatch_console_and_views_flow():
    """Verify emergency dispatch console behavior: candidate routes initially, actual routes and delta after run."""
    from app.ui_helpers import generate_why_it_changed, build_map_svg
    from app.result_adapter import get_landscape, get_scenario
    
    # 1. Verify Landscape statistics
    l1 = get_landscape("scenario_1")
    assert l1["total_states"] == 32
    assert l1["feasible_count"] == 10
    assert l1["feasibility_rate"] == 10 / 32
    
    l2 = get_landscape("scenario_2")
    assert l2["total_states"] == 64
    assert l2["feasible_count"] == 13
    assert l2["feasibility_rate"] == 13 / 64
    
    # 2. Verify Map SVG rendering in both states:
    # (A) Pre-run state: no result provided -> candidate routes only, no assigned routes
    s2 = get_scenario("scenario_2")
    svg_prerun = build_map_svg(s2, None)
    assert "<svg" in svg_prerun
    assert 'class="ln"' in svg_prerun  # candidate lines
    assert 'class="ln on"' not in svg_prerun  # NO active routes before execution
    assert 'backup pair' in svg_prerun
    
    # (B) Post-run state: result provided -> assigned routes rendered
    exact_res = run_exact("scenario_2")
    assert exact_res["objective_value"] == 13.0
    assert exact_res["assignments"] == [("A1", "C2"), ("A3", "C3")]
    
    svg_postrun = build_map_svg(s2, exact_res)
    assert 'class="ln on"' in svg_postrun  # active routes
    assert 'class="capt kept"' in svg_postrun  # backup preserved
    assert 'held' in svg_postrun  # A2 held
    
    # 3. Verify 'Why it changed' delta statement
    greedy_res = run_greedy("scenario_2")
    assert greedy_res["objective_value"] == 22.0
    why_text = generate_why_it_changed(exact_res, greedy_res, s2)
    assert "C3 is served by A3 instead of A2" in why_text
    assert "weighted response cost rises from 12 to 13" in why_text
    assert "coverage penalty falls from 10 to 0" in why_text
    assert "Dispatch cost 22 → 13 (-9)" in why_text

def test_json_export_and_methodology_assumptions():
    """Verify that JSON export captures clean run structures and methodology documents operational assumptions."""
    import json
    from app.result_adapter import run_exact, run_greedy
    
    # Verify export serialization of run records
    runs = [run_exact("scenario_2"), run_greedy("scenario_2")]
    clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in runs]
    serialized = json.dumps(clean, indent=2, default=str)
    deserialized = json.loads(serialized)
    assert len(deserialized) == 2
    assert deserialized[0]["method"] == "Exact Classical Solver"
    assert deserialized[0]["objective_value"] == 13.0
    assert deserialized[1]["method"] == "Greedy (Priority Nearest)"
    assert deserialized[1]["objective_value"] == 22.0






