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


def test_readout_correction_undoes_known_flips():
    errors = {5: (0.05, 0.10), 9: (0.02, 0.08)}            # (P(1|0), P(0|1)) per physical qubit
    true = {"01": 0.7, "10": 0.3}                          # qubit 0 is the rightmost bit
    noisy = {}
    for bits, p in true.items():
        for out in ("00", "01", "10", "11"):
            w = p
            for k, q in enumerate([5, 9]):
                t, o = bits[-1 - k], out[-1 - k]
                e01, e10 = errors[q]
                w *= (e01 if o == "1" else 1 - e01) if t == "0" else (e10 if o == "0" else 1 - e10)
            noisy[out] = noisy.get(out, 0) + w
    fixed = run_ibm_hardware.correct_readout({k: v * 1e6 for k, v in noisy.items()}, [5, 9], errors)
    assert fixed.get("01", 0) == pytest.approx(0.7, abs=1e-6) and fixed.get("10", 0) == pytest.approx(0.3, abs=1e-6)


def test_readout_errors_from_calibration_counts():
    errs = run_ibm_hardware.readout_errors({"00": 90, "01": 10}, {"11": 80, "10": 20}, [3, 7])
    assert errs[3] == pytest.approx((0.10, 0.20)) and errs[7] == pytest.approx((0.0, 0.0))
