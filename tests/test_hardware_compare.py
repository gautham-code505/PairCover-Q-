import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "app"))

import hardware_compare as hc


@pytest.fixture(scope="module")
def runs():
    r = hc.load_hardware_runs()
    if not hc.problem_choices(r):
        pytest.skip("no real-device result in reports/ibm_hardware")
    return r


def test_real_runs_listed_first(runs):
    assert runs[0]["kind"] == "real"


def test_exact_is_optimal_and_greedy_never_beats_it(runs):
    for iid, p in hc.problem_choices(runs):
        res = hc.compare(iid, p, runs)
        rows = {r["key"]: r for r in res["rows"]}
        assert rows["exact"]["cost"] == pytest.approx(res["exact_cost"])
        assert rows["greedy"]["cost"] >= res["exact_cost"] - 1e-9
        assert 0 < res["uniform_p_opt"] <= res["uniform_valid_p_opt"] <= 1


def test_live_simulator_matches_stored_noiseless_probability(runs):
    real = runs[0]
    for c in real["circuits"]:
        sim = next(r for r in hc.compare(c["id"], c["p"], runs)["rows"] if r["key"] == "sim")
        assert sim["p_opt"] == pytest.approx(c["ideal_p_opt"], abs=1e-6)
        assert sim["p_valid"] == pytest.approx(c["ideal_p_feasible"], abs=1e-6)


def test_hardware_row_reports_most_frequent_answer(runs):
    res = hc.compare("oper-4q-1", 2, runs)
    hw = next(r for r in res["rows"] if r["kind"] == "hardware")
    assert hw["optimal"] and hc.label(hw["pairs"]) == "A3 → C1"
    assert hw["seconds"] > hw["chip_seconds"] > 0


def test_decode_and_label():
    assert hc.decode(0b101, [(0, 0), (1, 0), (2, 1)]) == [(0, 0), (2, 1)]
    assert hc.label([]) == "no ambulance sent"


def test_mitigation_rows_compare_within_one_session(runs):
    rows = {r["key"]: r for r in hc.compare("oper-4q-1", 2, runs)["rows"]}
    if "hw_ro" not in rows:
        pytest.skip("no readout-calibrated runs")
    ro = rows["hw_ro"]
    assert ro["p_opt_before_readout"] is not None and ro["n_runs"] <= rows["hw_raw"]["n_runs"]
    assert rows["hw_raw"]["p_opt_lo"] <= rows["hw_raw"]["p_opt"] <= rows["hw_raw"]["p_opt_hi"]
