"""
Dispatch policies compared in the rolling simulation.

Every policy receives the same DispatchState at each decision epoch and returns a
list of (idle_index, call_index) pairs. P1 calls are always sent the nearest idle
unit by the coverage-aware policies too, so coverage can never delay a top-priority call.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from qrescue.simulation.paircover import (
    build_model,
    model_coverage_loss,
    solve_exact,
    true_coverage_loss,
)


@dataclass
class DispatchState:
    t: float
    calls: list                 # pending Call objects
    idle: np.ndarray            # ambulance ids that are idle now
    travel: np.ndarray          # (len(idle), len(calls)) minutes
    covers: np.ndarray          # (len(idle), Z) bool, unit reaches zone within threshold
    zone_rate: np.ndarray       # (Z,) expected calls per hour
    cover_minutes: float


def call_order(calls) -> list:
    """Most urgent first, then oldest first."""
    return sorted(range(len(calls)), key=lambda j: (calls[j].priority, calls[j].t))


def _nearest(state: DispatchState, free: set, j: int) -> int:
    return min(free, key=lambda u: (state.travel[u, j], u))


class ClosestIdle:
    """Baseline: each call, in priority then arrival order, gets the nearest idle unit."""
    name = "closest-idle"

    def __init__(self):
        self.stats: dict = {}

    def __call__(self, state: DispatchState) -> list:
        free, out = set(range(len(state.idle))), []
        for j in call_order(state.calls):
            if not free:
                break
            u = _nearest(state, free, j)
            out.append((u, j))
            free.discard(u)
        return out


class CoverageSingle:
    """Classical coverage-aware rule in the spirit of Jagtenberg et al. (2017).

    Calls are handled one at a time. For a non-P1 call, among idle units that arrive within
    the threshold, send the one whose departure uncovers the least demand (ties: nearer unit).
    If no unit arrives within the threshold, send the nearest.
    """
    name = "coverage-single"

    def __init__(self):
        self.stats: dict = {}

    def __call__(self, state: DispatchState) -> list:
        free, out = set(range(len(state.idle))), []
        for j in call_order(state.calls):
            if not free:
                break
            if state.calls[j].priority == 1:
                u = _nearest(state, free, j)
            else:
                cand = [u for u in free if state.travel[u, j] <= state.cover_minutes]
                if not cand:
                    u = _nearest(state, free, j)
                else:
                    count = state.covers[sorted(free)].sum(0)
                    sole = count == 1
                    u = min(cand, key=lambda u: (state.zone_rate[state.covers[u] & sole].sum(), state.travel[u, j], u))
            out.append((u, j))
            free.discard(u)
        return out


@dataclass
class PairCoverStats:
    decisions: int = 0              # epochs where the batch model was solved
    multi_call: int = 0             # ... with two or more non-P1 calls at once
    differs_from_greedy: int = 0    # batch choice differed from closest-idle on the same state
    model_loss_mismatch: int = 0    # pairwise model loss != true coverage loss of the choice
    qubits: list = field(default_factory=list)   # (units x calls) per decision
    truncated: int = 0              # epochs where more than max_calls calls were pending
    eligibility_fallback: int = 0   # epochs where a unit beyond the threshold had to be used


class PairCover:
    """PairCover-Q: P1 calls get the nearest unit, then all remaining calls are assigned
    together by exactly minimising the pairwise-coverage objective (the epoch QUBO). As in the
    single-call rule, a unit is eligible for a call only if it arrives within the coverage
    threshold or is the nearest unit to that call.

    lam = 0 gives the coverage-free batch optimum, isolating what batching alone buys.
    """

    def __init__(self, lam: float = 20.0, tau: float = 20.0, allow_deferral: bool = False, max_calls: int = 6):
        self.lam, self.tau, self.allow_deferral, self.max_calls = lam, tau, allow_deferral, max_calls
        self.name = "paircover-q" if lam > 0 else "batch-no-coverage"
        self.stats = PairCoverStats()

    def __call__(self, state: DispatchState) -> list:
        free, out = set(range(len(state.idle))), []
        order = call_order(state.calls)
        for j in [j for j in order if state.calls[j].priority == 1]:
            if not free:
                return out
            u = _nearest(state, free, j)
            out.append((u, j))
            free.discard(u)
        rest = [j for j in order if state.calls[j].priority != 1]
        if not rest or not free:
            return out
        if len(rest) > self.max_calls:
            self.stats.truncated += 1
            rest = rest[: self.max_calls]
        units = sorted(free)
        sub_travel = state.travel[np.ix_(units, rest)]
        sub_covers = state.covers[units]
        weight = [state.calls[j].weight for j in rest]
        wait = [state.t - state.calls[j].t for j in rest]
        model = build_model(sub_travel, weight, wait, sub_covers, state.zone_rate, self.lam, self.tau,
                            max_travel=state.cover_minutes)
        assignment, _ = solve_exact(model, self.allow_deferral)

        st = self.stats
        st.decisions += 1
        st.multi_call += len(rest) >= 2
        st.qubits.append(len(units) * len(rest))
        greedy = set(_greedy_pairs(sub_travel, [state.calls[j] for j in rest]))
        st.differs_from_greedy += set(assignment) != greedy
        st.eligibility_fallback += not all(model.is_eligible(u, k) for u, k in assignment)
        sent = {u for u, _ in assignment}
        if abs(model_coverage_loss(model, sent) - true_coverage_loss(sub_covers, state.zone_rate, sent)) > 1e-9:
            st.model_loss_mismatch += 1

        return out + [(units[u], rest[k]) for u, k in assignment]


def _greedy_pairs(travel: np.ndarray, calls) -> list:
    free, out = set(range(travel.shape[0])), []
    for j in call_order(calls):
        if not free:
            break
        u = min(free, key=lambda u: (travel[u, j], u))
        out.append((u, j))
        free.discard(u)
    return out
