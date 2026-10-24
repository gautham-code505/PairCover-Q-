"""
QAOA as the per-epoch solver inside the rolling simulation ("QAOA in the loop").

At each decision the solver builds the epoch QUBO, optimises a depth-p QAOA circuit
(linear-ramp start, INTERP warm start between depths, exact expectation values), draws
`shots` samples and keeps the best sample that passes independent validation against the
raw tables: one-to-one, eligible pairs only, and serving as many calls as the eligible pairs
allow (the simulation's no-deferral rule). If no sample passes, the exact solver's answer
is used and the fallback is counted. Nothing is repaired.

For every decision the same validation is also applied to `shots` uniform-random bitstrings
and to the single most probable QAOA bitstring, so the report can show whether QAOA adds
anything over random sampling at these sizes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linear_sum_assignment

from qrescue.quantum.qaoa_fast import interp, ising_scale, linear_ramp, optimize, qubo_energies
from qrescue.simulation.paircover import EpochModel, epoch_qubo, objective, solve_exact


@dataclass
class LoopStats:
    decisions: int = 0
    trivial: int = 0                 # 0 or 1 QUBO variables: nothing to optimise
    too_large: int = 0               # above max_qubits, solved exactly
    outside_qubo: int = 0            # decision needed a unit beyond the threshold (not in the QUBO)
    qaoa_runs: int = 0
    qaoa_agrees: int = 0             # best valid QAOA sample is an exact optimum
    qaoa_fallback: int = 0           # no valid QAOA sample, exact answer used
    argmax_agrees: int = 0           # most probable bitstring alone is an exact optimum
    random_agrees: int = 0           # best valid uniform-random sample is an exact optimum
    random_fallback: int = 0
    qubits: list = field(default_factory=list)
    p_opt: list = field(default_factory=list)       # exact P(optimum) of the optimised circuit
    random_p_opt: list = field(default_factory=list)


def max_matching_size(model: EpochModel) -> int:
    if model.eligible is None:
        return min(model.n_units, model.n_calls)
    rows, cols = linear_sum_assignment(-model.eligible.astype(int))
    return int(model.eligible[rows, cols].sum())


class QAOASolver:
    """Drop-in replacement for solve_exact in PairCover(solver=...)."""

    def __init__(self, p: int = 2, shots: int = 1024, max_qubits: int = 14, seed: int = 0):
        self.p, self.shots, self.max_qubits = p, shots, max_qubits
        self.rng = np.random.default_rng(seed)
        self.stats = LoopStats()

    def _best_valid(self, samples, variables, model, k_req):
        best, best_cost = None, float("inf")
        for idx in np.unique(samples):
            pairs = [variables[k] for k in range(len(variables)) if (int(idx) >> k) & 1]
            if len(pairs) != k_req:
                continue
            cost = objective(model, pairs)
            if cost < best_cost:
                best, best_cost = pairs, cost
        return best, best_cost

    def __call__(self, model: EpochModel, allow_deferral: bool = False):
        st = self.stats
        st.decisions += 1
        exact, exact_cost = solve_exact(model, allow_deferral)
        variables, h, J, const, _ = epoch_qubo(model)
        n = len(variables)
        k_req = max_matching_size(model)
        if allow_deferral:
            return exact, exact_cost
        if len(exact) > k_req:
            st.outside_qubo += 1              # the decision needs an ineligible unit: outside the QUBO
            return exact, exact_cost
        if n <= 1:
            st.trivial += 1
            return exact, exact_cost
        if n > self.max_qubits:
            st.too_large += 1
            return exact, exact_cost
        st.qaoa_runs += 1
        st.qubits.append(n)
        energies = qubo_energies(h, J, n)
        scale = ising_scale(h, J, n)
        params, probs = None, None
        for depth in range(1, self.p + 1):
            r = optimize(energies, scale, depth, linear_ramp(depth) if params is None else interp(params), maxiter=300)
            params, probs = r["params"], r["probs"]
        is_opt = np.array([abs(objective(model, [variables[k] for k in range(n) if (i >> k) & 1]) - exact_cost) < 1e-6
                           for i in range(2 ** n)])
        st.p_opt.append(float(probs[is_opt].sum()))
        st.random_p_opt.append(float(is_opt.mean()))
        st.argmax_agrees += bool(is_opt[int(np.argmax(probs))])

        rand_best, rand_cost = self._best_valid(self.rng.integers(0, 2 ** n, self.shots), variables, model, k_req)
        if rand_best is None:
            st.random_fallback += 1
        elif abs(rand_cost - exact_cost) < 1e-6:
            st.random_agrees += 1

        best, cost = self._best_valid(self.rng.choice(2 ** n, size=self.shots, p=probs / probs.sum()), variables, model, k_req)
        if best is None:
            st.qaoa_fallback += 1
            return exact, exact_cost
        if abs(cost - exact_cost) < 1e-6:
            st.qaoa_agrees += 1
        return best, cost
