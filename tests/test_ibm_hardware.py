import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

run_ibm_hardware = pytest.importorskip("run_ibm_hardware")


def test_decode_follows_qiskit_bit_order():
    variables = [(0, 0), (1, 0), (2, 1)]
    assert run_ibm_hardware.decode(0b101, variables) == ["A1->C1", "A3->C2"]


def test_score_all_shots_on_classical_optimum():
    inst, ramp = run_ibm_hardware.load_benchmark()
    prob = run_ibm_hardware.problem(inst["oper-4q-1"])
    best = format(prob["classical_best"], f"0{prob['n']}b")
    meta = {"id": "oper-4q-1", "random_feasible_p_opt": 0.2}
    r = run_ibm_hardware.score(meta, {best: 900, "0000": 100}, inst)
    assert r["p_opt"] == pytest.approx(0.9)
    assert r["most_frequent_is_optimal"] and r["hardware_pick_is_optimal"]
    assert r["hardware_pick"] == run_ibm_hardware.decode(prob["classical_best"], prob["variables"])
    assert r["gain_vs_uniform_feasible"] == pytest.approx(4.5)


def test_score_without_feasible_samples():
    inst, _ = run_ibm_hardware.load_benchmark()
    meta = {"id": "oper-4q-1", "random_feasible_p_opt": 0.2}
    r = run_ibm_hardware.score(meta, {"1111": 10}, inst)
    assert r["p_feasible"] == 0 and r["hardware_pick"] is None
