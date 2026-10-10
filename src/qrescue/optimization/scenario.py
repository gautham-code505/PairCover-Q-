"""
Synthetic 5-qubit ambulance assignment scenario.
Ambulances: A1, A2
Calls: C1, C2, C3

Eligible variables and fixed ordering:
x0 = A1-C1
x1 = A1-C2
x2 = A1-C3
x3 = A2-C2
x4 = A2-C3

Ineligible: A2-C1
"""

VARIABLES = [
    ('A1', 'C1'), # x0
    ('A1', 'C2'), # x1
    ('A1', 'C3'), # x2
    ('A2', 'C2'), # x3
    ('A2', 'C3')  # x4
]

PRIORITY_WEIGHTS = {'C1': 3, 'C2': 2, 'C3': 1}
UNSERVED_TIME = 20

TRAVEL_TIMES = {
    ('A1', 'C1'): 5,
    ('A1', 'C2'): 8,
    ('A1', 'C3'): 6,
    ('A2', 'C2'): 4,
    ('A2', 'C3'): 9
}

COVERAGE_PARAMS = {
    'A1': 0.5,
    'A2': 0.4,
    ('A1', 'A2'): 1.0
}
LAMBDA_COVERAGE = 10
ASSIGNMENT_PENALTY = 50

# Pre-computed expected values from the research specification
EXPECTED_H = [-40, -19, -9, -28, -7]
EXPECTED_J = {
    (0, 1): 50, (0, 2): 50, (1, 2): 50, (3, 4): 50, # One ambulance, multiple calls
    (1, 3): 60, (2, 4): 60,                         # Multiple ambulances, same call
    (0, 3): 10, (0, 4): 10, (1, 4): 10, (2, 3): 10  # Cross-terms (both dispatched)
}
EXPECTED_QUBO_ENERGY = -58
EXPECTED_RAW_F = 62
EXPECTED_OFFSET = 120
EXPECTED_PENALTY_BOUND_LOWER = 45

def generate_qubo_scenario1(
    variables=VARIABLES,
    priority_weights=PRIORITY_WEIGHTS,
    unserved_time=UNSERVED_TIME,
    travel_times=TRAVEL_TIMES,
    coverage_params=COVERAGE_PARAMS,
    lambda_coverage=LAMBDA_COVERAGE,
    assignment_penalty=ASSIGNMENT_PENALTY
):
    """
    Derive Scenario 1 QUBO coefficients dynamically from scenario data.
    """
    num_vars = len(variables)
    h = [0.0] * num_vars
    J = {}
    
    # Linear coefficients: saving + single coverage penalty
    for i, (amb, call) in enumerate(variables):
        saving = priority_weights[call] * (unserved_time - travel_times[(amb, call)])
        single_cov = lambda_coverage * coverage_params.get(amb, 0.0)
        h[i] = -saving + single_cov
        
    # Quadratic couplings
    for i in range(num_vars):
        for j in range(i + 1, num_vars):
            amb_i, call_i = variables[i]
            amb_j, call_j = variables[j]
            
            # Same ambulance
            if amb_i == amb_j:
                J[(i, j)] = J.get((i, j), 0) + assignment_penalty
                
            # Same call
            if call_i == call_j:
                J[(i, j)] = J.get((i, j), 0) + assignment_penalty
                
            # Mutual coverage interaction (both dispatched)
            if amb_i != amb_j:
                pair_key = (amb_i, amb_j) if (amb_i, amb_j) in coverage_params else (amb_j, amb_i)
                if pair_key in coverage_params:
                    pair_cov = coverage_params[pair_key]
                    J[(i, j)] = J.get((i, j), 0) + int(lambda_coverage * pair_cov)
                    
    return h, J

