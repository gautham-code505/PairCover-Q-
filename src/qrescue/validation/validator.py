from qrescue.optimization.scenario import VARIABLES

def decode_assignment(x, variables=VARIABLES):
    """
    Decodes a bitstring x into a list of assignments based on the fixed variable ordering.
    """
    assignments = []
    for i, val in enumerate(x):
        if val == 1:
            assignments.append(variables[i])
    return assignments

def is_feasible(x, variables=VARIABLES):
    """
    Independent feasibility validator.
    Validates:
    1. One ambulance serves at most one call.
    2. One call is served by at most one ambulance.
    """
    assignments = decode_assignment(x, variables)
    
    ambulance_counts = {}
    call_counts = {}
    
    for amb, call in assignments:
        ambulance_counts[amb] = ambulance_counts.get(amb, 0) + 1
        call_counts[call] = call_counts.get(call, 0) + 1
        
    for count in ambulance_counts.values():
        if count > 1: return False
        
    for count in call_counts.values():
        if count > 1: return False
        
    return True

def decode_qiskit_bitstring(bitstr, variables=VARIABLES):
    """
    Decodes a Qiskit measurement bitstring (little-endian convention)
    into binary variable list x and list of assignments.
    
    In Qiskit, bitstring key s is ordered q_{n-1}...q_1 q_0.
    Since variable k maps to qubit k, x_k = int(s[n - 1 - k]).
    """
    n = len(variables)
    if len(bitstr) != n:
        raise ValueError(f"Bitstring length {len(bitstr)} does not match variable count {n}")
    x = [int(bitstr[n - 1 - k]) for k in range(n)]
    assignments = decode_assignment(x, variables)
    return x, assignments

