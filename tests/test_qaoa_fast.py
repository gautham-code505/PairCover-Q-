import numpy as np
import pytest
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector

from qrescue.optimization.qubo import calculate_qubo_energy
from qrescue.optimization.scenario2 import generate_qubo_scenario2
from qrescue.quantum.ising import qubo_to_ising
from qrescue.quantum.qaoa_fast import (
    bit_matrix,
    interp,
    ising_scale,
    linear_ramp,
    optimize,
    qaoa_state,
    qubo_energies,
)


def _qiskit_op(h, J, n, scale):
    h_z, j_z, _ = qubo_to_ising(h, J, n)
    labels, coeffs = [], []
    for i, c in enumerate(h_z):
        if abs(c) > 1e-12:
            s = ["I"] * n; s[i] = "Z"
            labels.append("".join(reversed(s))); coeffs.append(c / scale)
    for (i, j), c in j_z.items():
        if abs(c) > 1e-12:
            s = ["I"] * n; s[i] = "Z"; s[j] = "Z"
            labels.append("".join(reversed(s))); coeffs.append(c / scale)
    return SparsePauliOp(labels, coeffs)


def test_energies_follow_qiskit_bit_order():
    h, J = generate_qubo_scenario2()
    e = qubo_energies(h, J, 6)
    x = bit_matrix(6)
    for i in (0, 1, 5, 33, 63):
        assert e[i] == pytest.approx(calculate_qubo_energy(list(x[i]), h, J))
    # basis index 0b100001 (Qiskit key '100001') is x0 = x5 = 1: A1->C2, A3->C3, the Round 1 optimum
    assert e[0b100001] == pytest.approx(e.min())


@pytest.mark.parametrize("p", [1, 2, 3])
def test_state_matches_qiskit_qaoa_ansatz(p):
    h, J = generate_qubo_scenario2()
    scale = ising_scale(h, J, 6)
    params = np.random.default_rng(p).uniform(0, 2, 2 * p)
    ansatz = QAOAAnsatz(_qiskit_op(h, J, 6, scale), reps=p)
    ref = Statevector(ansatz.assign_parameters(params)).data
    mine = qaoa_state(qubo_energies(h, J, 6) / scale, params)
    assert abs(np.vdot(ref, mine)) == pytest.approx(1.0, abs=1e-9)    # equal up to global phase


def test_round1_audit_result_is_reproduced():
    # Round 1 audit: p=1, seed 10, COBYLA rhobeg 0.5 -> 6.47% optimum probability, 73.41% feasible.
    h, J = generate_qubo_scenario2()
    scale = ising_scale(h, J, 6)
    np.random.seed(10)
    x0 = np.concatenate([np.random.uniform(0, np.pi, 1), np.random.uniform(0, 2 * np.pi, 1)])
    res = optimize(qubo_energies(h, J, 6), scale, 1, x0, maxiter=200)
    assert res["probs"][0b100001] == pytest.approx(0.0647, abs=5e-4)


def test_interp_and_ramp_shapes():
    assert linear_ramp(3).shape == (6,)
    grown = interp(np.array([0.3, 0.6]))
    assert grown.shape == (4,)
    assert grown[0] == pytest.approx(0.3) and grown[2] == pytest.approx(0.6)


def test_probabilities_normalised_for_larger_instance():
    rng = np.random.default_rng(0)
    n = 10
    h = rng.normal(size=n)
    J = {(i, j): rng.normal() for i in range(n) for j in range(i + 1, n) if rng.uniform() < 0.3}
    psi = qaoa_state(qubo_energies(h, J, n), linear_ramp(2))
    assert np.sum(np.abs(psi) ** 2) == pytest.approx(1.0)
