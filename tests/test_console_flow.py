"""
Independent regression checks for the dispatch console flow and for quantities
the UI labels as exact.

These drive the real Streamlit script (app/main.py) headlessly, so they fail if
the console ever shows a run other than the one that just executed.
"""

from __future__ import annotations

import itertools
import math
import os
import re
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_ROOT, os.path.join(_ROOT, "src"), os.path.join(_ROOT, "app")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from streamlit.testing.v1 import AppTest

from app import result_adapter as ra
from qrescue.optimization.qubo import calculate_qubo_energy
from qrescue.optimization.scenario import generate_qubo_scenario1
from qrescue.optimization.scenario2 import generate_qubo_scenario2

MAIN = os.path.join(_ROOT, "app", "main.py")


def _console(at: AppTest) -> dict:
    """What the console is showing right now, read from the rendered markup."""
    md = " ".join(m.value for m in at.markdown)
    zone = re.search(r"Simulated Response Zone</span><span[^>]*>([^<]*)<", md)
    cost = re.search(r"<b>([^<]*)</b>latest dispatch cost", md)
    card = re.search(r'class="res"><div><div class="row"><b>([^<]*)</b>', md)
    return {
        "zone": zone.group(1) if zone else None,
        "cost": cost.group(1) if cost else None,
        "card": card.group(1) if card else None,
    }


def _run(at: AppTest, method: str) -> dict:
    at.radio(key="dc_m_choice").set_value(method).run()
    at.button(key="dc_run_btn").click().run()
    assert not at.exception, [e.value for e in at.exception]
    return _console(at)


@pytest.fixture()
def app() -> AppTest:
    at = AppTest.from_file(MAIN, default_timeout=120).run()
    assert not at.exception
    return at


def test_console_starts_with_no_decision(app: AppTest) -> None:
    shown = _console(app)
    assert shown["card"] is None
    assert shown["cost"] == "—"
    assert "no decision" in shown["zone"]


def test_console_shows_the_run_that_just_executed(app: AppTest) -> None:
    shown = _run(app, "Nearest available")
    assert "Nearest available" in shown["card"] and "Nearest available" in shown["zone"]
    assert float(shown["cost"]) == 22.0

    shown = _run(app, "Exact optimisation")
    assert "Exact optimisation" in shown["card"] and "Exact optimisation" in shown["zone"]
    assert float(shown["cost"]) == 13.0


def test_new_run_wins_over_an_earlier_run_picker_choice(app: AppTest) -> None:
    _run(app, "Nearest available")
    _run(app, "Exact optimisation")
    picker = next(s for s in app.selectbox if s.key == "dc_select_run")
    picker.set_value(0).run()
    assert "Nearest available" in _console(app)["card"]

    shown = _run(app, "Exact optimisation")
    assert "Exact optimisation" in shown["card"]
    assert float(shown["cost"]) == 13.0


def test_scenario_switch_never_shows_the_other_scenarios_result(app: AppTest) -> None:
    _run(app, "Exact optimisation")
    app.selectbox(key="hdr_scen_sel").set_value("Validation case · 5 qubits (Scenario 1)").run()
    shown = _console(app)
    assert shown["card"] is None and shown["cost"] == "—"

    shown = _run(app, "Exact optimisation")
    assert float(shown["cost"]) == 62.0


@pytest.mark.parametrize("sid,gen", [("scenario_1", generate_qubo_scenario1), ("scenario_2", generate_qubo_scenario2)])
def test_qubo_matches_dispatch_cost_and_ground_state_is_the_feasible_optimum(sid, gen) -> None:
    scen = ra.get_scenario(sid)
    h, J = gen()
    metrics = ra.calculate_scenario1_raw_metrics if sid == "scenario_1" else ra.calculate_scenario2_raw_metrics
    feasible, infeasible = [], []
    for bits in itertools.product((0, 1), repeat=len(scen["variables"])):
        energy = calculate_qubo_energy(bits, h, J)
        _, _, obj, ok = metrics(bits)
        if ok:
            assert energy + scen["qubo_offset"] == pytest.approx(obj)
            feasible.append(obj)
        else:
            infeasible.append(energy + scen["qubo_offset"])
    assert len(feasible) == scen["landscape"]["feasible_count"]
    assert scen["landscape"]["feasibility_rate"] == pytest.approx(len(feasible) / 2 ** len(scen["variables"]))
    # No rule-breaking state may undercut the best valid plan, or QAOA would be steered to it.
    assert min(infeasible) > min(feasible)


@pytest.mark.parametrize("sid", ["scenario_1", "scenario_2"])
def test_zone_layout_distances_equal_travel_times(sid) -> None:
    scen = ra.get_scenario(sid)
    for (amb, call), minutes in scen["travel_times"].items():
        assert math.dist(scen["positions"][amb], scen["positions"][call]) == pytest.approx(minutes, abs=1e-3)


def test_statevector_figures_do_not_depend_on_shot_count() -> None:
    """Shots only change the sampled estimate. The exact statevector values must not move."""
    few = ra.run_qaoa("scenario_2", p=1, seed=10, maxiter=100, shots=100)["experiment"]
    many = ra.run_qaoa("scenario_2", p=1, seed=10, maxiter=100, shots=10000)["experiment"]
    assert few["final_params"] == pytest.approx(many["final_params"])
    assert few["sv_opt_prob"] == pytest.approx(many["sv_opt_prob"])
    assert few["sv_feas_rate"] == pytest.approx(many["sv_feas_rate"])
    # The sampled rates are estimates of the exact ones, within sampling error.
    for exp in (few, many):
        n = exp["shots"]
        for sampled, exact in ((exp["sampled_opt_prob"], exp["sv_opt_prob"]), (exp["feasibility_rate"], exp["sv_feas_rate"])):
            assert abs(sampled - exact) < 5 * math.sqrt(exact * (1 - exact) / n)
        assert exp["optimum_hits"] == exp["counts"].get(exp["optimal_bitstring"], 0)


def _main_text(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)


def test_main_menu_still_works_after_opening_a_diagnostic_tool(app: AppTest) -> None:
    app.radio(key="adv_tool_pick").set_value("Overview").run()
    app.radio(key="main_view").set_value("⚛️ Quantum Lab").run()
    assert not app.exception
    assert app.radio(key="adv_tool_pick").value == "(None - Main Console)"
    assert "QAOA Circuit" in _main_text(app)


def test_scenario_builder_run_button_runs_the_ticked_methods(app: AppTest) -> None:
    app.radio(key="adv_tool_pick").set_value("Scenario Builder").run()
    next(b for b in app.button if "Run selected" in (b.label or "")).click().run()
    assert not app.exception
    assert len(app.session_state["pq_results"]) >= 1


def test_guided_compare_runs_both_and_explains_the_change(app: AppTest) -> None:
    app.button(key="dc_guided").click().run()
    assert not app.exception
    shown = _console(app)
    assert "Exact optimisation" in shown["card"] and float(shown["cost"]) == 13.0
    text = _main_text(app)
    assert "Why it changed" in text and "22" in text


def test_no_scenario_two_figures_leak_into_scenario_one(app: AppTest) -> None:
    app.selectbox(key="hdr_scen_sel").set_value("Validation case · 5 qubits (Scenario 1)").run()
    app.radio(key="dc_m_choice").set_value("QAOA").run()
    app.button(key="dc_run_btn").click().run()
    text = _main_text(app)
    assert "6 qubits" not in text and "5 qubits" in text
    assert "Matches optimum (62)" in text          # 62 is scenario 1's enumerated optimum
    app.radio(key="main_view").set_value("📊 Results & Benchmarks").run()
    text = _main_text(app)
    assert "68 / 1,000" not in text and "6.47%" not in text


def test_exact_alone_does_not_quote_a_nearest_available_result_that_never_ran(app: AppTest) -> None:
    _run(app, "Exact optimisation")
    text = _main_text(app)
    assert "Run Nearest available to compare" in text
    assert "22.0" not in text


def test_status_sentence_describes_only_what_the_result_did() -> None:
    import ui_helpers as H  # noqa: E402  (app/ is on sys.path via the app import above)
    scen = ra.get_scenario("scenario_2")
    tone, text = H.status_sentence(None, scen)
    assert tone == "idle" and "No decision yet" in text
    tone, text = H.status_sentence(ra.run_greedy("scenario_2"), scen)
    assert tone == "warn" and "A1+A2 left" in text and "<b>22</b>" in text
    tone, text = H.status_sentence(ra.run_exact("scenario_2"), scen)
    assert tone == "ok" and "kept A2 in reserve" in text and "<b>13</b>" in text


def test_workflow_steps_follow_progress() -> None:
    import ui_helpers as H
    assert [s for _, s in H.workflow_steps(0, False)] == ["done", "now", "todo", "todo"]
    assert [s for _, s in H.workflow_steps(1, False)] == ["done", "done", "done", "now"]
    assert all(s == "done" for _, s in H.workflow_steps(2, True))


def test_theme_config_defines_both_modes() -> None:
    import tomllib
    with open(os.path.join(_ROOT, ".streamlit", "config.toml"), "rb") as fh:
        theme = tomllib.load(fh)["theme"]
    assert {"light", "dark"} <= set(theme)  # both needed for the Light/Dark switch
