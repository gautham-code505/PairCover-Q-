import itertools
import numpy as np

def generate_all_bitstrings(n):
    """
    Generate an independent brute-force enumeration of all 2^n bitstrings.
    Each bitstring is a tuple of 0s and 1s.
    """
    return list(itertools.product([0, 1], repeat=n))
