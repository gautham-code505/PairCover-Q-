import pytest
import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qrescue.optimization.brute_force import generate_all_bitstrings
from qrescue.optimization.qubo import calculate_qubo_energy
from qrescue.optimization.scenario2 import (
    generate_qubo_scenario2, 
    calc_raw_objective, 
    VARIABLES_2,
    LAMBDA_COVERAGE_2,
    ASSIGNMENT_PENALTY_2
)
from qrescue.quantum.ising import qubo_to_ising, calculate_ising_energy
from qrescue.validation.validator import is_feasible, decode_qiskit_bitstring

def test_scenario2_coefficients():
    h, J = generate_qubo_scenario2()
    
    expected_h = [-32, -14, -30, -16, -16, -15]
    assert h == expected_h, f"Expected h={expected_h}, got {h}"
    
    # 40 on: (0,1), (2,3), (4,5), (0,4), (2,4), (1,5), (3,5)
    for pair in [(0,1), (2,3), (4,5), (0,4), (2,4), (1,5), (3,5)]:
        assert J.get(pair, 0) == 40, f"Expected 40 for pair {pair}"
        
    # 50 on: (0,2), (1,3)
    for pair in [(0,2), (1,3)]:
        assert J.get(pair, 0) == 50, f"Expected 50 for pair {pair}"
        
    # 10 on: (0,3), (1,2)
    for pair in [(0,3), (1,2)]:
        assert J.get(pair, 0) == 10, f"Expected 10 for pair {pair}"
        
    # Check all remaining are 0
    all_specified = [(0,1), (2,3), (4,5), (0,4), (2,4), (1,5), (3,5), (0,2), (1,3), (0,3), (1,2)]
    for i in range(6):
        for j in range(i+1, 6):
            if (i, j) not in all_specified:
                assert J.get((i, j), 0) == 0, f"Expected 0 for pair {(i,j)}"

def test_exhaustive_scenario2():
    bitstrings = generate_all_bitstrings(6)
    assert len(bitstrings) == 64, "Total bitstrings must be 64"
    
    best_cost_no_cov = float('inf')
    best_x_no_cov = None
    
    best_cost_cov = float('inf')
    best_x_cov = None
    
    for x in bitstrings:
        cost_no = calc_raw_objective(x, include_coverage=False)
        if cost_no < best_cost_no_cov:
            best_cost_no_cov = cost_no
            best_x_no_cov = x
            
        cost_cov = calc_raw_objective(x, include_coverage=True)
        if cost_cov < best_cost_cov:
            best_cost_cov = cost_cov
            best_x_cov = x
            
    # 1. Without coverage, optimum is A1->C2, A2->C3, cost 12
    assign_no_cov = [VARIABLES_2[i] for i, val in enumerate(best_x_no_cov) if val == 1]
    assert ('A1', 'C2') in assign_no_cov
    assert ('A2', 'C3') in assign_no_cov
    assert best_cost_no_cov == 12
    
    # 2. With coverage, optimum is A1->C2, A3->C3, cost 13
    assign_cov = [VARIABLES_2[i] for i, val in enumerate(best_x_cov) if val == 1]
    assert ('A1', 'C2') in assign_cov
    assert ('A3', 'C3') in assign_cov
    assert best_cost_cov == 13
    
    # 3. Every call is served
    calls_served = [c for a, c in assign_cov]
    assert 'C2' in calls_served
    assert 'C3' in calls_served

def test_scenario2_feasible_count():
    """Verify Scenario 2 has 64 binary strings and exactly 13 feasible assignments."""
    bitstrings = generate_all_bitstrings(6)
    assert len(bitstrings) == 64
    
    feasible_from_raw = [x for x in bitstrings if calc_raw_objective(x, include_coverage=True) != float('inf')]
    feasible_from_validator = [x for x in bitstrings if is_feasible(x, VARIABLES_2)]
    
    assert len(feasible_from_raw) == 13, f"Expected 13 feasible assignments, got {len(feasible_from_raw)}"
    assert len(feasible_from_validator) == 13, f"Validator expected 13, got {len(feasible_from_validator)}"
    assert feasible_from_raw == feasible_from_validator

def test_scenario2_qubo_energy_raw_equivalence_on_feasible():
    """Verify QUBO energy + 60 equals the raw-data objective on all feasible assignments."""
    h, J = generate_qubo_scenario2()
    bitstrings = generate_all_bitstrings(6)
    feasible = [x for x in bitstrings if is_feasible(x, VARIABLES_2)]
    
    for x in feasible:
        qubo_energy = calculate_qubo_energy(x, h, J)
        raw_f = calc_raw_objective(x, include_coverage=True)
        assert abs((qubo_energy + 60) - raw_f) < 1e-9, f"Mismatch for feasible state {x}: H+60={qubo_energy+60}, F={raw_f}"

def test_scenario2_global_qubo_minimum():
    """Verify the global QUBO minimum over ALL 64 states is feasible, equals x=(1,0,0,0,0,1), H=-47, F=13."""
    h, J = generate_qubo_scenario2()
    bitstrings = generate_all_bitstrings(6)
    
    min_energy = float('inf')
    best_x = None
    
    for x in bitstrings:
        e = calculate_qubo_energy(x, h, J)
        if e < min_energy:
            min_energy = e
            best_x = x
            
    assert tuple(best_x) == (1, 0, 0, 0, 0, 1), f"Expected optimal bitstring (1,0,0,0,0,1), got {best_x}"
    assert is_feasible(best_x, VARIABLES_2), "Global QUBO minimum must be feasible"
    assert min_energy == -47, f"Expected global QUBO minimum -47, got {min_energy}"
    assert calc_raw_objective(best_x, include_coverage=True) == 13, "Expected raw objective F=13"

def test_scenario2_ising_qubo_equivalence():
    """Verify Ising energy plus constant offset matches QUBO energy for all 64 bitstrings."""
    h, J = generate_qubo_scenario2()
    h_Z, J_Z, offset = qubo_to_ising(h, J, 6)
    bitstrings = generate_all_bitstrings(6)
    
    for x in bitstrings:
        qubo_e = calculate_qubo_energy(x, h, J)
        z = [1 - 2 * b for b in x]
        ising_e = calculate_ising_energy(z, h_Z, J_Z, offset)
        assert abs(qubo_e - ising_e) < 1e-9, f"Ising mismatch for {x}: QUBO={qubo_e}, Ising={ising_e}"

def test_scenario2_pauli_operator_diagonal_agreement():
    """Verify the actual Pauli operator's diagonal energies agree with QUBO energies for all 64 basis states."""
    h, J = generate_qubo_scenario2()
    h_Z, J_Z, offset = qubo_to_ising(h, J, 6)
    
    paulis = []
    coeffs = []
    for i in range(6):
        if abs(h_Z[i]) > 1e-9:
            pauli_str = ['I'] * 6
            pauli_str[i] = 'Z'
            paulis.append("".join(reversed(pauli_str)))
            coeffs.append(h_Z[i])
            
    for (i, j), weight in J_Z.items():
        if abs(weight) > 1e-9:
            pauli_str = ['I'] * 6
            pauli_str[i] = 'Z'
            pauli_str[j] = 'Z'
            paulis.append("".join(reversed(pauli_str)))
            coeffs.append(weight)
            
    hamiltonian = SparsePauliOp(paulis, coeffs)
    mat = hamiltonian.to_matrix()
    
    # In Qiskit, basis state |k> corresponds to bitstring key s = format(k, '06b')
    # and variable x_i = int(s[5 - i]).
    for k in range(64):
        bitstr = format(k, '06b')
        x = [int(bitstr[5 - i]) for i in range(6)]
        expected_qubo_e = calculate_qubo_energy(x, h, J)
        pauli_diag_e = mat[k, k].real + offset
        assert abs(expected_qubo_e - pauli_diag_e) < 1e-9, (
            f"Pauli diagonal mismatch for basis {k} ({bitstr}, x={x}): "
            f"QUBO={expected_qubo_e}, Pauli+offset={pauli_diag_e}"
        )

def test_non_palindromic_bit_order_decoder():
    """Verify the decoder passes a non-palindromic bit-order test."""
    # State with ONLY x0 = 1 (A1 -> C2): x = [1, 0, 0, 0, 0, 0]
    # In Qiskit little-endian: q5 q4 q3 q2 q1 q0 -> '000001'
    x, assignments = decode_qiskit_bitstring('000001', VARIABLES_2)
    assert x == [1, 0, 0, 0, 0, 0], f"Expected [1,0,0,0,0,0], got {x}"
    assert assignments == [('A1', 'C2')], f"Expected [('A1', 'C2')], got {assignments}"
    assert assignments != [('A3', 'C3')], "Unreversed bitstring would erroneously decode to ('A3', 'C3')"
    
    # State with x0=1 and x4=1: x = [1, 0, 0, 0, 1, 0]
    # In Qiskit: '010001'
    x2, assignments2 = decode_qiskit_bitstring('010001', VARIABLES_2)
    assert x2 == [1, 0, 0, 0, 1, 0]
    assert ('A1', 'C2') in assignments2
    assert ('A3', 'C2') in assignments2

def test_zero_coverage_cost_case():
    """Verify zero-coverage-cost case agrees with the exact coverage-free assignment optimum."""
    h_nocov, J_nocov = generate_qubo_scenario2(lambda_coverage=0)
    bitstrings = generate_all_bitstrings(6)
    
    min_energy = float('inf')
    best_x = None
    for x in bitstrings:
        e = calculate_qubo_energy(x, h_nocov, J_nocov)
        if e < min_energy:
            min_energy = e
            best_x = x
            
    # Optimum without coverage is A1->C2, A2->C3 (cost 12, H = -48)
    assert tuple(best_x) == (1, 0, 0, 1, 0, 0)
    assert min_energy == -48
    assert min_energy + 60 == 12
    assert calc_raw_objective(best_x, include_coverage=False) == 12

def test_scenario2_dynamic_parameters():
    """Verify scenario generation parameters (including lambda and penalty) are dynamically used."""
    h_std, J_std = generate_qubo_scenario2(lambda_coverage=10, assignment_penalty=40)
    h_high, J_high = generate_qubo_scenario2(lambda_coverage=20, assignment_penalty=50)
    
    # Couplings on (0,3) should reflect lambda_coverage: 10 vs 20
    assert J_std[(0, 3)] == 10
    assert J_high[(0, 3)] == 20
    
    # Couplings on same ambulance (0,1) should reflect assignment_penalty: 40 vs 50
    assert J_std[(0, 1)] == 40
    assert J_high[(0, 1)] == 50
    
    # Raw objective should scale with lambda_coverage
    x_both = [1, 0, 0, 1, 0, 0]  # Both A1 and A2 dispatched
    cost_std = calc_raw_objective(x_both, include_coverage=True, lambda_coverage=10)
    cost_high = calc_raw_objective(x_both, include_coverage=True, lambda_coverage=20)
    assert cost_std == 22
    assert cost_high == 32
