"""
PairCover-Q demonstration scenario (Scenario 2).
Ambulances: A1, A2, A3
Calls: C2, C3

Variables:
x0 = A1-C2
x1 = A1-C3
x2 = A2-C2
x3 = A2-C3
x4 = A3-C2
x5 = A3-C3
"""

VARIABLES_2 = [
    ('A1', 'C2'), # x0
    ('A1', 'C3'), # x1
    ('A2', 'C2'), # x2
    ('A2', 'C3'), # x3
    ('A3', 'C2'), # x4
    ('A3', 'C3')  # x5
]

PRIORITY_WEIGHTS_2 = {'C2': 2, 'C3': 1}
UNSERVED_TIME_2 = 20

TRAVEL_TIMES_2 = {
    ('A1', 'C2'): 4,
    ('A1', 'C3'): 6,
    ('A2', 'C2'): 5,
    ('A2', 'C3'): 4,
    ('A3', 'C2'): 12,
    ('A3', 'C3'): 5
}

LAMBDA_COVERAGE_2 = 10
SHARED_DEMAND_2 = 1.0
ASSIGNMENT_PENALTY_2 = 40

def generate_qubo_scenario2(
    variables=VARIABLES_2,
    priority_weights=PRIORITY_WEIGHTS_2,
    unserved_time=UNSERVED_TIME_2,
    travel_times=TRAVEL_TIMES_2,
    lambda_coverage=LAMBDA_COVERAGE_2,
    shared_demand=SHARED_DEMAND_2,
    assignment_penalty=ASSIGNMENT_PENALTY_2
):
    """Derive QUBO coefficients directly from scenario data."""
    num_vars = len(variables)
    h = [0.0] * num_vars
    J = {}
    coverage_penalty = int(lambda_coverage * shared_demand)
    
    # Linear coefficients: saving 
    for i, (amb, call) in enumerate(variables):
        saving = priority_weights[call] * (unserved_time - travel_times[(amb, call)])
        h[i] = -saving

    # Quadratic constraints: One ambulance to at most one call
    for i in range(num_vars):
        for j in range(i+1, num_vars):
            amb_i, call_i = variables[i]
            amb_j, call_j = variables[j]
            
            # Constraint 1: same ambulance
            if amb_i == amb_j:
                J[(i, j)] = J.get((i, j), 0) + assignment_penalty
                
            # Constraint 2: same call
            if call_i == call_j:
                J[(i, j)] = J.get((i, j), 0) + assignment_penalty
                
            # Coverage penalty: if A1 and A2 are both dispatched
            if (amb_i == 'A1' and amb_j == 'A2') or (amb_i == 'A2' and amb_j == 'A1'):
                J[(i, j)] = J.get((i, j), 0) + coverage_penalty
                
    return h, J

def calc_raw_objective(
    x, 
    include_coverage=True, 
    lambda_coverage=LAMBDA_COVERAGE_2, 
    shared_demand=SHARED_DEMAND_2
):
    """Calculate the raw response time and coverage cost."""
    assignments = []
    for i, val in enumerate(x):
        if val == 1:
            assignments.append(VARIABLES_2[i])
            
    ambs = [a for a, c in assignments]
    calls = [c for a, c in assignments]
    
    if len(set(ambs)) < len(ambs) or len(set(calls)) < len(calls):
        return float('inf')
        
    cost = 0
    served_calls = set(calls)
    
    for c in ['C2', 'C3']:
        if c not in served_calls:
            cost += PRIORITY_WEIGHTS_2[c] * UNSERVED_TIME_2
            
    for a, c in assignments:
        cost += PRIORITY_WEIGHTS_2[c] * TRAVEL_TIMES_2[(a, c)]
        
    if include_coverage:
        if 'A1' in ambs and 'A2' in ambs:
            cost += int(lambda_coverage * shared_demand)
            
    return cost

