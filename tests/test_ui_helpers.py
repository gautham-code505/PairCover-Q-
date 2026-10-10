"""Tests for app/ui_helpers.py (pure presentation logic; no Streamlit/Plotly needed).

All fixtures below are SYNTHETIC PRESENTATION FIXTURES. Their numbers are
arbitrary and are NOT QAOA, classical-solver or experimental output.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import ui_helpers as H  # noqa: E402

VARS = [("A1", "C2"), ("A1", "C3"), ("A2", "C2"), ("A2", "C3"), ("A3", "C2"), ("A3", "C3")]


def fx_result(method="Classical fixture", feasible=True, objective=10.0, exp=None, sid="S-FIXTURE"):
    return {"scenario_id": sid, "method": method, "assignments": [("A1", "C2")], "unserved_calls": ["C3"],
            "weighted_response_cost": 8.0, "coverage_penalty": 2.0, "objective_value": objective,
            "feasible": feasible, "runtime_seconds": 0.01, "experiment": exp or {}}


class FakeNp:  # mimics the numpy scalar/array protocol without importing numpy
    def __init__(self, v):
        self.v = v

    def tolist(self):
        return self.v


def test_formatting_handles_missing_inf_nan():
    assert H.fmt_num(None) == "—" and H.fmt_num(float("nan")) == "—" and H.fmt_num("x") == "—"
    assert H.fmt_num(float("inf")) == "∞" and H.fmt_num(-float("inf")) == "−∞"
    assert H.fmt_num(1234.5, 1) == "1,234.5" and H.fmt_num(True) == "—"
    assert H.fmt_pct(0.1234) == "12.3%" and H.fmt_pct(None) == "—"
    assert H.fmt_seconds(0.0123) == "12 ms" and H.fmt_seconds(2.5) == "2.50 s"
    assert H.fmt_feasible(None) == "? unknown"


def test_numpy_like_values_are_normalised():
    r = H.normalize_result(fx_result(feasible=FakeNp(True), objective=FakeNp(7)))
    assert r["feasible"] is True and r["objective_value"] == 7.0 and not r["_problems"]


def test_missing_metrics_stay_none_not_zero():
    r = H.normalize_result({"method": "m"})
    assert r["objective_value"] is None and r["feasible"] is None and r["assignments"] == []
    assert any("Missing key" in p for p in r["_problems"])
    assert H.validate_result(5)[0].startswith("Result must be a mapping")


def test_normalize_results_skips_non_mappings():
    good, issues = H.normalize_results([fx_result(), "oops", None])
    assert len(good) == 1 and len(issues) == 2


def test_provenance_prefers_explicit_kind_and_flags_inference():
    assert H.provenance(fx_result(exp={"kind": "classical_exact"}))["inferred"] is False
    p = H.provenance(fx_result(method="QAOA p=1", exp={"final_params": [0.1]}))
    assert p["is_qaoa"] and p["inferred"]
    assert not H.provenance(fx_result(method="Brute force"))["is_qaoa"]
    assert H.provenance(fx_result(method="mystery"))["kind"] == "unspecified"


def test_retain_result_replaces_latest_but_keeps_distinct_run_ids():
    st = {}
    H.retain_result(st, fx_result(objective=1))
    H.retain_result(st, fx_result(objective=2))
    assert [r["objective_value"] for r in st["pq_results"]] == [2]
    H.retain_result(st, fx_result(exp={"run_id": "a"}))
    H.retain_result(st, fx_result(exp={"run_id": "b"}))
    H.retain_result(st, fx_result(exp={"run_id": "a"}, objective=99))
    assert len(st["pq_results"]) == 3 and st["pq_results"][-1]["objective_value"] == 99


def test_retain_result_trims_and_stores_plain_python():
    st = {}
    for i in range(5):
        H.retain_result(st, fx_result(sid=f"S{i}", objective=FakeNp(i)), max_items=3)
    assert len(st["pq_results"]) == 3 and isinstance(st["pq_results"][0]["objective_value"], int)


def test_failure_record_has_no_metrics():
    f = H.make_failure("QAOA", "S1", ValueError("boom"), stage="sampling")
    assert f["error_type"] == "ValueError" and f["message"] == "boom" and "objective_value" not in f
    st = {}
    H.retain_failure(st, f)
    assert len(st["pq_failures"]) == 1


def test_best_feasible_ignores_infeasible_and_reports_ties():
    rs = H.normalize_results([fx_result("A", True, 5), fx_result("B", True, 5), fx_result("C", False, 1),
                              fx_result("D", None, 0), fx_result("E", True, float("inf"))])[0]
    tied, best = H.best_feasible(rs)
    assert tied == ["A", "B"] and best == 5
    assert H.best_feasible([r for r in rs if r["method"] in ("C", "D")]) == ([], None)


def test_aggregate_uses_feasible_runs_only():
    rs = H.normalize_results([fx_result("Q", True, 10), fx_result("Q", True, 20), fx_result("Q", False, 3)])[0]
    a = H.aggregate_runs(rs)[0]
    assert a["runs"] == 3 and a["feasible_runs"] == 2 and math.isclose(a["feasible_rate"], 2 / 3)
    assert (a["objective_min"], a["objective_mean"], a["objective_max"]) == (10, 15, 20)


def test_objective_difference_needs_feasible_reference():
    rs = H.normalize_results([fx_result("Ref", True, 10), fx_result("Q", True, 12), fx_result("Z", True, 9, sid="other")])[0]
    d = H.objective_difference(rs, "Ref")
    assert len(d) == 1 and d[0]["abs_diff"] == 2 and math.isclose(d[0]["pct_diff"], 20.0)
    assert H.objective_difference(rs, "Missing") == []


def test_decode_bitstring_uses_qiskit_little_endian():
    # key '000001' -> q0 = 1 -> x0 -> VARS[0]
    assert H.decode_bitstring("000001", VARS) == [("A1", "C2")]
    assert H.decode_bitstring("100000", VARS) == [("A3", "C3")]
    assert H.decode_bitstring("100000", VARS, "variable_order") == [("A1", "C2")]
    assert H.decode_bitstring("0101", VARS) is None and H.decode_bitstring("00000x", VARS) is None
    assert H.decode_bitstring("000001", None) is None


def test_sample_rows_prefer_table_else_counts_without_inventing_feasibility():
    rows = H.build_sample_rows({"counts": {"000001": 30, "000010": 70}}, VARS)
    assert [r["bitstring"] for r in rows] == ["000010", "000001"]
    assert math.isclose(rows[0]["probability"], 0.7) and rows[0]["feasible"] is None
    rows = H.build_sample_rows({"counts": {"000001": 1}, "feasible_bitstrings": {"000001": False}}, VARS)
    assert rows[0]["feasible"] is False
    rows = H.build_sample_rows({"sample_table": [{"bitstring": "11", "count": 2, "feasible": True, "assignments": [["A1", "C2"]]}]})
    assert rows[0]["feasible"] is True and H.format_assignments(rows[0]["assignments"]) == "A1→C2"
    assert H.build_sample_rows({}) == []


def test_history_requires_two_numbers_and_never_promotes_endpoints():
    assert H.get_history({"initial_qubo_energy": 1.0, "final_qubo_energy": 0.0}) is None
    assert H.get_history({"history": {"values": [1.0]}}) is None
    h = H.get_history({"energy_history": [3, 2, "x", float("nan"), 1]})
    assert h["values"] == [3.0, 2.0, 1.0] and h["quantity"] == "unspecified"


def test_history_reference_only_when_same_quantity():
    base = {"values": [3, 2, 1], "quantity": "expected_qubo_energy"}
    assert H.get_history({"history": {**base, "reference": {"value": 0.5, "label": "r"}}})["reference"] is None
    ok = H.get_history({"history": {**base, "reference": {"value": 0.5, "label": "r", "same_quantity": True}}})
    assert ok["reference"]["value"] == 0.5 and "Expected" in ok["quantity_label"]


def test_outcome_split_is_consistent_and_optional():
    s = H.outcome_split({"sampled_feas_rate": 0.4, "optimum_hits": 100, "shots": 1000})
    assert math.isclose(s["optimum"], 0.1) and math.isclose(s["other_feasible"], 0.3) and math.isclose(s["infeasible"], 0.6)
    assert H.outcome_split({}) is None
    assert H.outcome_split({"sampled_feas_rate": 0.5})["optimum"] is None


def test_optimizer_status_and_energy_summary_only_report_supplied_values():
    assert H.optimizer_status({"success": False, "message": "maxiter"})["status"] == "failed"
    assert H.optimizer_status({})["status"] == "unknown"
    rows = H.energy_summary({"final_qubo_energy": -1.5, "best_cost": 42})
    assert [r["key"] for r in rows] == ["final_qubo_energy", "best_cost"]
    assert rows[0]["quantity"] != rows[1]["quantity"]


def test_latest_by_method_keeps_last_per_method():
    rs = H.normalize_results([fx_result("A", objective=1), fx_result("B"), fx_result("A", objective=2), fx_result("C", sid="x")])[0]
    out = H.latest_by_method(rs, "S-FIXTURE")
    assert [(r["method"], r["objective_value"]) for r in out] == [("B", 10.0), ("A", 2.0)]
