import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import minimize
from qrescue.optimization.qubo import get_scenario_qubo
from qrescue.quantum.ising import qubo_to_ising

def test_bit_ordering():
    """
    Verify bit ordering with a basis-state test.
    Qiskit uses little-endian ordering. We want to ensure we map bits correctly.
    """
    qc = QuantumCircuit(5)
    # Apply X to qubit 0
    qc.x(0)
    qc.measure_all()
    
    simulator = AerSimulator()
    result = simulator.run(qc, shots=100).result()
    counts = result.get_counts()
    
    # In Qiskit, bitstring is printed as q4 q3 q2 q1 q0.
    # So X on qubit 0 should yield '00001'.
    assert '00001' in counts
    assert counts['00001'] == 100

def test_qaoa_smoke():
    """
    A small QAOA p=1 smoke test. 
    Ensure it runs with a supported ansatz and simulator without claiming quantum advantage.
    """
    h, J = get_scenario_qubo()
    h_Z, J_Z, offset = qubo_to_ising(h, J, 5)
    
    # Build Pauli Operator for Ising Hamiltonian
    paulis = []
    coeffs = []
    
    for i in range(5):
        if abs(h_Z[i]) > 1e-9:
            pauli_str = ['I'] * 5
            pauli_str[i] = 'Z'
            # Reverse for Qiskit's little-endian convention
            paulis.append("".join(reversed(pauli_str)))
            coeffs.append(h_Z[i])
            
    for (i, j), weight in J_Z.items():
        if abs(weight) > 1e-9:
            pauli_str = ['I'] * 5
            pauli_str[i] = 'Z'
            pauli_str[j] = 'Z'
            paulis.append("".join(reversed(pauli_str)))
            coeffs.append(weight)
            
    hamiltonian = SparsePauliOp(paulis, coeffs)
    ansatz = QAOAAnsatz(hamiltonian, reps=1)
    
    # Just run the circuit to ensure it compiles and simulates.
    from qiskit import transpile
    bound_circ = ansatz.assign_parameters([0.1, 0.2])
    bound_circ.measure_all()
    simulator = AerSimulator()
    bound_circ = transpile(bound_circ, simulator)
    result = simulator.run(bound_circ, shots=10).result()
    counts = result.get_counts()
    
    assert len(counts) > 0, "QAOA circuit should produce measurement outcomes."
    # Record optimizer, seed, depth, sampling settings
    metadata = {
        "optimizer": "COBYLA (mock)",
        "seed": 42,
        "depth": bound_circ.depth(),
        "shots": 10
    }
    assert metadata["depth"] > 0
