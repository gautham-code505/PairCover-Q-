def qubo_to_ising(h, J, num_vars):
    """
    Convert a QUBO into an Ising cost operator using the convention x_i = (1 - Z_i)/2.
    
    Returns:
        h_Z (list): Linear coefficients for Z_i operators.
        J_Z (dict): Quadratic coefficients for Z_i Z_j operators.
        offset (float): Constant offset.
    """
    h_Z = [0.0] * num_vars
    J_Z = {}
    offset = 0.0

    # Process linear terms: h_i * (1 - Z_i) / 2 = h_i / 2 - (h_i / 2) * Z_i
    for i in range(num_vars):
        h_Z[i] -= h[i] / 2.0
        offset += h[i] / 2.0

    # Process quadratic terms: J_{ij} * (1 - Z_i) / 2 * (1 - Z_j) / 2
    # = (J_{ij} / 4) * (1 - Z_i - Z_j + Z_i * Z_j)
    for (i, j), weight in J.items():
        w_4 = weight / 4.0
        offset += w_4
        h_Z[i] -= w_4
        h_Z[j] -= w_4
        J_Z[(i, j)] = w_4

    return h_Z, J_Z, offset

def calculate_ising_energy(z, h_Z, J_Z, offset):
    """
    Calculate the Ising energy for a given z spin state (values +1, -1).
    Energy = sum_i(h_Z_i * Z_i) + sum_{i<j}(J_Z_ij * Z_i * Z_j) + offset
    """
    energy = offset
    for i in range(len(h_Z)):
        energy += h_Z[i] * z[i]
    for (i, j), weight in J_Z.items():
        energy += weight * z[i] * z[j]
    return energy
