"""
Exact QAOA simulation for small QUBOs (up to ~16 qubits) with NumPy.

This computes exactly the state Qiskit's QAOAAnsatz produces (tests check amplitude
equality against qiskit.quantum_info.Statevector), but runs fast enough for the thousands
of optimisation runs a fair benchmark needs. Conventions match Qiskit:

- qubit k is bit k of the basis-state index (little-endian), and x_k = bit k;
- the cost layer is exp(-i * gamma * C) with C the scaled cost Hamiltonian;
- the mixer layer is RX(2 * beta) on every qubit, i.e. exp(-i * beta * X);
- the parameter vector is [beta_1..beta_p, gamma_1..gamma_p], as in QAOAAnsatz.

The cost Hamiltonian is the QUBO divided by `scale` (the largest absolute Ising
coefficient, as in the Round 1 audit). The QUBO and the Ising form differ only by a
constant, which is a global phase, so the two give the same state.
"""

from __future__ import annotations

import time

import numpy as np
from scipy.optimize import minimize

from qrescue.quantum.ising import qubo_to_ising


def bit_matrix(n: int) -> np.ndarray:
    """(2^n, n) array whose row i holds x_k = bit k of i."""
    idx = np.arange(2 ** n)
    return ((idx[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8)


def qubo_energies(h, J: dict, n: int) -> np.ndarray:
    """QUBO energy of every basis state, indexed like a Qiskit statevector."""
    x = bit_matrix(n).astype(float)
    e = x @ np.asarray(h, dtype=float)
    for (i, j), w in J.items():
        e += w * x[:, i] * x[:, j]
    return e


def ising_scale(h, J: dict, n: int) -> float:
    h_z, j_z, _ = qubo_to_ising(h, J, n)
    coeffs = [abs(c) for c in h_z if abs(c) > 1e-12] + [abs(c) for c in j_z.values() if abs(c) > 1e-12]
    return float(max(coeffs)) if coeffs else 1.0


def _apply_mixer(psi: np.ndarray, n: int, beta: float) -> np.ndarray:
    """exp(-i beta X) on every qubit, updating the state in place."""
    c, s = np.cos(beta), -1j * np.sin(beta)
    for k in range(n):
        v = psi.reshape(-1, 2, 2 ** k)      # middle axis is qubit k (little-endian index)
        a0 = v[:, 0, :].copy()
        v[:, 0, :] *= c
        v[:, 0, :] += s * v[:, 1, :]
        v[:, 1, :] *= c
        v[:, 1, :] += s * a0
    return psi


def qaoa_state(scaled_energies: np.ndarray, params) -> np.ndarray:
    params = np.asarray(params, dtype=float)
    p = len(params) // 2
    betas, gammas = params[:p], params[p:]
    dim = len(scaled_energies)
    n = int(round(np.log2(dim)))
    psi = np.full(dim, 1 / np.sqrt(dim), dtype=complex)
    for b, g in zip(betas, gammas):
        psi = psi * np.exp(-1j * g * scaled_energies)
        psi = _apply_mixer(psi, n, b)
    return psi


def linear_ramp(p: int, delta: float = 0.75) -> np.ndarray:
    """Annealing-like start: gamma grows and beta shrinks across layers."""
    k = (np.arange(p) + 0.5) / p
    return np.concatenate([(1 - k) * delta, k * delta])


def interp(params) -> np.ndarray:
    """INTERP initialisation (Zhou et al. 2020): depth-p optimum -> depth-(p+1) start."""
    params = np.asarray(params, dtype=float)
    p = len(params) // 2

    def grow(v):
        out = np.zeros(p + 1)
        for i in range(p + 1):
            left = v[i - 1] if i - 1 >= 0 else 0.0
            right = v[i] if i < p else 0.0
            out[i] = (i / p) * left + ((p - i) / p) * right
        return out

    return np.concatenate([grow(params[:p]), grow(params[p:])])


def optimize(energies: np.ndarray, scale: float, p: int, x0, maxiter: int = 500, rhobeg: float = 0.5) -> dict:
    """Minimise <H> (unscaled QUBO energy) over angles with COBYLA, exact expectation values."""
    scaled = energies / scale
    trace = []

    def f(theta):
        psi = qaoa_state(scaled, theta)
        v = float(np.real(np.vdot(psi, energies * psi)))
        trace.append(v)
        return v

    t0 = time.perf_counter()
    res = minimize(f, np.asarray(x0, dtype=float), method="COBYLA", options={"maxiter": maxiter, "rhobeg": rhobeg})
    probs = np.abs(qaoa_state(scaled, res.x)) ** 2
    return {"params": res.x, "expectation": float(res.fun), "nfev": int(res.nfev), "success": bool(res.success),
            "seconds": time.perf_counter() - t0, "probs": probs, "trace": trace}
