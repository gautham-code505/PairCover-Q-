import numpy as np
import pytest

from qrescue.quantum.loop_solver import QAOASolver, max_matching_size
from qrescue.simulation.engine import simulate
from qrescue.simulation.instances import model_from_dict, model_to_dict, surge_instances
from qrescue.simulation.paircover import build_model, epoch_qubo, objective, solve_exact
from qrescue.simulation.policies import PairCover
from qrescue.simulation.region import default_region, generate_calls


def test_instance_round_trip():
    region = default_region()
    inst = surge_instances(region, 5.0, 5.0, [8], 1, np.random.default_rng(0))
    assert inst and inst[0]["qubits"] == 8
    model = model_from_dict(inst[0])
    assert len(epoch_qubo(model)[0]) == 8
    again = model_from_dict(model_to_dict(model))
    assert solve_exact(again, True)[1] == pytest.approx(solve_exact(model, True)[1])


def test_max_matching_size_respects_eligibility():
    travel = np.array([[3.0, 30.0], [4.0, 31.0]])      # only unit 0/1 -> call 0 within threshold
    model = build_model(travel, [1, 1], [0, 0], np.zeros((2, 1), bool), np.zeros(1), 5.0, 20.0, max_travel=12.0)
    # call 1's nearest unit (unit 0) is always eligible, so a full matching exists
    assert max_matching_size(model) == 2


def test_qaoa_solver_returns_valid_assignment_matching_exact_on_round1_case():
    travel = np.array([[4, 6], [5, 4], [12, 5]])
    covers = np.array([[1], [1], [0]], dtype=bool)
    model = build_model(travel, [2, 1], [0, 0], covers, np.array([1.0]), lam=10.0, tau=20.0)
    solver = QAOASolver(p=2, shots=256, seed=0)
    assignment, cost = solver(model)
    assert cost == pytest.approx(objective(model, assignment))
    assert cost == pytest.approx(13.0)
    assert solver.stats.qaoa_runs == 1 and solver.stats.qaoa_fallback == 0


def test_qaoa_in_loop_never_breaks_simulation_invariants():
    region = default_region()
    calls = generate_calls(region, 5.0, 6, seed=2)
    solver = QAOASolver(p=1, shots=128, seed=0)
    res = simulate(region, calls, PairCover(5.0, solver=solver), 5.0, horizon_hours=6)
    assert not np.isnan(res.response).any()
    assert res.deferrals == 0
    st = solver.stats
    assert st.qaoa_agrees + st.qaoa_fallback <= st.qaoa_runs
