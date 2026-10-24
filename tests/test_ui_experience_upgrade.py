"""
PairCover-Q — UI Experience Upgrade & Benchmark Consistency Verification Suite.

Validates:
1. Navigation items (symbols and secondary tools)
2. Animated simulation map states (pulsing nodes, moving vehicles, route traces, pause/motion controls)
3. Top Executive Decision Summary Card & operational trade-off explanations
4. Quantum metrics reporting and benchmark consistency (shot counts, baselines)
5. Local CSV dataset validation and provenance disclosures
"""

from __future__ import annotations

import os
import sys
import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_SRC = os.path.join(_ROOT, "src")
for _p in (_ROOT, _SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app import ui_components as ui
from app import ui_helpers as H
from app.result_adapter import get_scenario, run_exact, run_greedy, run_qaoa, get_landscape
from qrescue.data.validator import validate_ems_csv, detect_field_mapping


def test_navigation_views_and_aliases() -> None:
    """Verify primary navigation items with symbols and backward-compatible views."""
    assert "🚑 Dispatch Console" in ui.PRIMARY_VIEWS
    assert "⚛️ Quantum Lab" in ui.PRIMARY_VIEWS
    assert "📊 Results & Benchmarks" in ui.PRIMARY_VIEWS
    assert "📘 Method & Data" in ui.PRIMARY_VIEWS
    assert "🆘 Create Your Emergency" in ui.PRIMARY_VIEWS
    assert len(ui.PRIMARY_VIEWS) == 5

    # Verify all primary and secondary views are present in VIEWS and _VIEW_SUBTITLES
    for pv in ui.PRIMARY_VIEWS:
        assert pv in ui.VIEWS
        assert pv in ui._VIEW_SUBTITLES

    for sv in ("Overview", "Scenario Builder", "Dispatch Simulator", "Benchmark Analytics"):
        assert sv in ui.VIEWS
        assert sv in ui._VIEW_SUBTITLES


def test_animated_map_svg_features_and_controls() -> None:
    """Verify pulsing calls, moving vehicle markers, and reduced-motion states."""
    s2 = get_scenario("scenario_2")
    exact_res = run_exact("scenario_2")

    # 1. Animated state
    svg_anim = H.build_map_svg(s2, exact_res, animate=True)
    assert '<svg' in svg_anim
    assert 'class="call-pulse"' in svg_anim
    assert 'class="ln-trace"' in svg_anim
    assert 'class="veh-marker"' in svg_anim
    assert '<animateMotion' in svg_anim
    assert 'class="ln on"' in svg_anim
    assert 'backup preserved' in svg_anim
    assert 'data-status="kept"' in svg_anim

    # 2. Reduced motion / paused state (animate=False)
    svg_static = H.build_map_svg(s2, exact_res, animate=False)
    assert '<svg' in svg_static
    assert 'class="call-pulse"' not in svg_static
    assert 'class="ln-trace"' not in svg_static
    assert '<animateMotion' not in svg_static
    assert 'class="ln on"' in svg_static

    # 3. Greedy run state (breaks backup)
    greedy_res = run_greedy("scenario_2")
    svg_greedy = H.build_map_svg(s2, greedy_res, animate=True)
    assert 'backup broken' in svg_greedy
    assert 'data-status="hit"' in svg_greedy


def test_analytical_random_baselines_consistency() -> None:
    """Verify exact calculation of uniform random baselines for Scenario 1 and Scenario 2."""
    l1 = get_landscape("scenario_1")
    assert l1["total_states"] == 32
    assert l1["feasible_count"] == 10
    assert abs(l1["feasibility_rate"] - (10 / 32)) < 1e-9  # 31.25%
    assert abs(l1["optimum_prob"] - (1 / 32)) < 1e-9       # 3.125%

    l2 = get_landscape("scenario_2")
    assert l2["total_states"] == 64
    assert l2["feasible_count"] == 13
    assert abs(l2["feasibility_rate"] - (13 / 64)) < 1e-9  # 20.3125%
    assert abs(l2["optimum_prob"] - (1 / 64)) < 1e-9       # 1.5625%


def test_qaoa_metric_separation_and_shot_reporting() -> None:
    """Verify distinct separation of energy, cost, and explicit shot count reporting."""
    q_res = run_qaoa("scenario_2", p=1, seed=10, maxiter=50, shots=500)
    exp = q_res["experiment"]

    # Strict quantity separation
    assert "qubo_energy" in q_res or "final_qubo_energy" in exp
    assert "sampled_opt_prob" in exp
    assert "sv_opt_prob" in exp
    assert exp["shots"] == 500
    assert "optimum_hits" in exp
    assert isinstance(exp["optimum_hits"], int)

    # Feasibility rates
    assert 0.0 <= exp["feasibility_rate"] <= 1.0
    assert 0.0 <= exp["sv_feas_rate"] <= 1.0


def test_csv_upload_validation_end_to_end() -> None:
    """Verify CSV validation handles standard EMS schemas and distinguishes historical data."""
    csv_sample = (
        "Call Date,Emergency Type,Vehicle Type,Caller Taluk,Response Time,BS(km)\n"
        "2026-03-01 10:15:00,Cardiac,108 BLS,Chennai Central,12.4,4.2\n"
        "2026-03-01 10:22:00,Trauma,108 ALS,Madurai North,8.1,2.5\n"
        "2026-03-01 10:35:00,Maternal,108 BLS,Coimbatore South,15.6,7.8\n"
    )
    report = validate_ems_csv(csv_sample)
    assert report["is_valid"] is True
    assert report["row_count"] == 3
    assert report["detected_fields"]["call_time"] == "Call Date"
    assert report["detected_fields"]["response_time"] == "Response Time"
    assert report["detected_fields"]["distance"] == "BS(km)"
    assert report["stats"]["response_time"]["count"] == 3
    assert report["stats"]["response_time"]["mean"] == pytest.approx(12.033, 0.01)
    assert "historical records" in report["provenance_disclosure"].lower()
