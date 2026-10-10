import pytest
from qrescue.optimization.scenario import (
    EXPECTED_H, EXPECTED_J, EXPECTED_QUBO_ENERGY, EXPECTED_RAW_F, EXPECTED_OFFSET
)
from qrescue.optimization.brute_force import generate_all_bitstrings
from qrescue.optimization.qubo import get_scenario_qubo, calculate_qubo_energy
from qrescue.validation.validator import is_feasible, decode_assignment
from qrescue.quantum.ising import qubo_to_ising, calculate_ising_energy

def test_bitstrings_and_feasible_assignments():
    bitstrings = generate_all_bitstrings(5)
    assert len(bitstrings) == 32, "Total bitstrings must be 32"
    
    feasible_count = sum(1 for x in bitstrings if is_feasible(x))
    assert feasible_count == 10, "Expected exactly 10 feasible assignments"

def test_best_feasible_assignment():
    bitstrings = generate_all_bitstrings(5)
    h, J = get_scenario_qubo()
    
    best_energy = float('inf')
    best_x = None
    
    for x in bitstrings:
        if is_feasible(x):
            energy = calculate_qubo_energy(x, h, J)
            if energy < best_energy:
                best_energy = energy
                best_x = x
                
    # Best assignment should be A1-C1 and A2-C2
    assignments = decode_assignment(best_x)
    assert ('A1', 'C1') in assignments, "Best assignment must include A1-C1"
    assert ('A2', 'C2') in assignments, "Best assignment must include A2-C2"
    assert len(assignments) == 2, "Best assignment must have exactly 2 assignments"
    
    assert best_energy == EXPECTED_QUBO_ENERGY, f"Expected QUBO energy {EXPECTED_QUBO_ENERGY}, got {best_energy}"
    assert best_energy + EXPECTED_OFFSET == EXPECTED_RAW_F, "Raw objective F = H + 120 mismatch"

def test_qubo_coefficients():
    h, J = get_scenario_qubo()
    assert h == EXPECTED_H, "Linear QUBO coefficients mismatch"
    assert J == EXPECTED_J, "Quadratic QUBO coefficients mismatch"

def test_ising_energy_equivalence():
    h, J = get_scenario_qubo()
    h_Z, J_Z, offset = qubo_to_ising(h, J, 5)
    
    bitstrings = generate_all_bitstrings(5)
    for x in bitstrings:
        qubo_energy = calculate_qubo_energy(x, h, J)
        # Convert x (0,1) to z (+1, -1) using x = (1-z)/2 => z = 1 - 2x
        z = [1 - 2 * xi for xi in x]
        ising_energy = calculate_ising_energy(z, h_Z, J_Z, offset)
        assert abs(qubo_energy - ising_energy) < 1e-9, f"Energy mismatch for x={x}: QUBO={qubo_energy}, Ising={ising_energy}"

def test_scenario1_dynamic_derivation():
    from qrescue.optimization.scenario import generate_qubo_scenario1
    derived_h, derived_J = generate_qubo_scenario1()
    assert derived_h == EXPECTED_H, f"Derived h={derived_h} != EXPECTED_H={EXPECTED_H}"
    assert derived_J == EXPECTED_J, f"Derived J={derived_J} != EXPECTED_J={EXPECTED_J}"

