"""
Per-epoch PairCover-Q model: the same objective as the Round 1 QUBO, built from a
live simulation state instead of a hand-written scenario.

For idle units u and pending calls j at one decision epoch:

    F(x) = sum_(u,j) w_j * t_uj * x_uj                (weighted travel)
         + sum_j U_j * (1 - s_j)                       (unserved this epoch)
         + lam * [ sum_u c_u * D_u + sum_(a<b) g_ab * D_a * D_b ]   (coverage loss)

with D_u = sum_j x_uj, s_j = sum_u x_uj and U_j = w_j * (tau + wait_j), so a call that
has already waited longer is more expensive to leave unserved again.

Coverage terms come from zones' covering idle units: a zone covered by exactly one
idle unit contributes its demand rate to c_u, a zone covered by exactly two contributes
to g_ab. Zones covered by three or more idle units are left out, because they lose
coverage only if three or more of their units leave in the same epoch; the simulation
counts how often that actually happens.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, replace

import numpy as np


@dataclass
class EpochModel:
    travel: np.ndarray        # (U, C) minutes from idle unit u to call j
    weight: np.ndarray        # (C,) priority weights w_j
    unserved: np.ndarray      # (C,) U_j
    c: np.ndarray             # (U,) single-cover demand per unit (calls / hour)
    g: dict                   # {(a, b): demand covered only by the pair a < b}
    lam: float
    eligible: np.ndarray | None = None   # (U, C) bool; None = every pair eligible

    def is_eligible(self, u: int, j: int) -> bool:
        return True if self.eligible is None else bool(self.eligible[u, j])

    @property
    def n_units(self) -> int:
        return self.travel.shape[0]

    @property
    def n_calls(self) -> int:
        return self.travel.shape[1]


def coverage_terms(covers: np.ndarray, zone_rate: np.ndarray) -> tuple[np.ndarray, dict]:
    """covers: (U, Z) bool, idle unit u reaches zone z within the threshold."""
    n_units = covers.shape[0]
    c = np.zeros(n_units)
    g: dict = {}
    count = covers.sum(0)
    for z in np.flatnonzero(count == 1):
        c[np.flatnonzero(covers[:, z])[0]] += zone_rate[z]
    for z in np.flatnonzero(count == 2):
        a, b = np.flatnonzero(covers[:, z])
        g[(a, b)] = g.get((a, b), 0.0) + zone_rate[z]
    return c, g


def build_model(travel, weight, wait, covers, zone_rate, lam, tau, max_travel=None) -> EpochModel:
    """max_travel: a unit is eligible for a call if it arrives within max_travel minutes
    or is the nearest unit to that call (so every call keeps at least one option)."""
    travel = np.asarray(travel, dtype=float)
    weight = np.asarray(weight, dtype=float)
    unserved = weight * (tau + np.asarray(wait, dtype=float))
    c, g = coverage_terms(covers, zone_rate)
    eligible = None
    if max_travel is not None:
        eligible = travel <= max_travel
        eligible[np.argmin(travel, axis=0), np.arange(travel.shape[1])] = True
    return EpochModel(travel, weight, unserved, c, g, lam, eligible)


def model_coverage_loss(model: EpochModel, units: set) -> float:
    loss = sum(model.c[u] for u in units)
    loss += sum(v for (a, b), v in model.g.items() if a in units and b in units)
    return float(loss)


def true_coverage_loss(covers: np.ndarray, zone_rate: np.ndarray, units: set) -> float:
    """Demand rate of zones that had a covering idle unit and have none after dispatch."""
    before = covers.any(0)
    keep = [u for u in range(covers.shape[0]) if u not in units]
    after = covers[keep].any(0) if keep else np.zeros_like(before)
    return float(zone_rate[before & ~after].sum())


def objective(model: EpochModel, assignment) -> float:
    """F(x) for a list of (unit, call) pairs; inf if it breaks one-to-one."""
    units = [u for u, _ in assignment]
    calls = [j for _, j in assignment]
    if len(set(units)) < len(units) or len(set(calls)) < len(calls):
        return float("inf")
    if not all(model.is_eligible(u, j) for u, j in assignment):
        return float("inf")
    served = set(calls)
    cost = sum(model.weight[j] * model.travel[u, j] for u, j in assignment)
    cost += sum(model.unserved[j] for j in range(model.n_calls) if j not in served)
    return float(cost + model.lam * model_coverage_loss(model, set(units)))


def solve_exact(model: EpochModel, allow_deferral: bool = False):
    """Exact minimiser by enumeration of one-to-one assignments.

    With allow_deferral=False only maximum-size assignments are considered, so no call is
    left waiting while an ambulance is idle; coverage then decides *which* units go. If the
    eligible pairs cannot serve that many calls, all pairs are allowed for that epoch (a far
    unit is better than a call waiting next to an idle ambulance).
    Returns (assignment, objective).
    """
    k_max = min(model.n_units, model.n_calls)
    if allow_deferral:
        return _best(model, range(0, k_max + 1))
    best, cost = _best(model, [k_max])
    if cost == float("inf") and model.eligible is not None:
        best, cost = _best(replace(model, eligible=None), [k_max])
    return best, cost


def _best(model: EpochModel, sizes):
    best, best_cost = [], float("inf")
    for k in sizes:
        for calls in itertools.combinations(range(model.n_calls), k):
            for units in itertools.permutations(range(model.n_units), k):
                assignment = list(zip(units, calls))
                cost = objective(model, assignment)
                if cost < best_cost - 1e-9:
                    best, best_cost = assignment, cost
    return best, best_cost


# --------------------------------------------------------------------------- #
# QUBO form of the same epoch problem (what QAOA would sample)
# --------------------------------------------------------------------------- #

def epoch_qubo(model: EpochModel, penalty: float | None = None):
    """QUBO over eligible variables (u, j) ordered by unit then call: H(x) = h.x + sum J_kl x_k x_l.
    Ineligible pairs get no variable at all, so no sample can represent them.

    On one-to-one assignments F(x) = H(x) + sum_j U_j. The default penalty is just above
    the provable bound max_(u,j) (U_j - w_j t_uj), which makes every QUBO minimiser feasible.
    """
    variables = [(u, j) for u in range(model.n_units) for j in range(model.n_calls) if model.is_eligible(u, j)]
    if penalty is None:
        gain = max((model.unserved[j] - model.weight[j] * model.travel[u, j] for u, j in variables), default=0.0)
        penalty = max(gain, 0.0) + 1.0
    h = [float(model.weight[j] * model.travel[u, j] - model.unserved[j] + model.lam * model.c[u]) for u, j in variables]
    J: dict = {}
    for k, (a, j) in enumerate(variables):
        for l in range(k + 1, len(variables)):
            b, m = variables[l]
            w = 0.0
            if a == b:
                w += penalty
            else:
                w += model.lam * model.g.get((min(a, b), max(a, b)), 0.0)
                if j == m:
                    w += penalty
            if w:
                J[(k, l)] = w
    return variables, h, J, float(model.unserved.sum()), penalty
