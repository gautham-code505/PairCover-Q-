"""Tests for "Create your own emergency" (app/custom_emergency.py and its screen)."""

from __future__ import annotations

import os
import re
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_ROOT, os.path.join(_ROOT, "src"), os.path.join(_ROOT, "app")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import custom_emergency as ce  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

TOWN = ce.PRESETS["Town keeps its only ambulance"]


@pytest.mark.parametrize("name", list(ce.PRESETS))
def test_every_preset_solves_and_exact_is_the_cheapest_plan(name) -> None:
    pre = ce.PRESETS[name]
    scen = ce.build_scenario(pre["calls"], pre["busy"])
    plans = scen["landscape"]["feasible"]
    greedy, exact = ce.run_custom_greedy(scen), ce.run_custom_exact(scen)
    assert exact["objective_value"] == pytest.approx(plans[0]["obj"])
    assert greedy["objective_value"] >= exact["objective_value"] - 1e-9
    for r in (greedy, exact):
        assert r["objective_value"] == pytest.approx(r["weighted_response_cost"] + r["coverage_penalty"])
        units = [a for a, _ in r["assignments"]]
        calls = [c for _, c in r["assignments"]]
        assert len(set(units)) == len(units) and len(set(calls)) == len(calls)
        assert not set(units) & set(pre["busy"])


def test_town_preset_shows_the_coverage_trade_off() -> None:
    scen = ce.build_scenario(TOWN["calls"], TOWN["busy"])
    greedy, exact = ce.run_custom_greedy(scen), ce.run_custom_exact(scen)
    assert ("A4", "C2") in greedy["assignments"] and greedy["coverage_penalty"] > 0   # town's only unit leaves
    assert ("A1", "C2") in exact["assignments"] and exact["coverage_penalty"] == 0    # city unit goes instead
    assert exact["weighted_response_cost"] > greedy["weighted_response_cost"]         # slightly slower ...
    assert exact["objective_value"] < greedy["objective_value"]                       # ... but cheaper overall


def test_zero_coverage_weight_removes_the_trade_off() -> None:
    scen = ce.build_scenario(TOWN["calls"], TOWN["busy"], lam=0.0)
    assert ce.run_custom_exact(scen)["coverage_penalty"] == 0
    assert ce.run_custom_greedy(scen)["coverage_penalty"] == 0


def test_qaoa_returns_a_real_valid_plan_and_honest_counts() -> None:
    scen = ce.build_scenario(TOWN["calls"], TOWN["busy"])
    r = ce.run_custom_qaoa(scen, p=1, seed=10, shots=500)
    exp = r["experiment"]
    assert r["feasible"]
    assert any(abs(p["obj"] - r["objective_value"]) < 1e-9 for p in scen["landscape"]["feasible"])
    assert 0 <= exp["optimum_hits"] <= exp["shots"] == 500
    assert 0.0 <= exp["sv_opt_prob"] <= 1.0 and 0.0 <= exp["random_opt_prob"] <= 1.0
    again = ce.run_custom_qaoa(scen, p=1, seed=10, shots=500)["experiment"]
    assert again["optimum_hits"] == exp["optimum_hits"]          # same seed, same samples


def test_qaoa_refuses_situations_too_large_to_simulate() -> None:
    scen = ce.build_scenario([(15, 1), (20, 1), (21, 1), (14, 1)], [])
    ok, why = ce.qaoa_available(scen)
    assert not ok and "qubits" in why
    with pytest.raises(ValueError):
        ce.run_custom_qaoa(scen)


@pytest.mark.parametrize("calls,busy", [([], []), ([(15, 1)] * 5, []), ([(15, 1)], ce.ambulance_names())])
def test_bad_input_is_rejected_with_a_message(calls, busy) -> None:
    with pytest.raises(ValueError):
        ce.build_scenario(calls, busy)


def test_each_situation_has_its_own_id() -> None:
    a = ce.build_scenario(TOWN["calls"], [])
    b = ce.build_scenario(TOWN["calls"], ["A5"])
    c = ce.build_scenario(TOWN["calls"], [], lam=10.0)
    assert len({a["scenario_id"], b["scenario_id"], c["scenario_id"]}) == 3
    assert ce.build_scenario(TOWN["calls"], [])["scenario_id"] == a["scenario_id"]


def test_screen_builds_compares_and_explains() -> None:
    at = AppTest.from_file(os.path.join(_ROOT, "app", "main.py"), default_timeout=180).run()
    at.radio(key="main_view").set_value("🆘 Create Your Emergency").run()
    assert not at.exception
    at.button(key="ce_guided").click().run()
    assert not at.exception
    text = " ".join(m.value for m in at.markdown)
    assert "Why it changed" in text and "A1 instead of A4" in text
    # A different situation must start clean: no result carried over.
    at.button(key="ce_preset_Short-staffed night").click().run()
    assert not at.exception
    assert re.search(r"<b>—</b>latest dispatch cost", " ".join(m.value for m in at.markdown))
