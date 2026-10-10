def calculate_qubo_energy(x, h, J):
    """
    Calculate the QUBO energy for a given bitstring x.
    Energy = sum_i(h_i * x_i) + sum_{i<j}(J_{ij} * x_i * x_j)
    """
    energy = 0.0
    for i in range(len(h)):
        energy += h[i] * x[i]
    for (i, j), weight in J.items():
        energy += weight * x[i] * x[j]
    return energy

def get_scenario_qubo():
    """
    Build the QUBO energy function using the coefficients from the synthetic scenario.
    """
    from qrescue.optimization.scenario import EXPECTED_H, EXPECTED_J
    return EXPECTED_H, EXPECTED_J
