"""
Years-to-Break Estimator Model
Estimates the time window (in years) before a Cryptographically Relevant 
Quantum Computer (CRQC) is projected to break specific legacy cryptographic keys,
based on published NIST Special Publication (SP 800-56B/C) and academic timelines (Mosca's theorem).
"""

from typing import Union

# Baseline timeline matrix (in estimated years until Shor's algorithm feasibility on target key size)
# Based on NIST PQC transition guidelines and Gidney & Ekerå quantum resource estimates.
QUANTUM_TIMELINE_LOOKUP = {
    # RSA (Integer Factorization Problem - Shor's Algorithm)
    ("RSA", 1024): 2.5,    # Critical near-term risk, already deprecation-vulnerable
    ("RSA", 2048): 7.0,    # Medium-term risk (NIST baseline target ~2030-2033)
    ("RSA", 3072): 10.0,   # Moderate runway
    ("RSA", 4096): 13.0,   # Longer runway due to higher qubit & gate count requirements
    
    # ECC / ECDSA (Discrete Logarithm Problem - Shor's Algorithm)
    # Note: ECC requires fewer physical/logical qubits than RSA for equivalent security levels
    ("ECC", 160): 2.0,     # Deprecated / critical
    ("ECC", 224): 3.5,     # Very high vulnerability
    ("ECC", 256): 5.0,     # Vulnerable sooner than RSA-2048 due to smaller qubit overhead
    ("ECC", 384): 9.0,     # High-grade ECC, longer runway
    ("ECC", 521): 11.5,    # Maximum standard curve runway
    
    # Legacy Discrete Logarithm (DSA / Diffie-Hellman)
    ("DSA", 1024): 2.5,
    ("DSA", 2048): 6.5,
    ("DIFFIE-HELLMAN", 1024): 2.5,
    ("DIFFIE-HELLMAN", 2048): 6.5,
    ("DIFFIE-HELLMAN", 3072): 9.5,
    
    # Symmetric / Post-Quantum resistant (Grover's algorithm only cuts security in half)
    ("AES", 128): 15.0,    # Grover's effective security = 64 bits (viable long-term with eventual upgrade)
    ("AES", 192): 20.0,    # Grover's effective security = 96 bits
    ("AES", 256): 25.0,    # Grover's effective security = 128 bits (quantum safe indefinitely)
}

def estimate_years_to_break(algorithm: str, key_size_bits: Union[int, float]) -> float:
    """
    Computes estimated years to quantum break for a given algorithm and key length.
    
    Parameters:
        algorithm (str): Name of the cryptographic algorithm (e.g., 'RSA', 'ECC', 'AES').
        key_size_bits (int | float): Key length in bits (e.g., 1024, 2048, 256).
        
    Returns:
        float: Estimated years until quantum compromise.
        
    Raises:
        ValueError: If algorithm is invalid or key_size_bits is non-positive.
    """
    if not algorithm or not isinstance(algorithm, str):
        raise ValueError("Algorithm must be a valid non-empty string.")
    
    try:
        key_size = int(key_size_bits)
    except (ValueError, TypeError):
        raise ValueError("key_size_bits must be an integer.")
        
    if key_size <= 0:
        raise ValueError("key_size_bits must be a positive integer.")
        
    algo_clean = algorithm.strip().upper()
    
    # Exact lookup
    key = (algo_clean, key_size)
    if key in QUANTUM_TIMELINE_LOOKUP:
        return QUANTUM_TIMELINE_LOOKUP[key]
        
    # Heuristic fallback for arbitrary key sizes
    if algo_clean in ("RSA", "DSA", "DIFFIE-HELLMAN"):
        if key_size <= 1024:
            return 2.5
        elif key_size <= 2048:
            return 2.5 + (key_size - 1024) * (4.5 / 1024)
        elif key_size <= 4096:
            return 7.0 + (key_size - 2048) * (6.0 / 2048)
        else:
            return 13.0 + min(5.0, (key_size - 4096) * 0.001)
            
    elif algo_clean == "ECC":
        if key_size <= 160:
            return 2.0
        elif key_size <= 256:
            return 2.0 + (key_size - 160) * (3.0 / 96)
        elif key_size <= 384:
            return 5.0 + (key_size - 256) * (4.0 / 128)
        elif key_size <= 521:
            return 9.0 + (key_size - 384) * (2.5 / 137)
        else:
            return 12.0
            
    elif algo_clean == "AES":
        if key_size < 192:
            return 15.0
        elif key_size < 256:
            return 20.0
        else:
            return 25.0
            
    # Default fallback for unknown or generic algorithms
    return 8.0
