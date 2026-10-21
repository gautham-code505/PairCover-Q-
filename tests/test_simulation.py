import itertools

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from qrescue.optimization.qubo import calculate_qubo_energy
from qrescue.simulation.engine import simulate, summarize
from qrescue.simulation.paircover import (
    EpochModel,
    build_model,
    coverage_terms,
    epoch_qubo,
    model_coverage_loss,
    objective,
    solve_exact,
    true_coverage_loss,
)
from qrescue.simulation.policies import ClosestIdle, CoverageSingle, DispatchState, PairCover
from qrescue.simulation.region import Call, default_region, generate_calls


def _random_model(rng, n_u, n_c, lam, with_eligibility):
    travel = rng.uniform(2, 18, (n_u, n_c)).round(1)
    covers = rng.uniform(size=(n_u, 8)) < 0.35
    zone_rate = rng.uniform(0.05, 0.6, 8)
    return build_model(travel, rng.choice([1, 2], n_c), rng.uniform(0, 6, n_c), covers, zone_rate,
                       lam, tau=20.0, max_travel=10.0 if with_eligibility else None), covers, zone_rate


def test_call_stream_is_reproducible():
    region = default_region()
    a = generate_calls(region, 3.0, 24, seed=7)
    b = generate_calls(region, 3.0, 24, seed=7)
    assert [(c.t, c.zone, c.priority) for c in a] == [(c.t, c.zone, c.priority) for c in b]
    assert all(x.t <= y.t for x, y in zip(a, a[1:]))


def test_coverage_terms_single_and_pair():
    covers = np.array([[1, 1, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]], dtype=bool)
    rate = np.array([0.5, 1.0, 0.4, 2.0])
    c, g = coverage_terms(covers, rate)
    assert c.tolist() == [0.5, 0.0, 0.4]
    assert g == {(0, 1): 1.0}           # zone 3 has three covering units and is left out


def test_pairwise_loss_is_exact_when_zones_have_at_most_two_covers():
    rng = np.random.default_rng(3)
    for _ in range(50):
        covers = rng.uniform(size=(4, 10)) < 0.3
        covers[:, covers.sum(0) > 2] = False
        rate = rng.uniform(0.1, 1.0, 10)
        model = EpochModel(np.ones((4, 1)), np.ones(1), np.ones(1), *coverage_terms(covers, rate), lam=1.0)
        for k in range(5):
            for sent in itertools.combinations(range(4), k):
                assert model_coverage_loss(model, set(sent)) == pytest.approx(true_coverage_loss(covers, rate, set(sent)))


def test_round1_backup_pair_scenario_is_reproduced():
    # Units A1, A2, A3; calls C2 (w=2), C3 (w=1); one zone covered only by A1 and A2 (lam * g = 10).
    travel = np.array([[4, 6], [5, 4], [12, 5]])
    covers = np.array([[1], [1], [0]], dtype=bool)
    model = build_model(travel, [2, 1], [0, 0], covers, np.array([1.0]), lam=10.0, tau=20.0)
    assignment, cost = solve_exact(model, allow_deferral=True)
    assert sorted(assignment) == [(0, 0), (2, 1)]      # A1 -> C2, A3 -> C3
    assert cost == pytest.approx(13.0)
    assert objective(model, [(0, 0), (1, 1)]) == pytest.approx(22.0)   # greedy


@pytest.mark.parametrize("seed", range(12))
def test_epoch_qubo_minimum_matches_exact_solver(seed):
    rng = np.random.default_rng(seed)
    model, _, _ = _random_model(rng, n_u=int(rng.integers(2, 4)), n_c=int(rng.integers(1, 4)), lam=20.0,
                                with_eligibility=bool(seed % 2))
    variables, h, J, const, _ = epoch_qubo(model)
    assert len(variables) <= 9
    best_x = min(itertools.product([0, 1], repeat=len(variables)), key=lambda x: calculate_qubo_energy(x, h, J))
    chosen = [variables[k] for k, v in enumerate(best_x) if v]
    _, exact_cost = solve_exact(model, allow_deferral=True)
    assert objective(model, chosen) == pytest.approx(exact_cost)
    assert calculate_qubo_energy(best_x, h, J) + const == pytest.approx(exact_cost)


def test_qubo_energy_equals_objective_on_every_feasible_assignment():
    model, _, _ = _random_model(np.random.default_rng(11), 3, 3, lam=15.0, with_eligibility=False)
    variables, h, J, const, _ = epoch_qubo(model)
    for x in itertools.product([0, 1], repeat=len(variables)):
        pairs = [variables[k] for k, v in enumerate(x) if v]
        cost = objective(model, pairs)
        if cost < float("inf"):
            assert calculate_qubo_energy(x, h, J) + const == pytest.approx(cost)


def test_no_coverage_batch_equals_linear_assignment():
    rng = np.random.default_rng(5)
    for _ in range(20):
        model, _, _ = _random_model(rng, 4, 3, lam=0.0, with_eligibility=False)
        assignment, cost = solve_exact(model, allow_deferral=False)
        cost_matrix = model.weight[None, :] * model.travel
        rows, cols = linear_sum_assignment(cost_matrix)
        assert len(assignment) == 3
        assert cost == pytest.approx(cost_matrix[rows, cols].sum())


def test_no_deferral_serves_every_call_it_can():
    model, _, _ = _random_model(np.random.default_rng(9), 2, 4, lam=40.0, with_eligibility=True)
    assignment, _ = solve_exact(model, allow_deferral=False)
    assert len(assignment) == 2


def _state(travel, priorities, covers, rate):
    calls = [Call(i, 0.0, 0, np.zeros(2), p, 20.0, False) for i, p in enumerate(priorities)]
    travel = np.asarray(travel, float)
    return DispatchState(1.0, calls, np.arange(travel.shape[0]), travel,
                         np.asarray(covers, bool), np.asarray(rate, float), 12.0)


def test_p1_call_always_gets_nearest_unit():
    # Unit 0 is nearest but is the sole cover of a busy zone; P1 must still get it.
    state = _state([[3.0], [6.0]], [1], [[1], [0]], [5.0])
    for policy in (ClosestIdle(), CoverageSingle(), PairCover(lam=100.0)):
        assert policy(state) == [(0, 0)]


def test_coverage_policies_protect_sole_cover_for_low_priority_call():
    state = _state([[3.0], [6.0]], [3], [[1], [0]], [5.0])
    assert ClosestIdle()(state) == [(0, 0)]
    assert CoverageSingle()(state) == [(1, 0)]
    assert PairCover(lam=20.0)(state) == [(1, 0)]


@pytest.mark.parametrize("policy_factory", [ClosestIdle, CoverageSingle, lambda: PairCover(0.0), lambda: PairCover(20.0)])
def test_simulation_invariants(policy_factory):
    region = default_region()
    calls = generate_calls(region, 4.0, 48, seed=1)
    result = simulate(region, calls, policy_factory(), 4.0, horizon_hours=48)
    assert not np.isnan(result.response).any()                       # every call dispatched
    assert result.deferrals == 0                                     # no call waits beside an idle unit
    for c in calls:
        travel = region.travel(region.base_xy[result.unit[c.id]], c.xy)
        assert result.dispatch_t[c.id] >= c.t
        assert result.response[c.id] == pytest.approx(result.dispatch_t[c.id] - c.t + travel)
    for a in range(region.n_ambulances):                             # no unit is double-booked
        mine = sorted(result.dispatch_t[result.unit == a])
        assert len(mine) == len(set(mine))
    s = summarize(result)
    assert 0.0 <= s["late_share"] <= 1.0 and 0.0 <= s["uncovered_demand"] <= 1.0
