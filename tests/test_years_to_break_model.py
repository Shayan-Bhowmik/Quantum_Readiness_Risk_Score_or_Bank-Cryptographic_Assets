import pytest
from app.logic.years_to_break_model import estimate_years_to_break

def test_rsa_1024_near_term_risk():
    """RSA-1024 must return a low number indicating imminent quantum vulnerability."""
    years = estimate_years_to_break("RSA", 1024)
    assert years <= 3.0
    assert isinstance(years, float)

def test_ecc_384_longer_runway():
    """ECC-384 must return a higher runway compared to RSA-1024 and ECC-256."""
    years_ecc_384 = estimate_years_to_break("ECC", 384)
    years_rsa_1024 = estimate_years_to_break("RSA", 1024)
    years_ecc_256 = estimate_years_to_break("ECC", 256)
    
    assert years_ecc_384 > years_rsa_1024
    assert years_ecc_384 > years_ecc_256
    assert years_ecc_384 == 9.0

def test_aes_quantum_resistance():
    """Symmetric algorithms like AES-256 must offer extensive quantum runway."""
    years_aes_256 = estimate_years_to_break("AES", 256)
    assert years_aes_256 >= 20.0

def test_case_insensitivity_and_spacing():
    """Algorithm input should be resilient to whitespace and case variations."""
    assert estimate_years_to_break(" rsa ", 2048) == 7.0
    assert estimate_years_to_break("Ecc", 256) == 5.0

def test_interpolation_for_arbitrary_key_size():
    """Non-standard key sizes must interpolate smoothly within expected bounds."""
    years_rsa_1536 = estimate_years_to_break("RSA", 1536)
    # Must sit strictly between RSA-1024 (2.5) and RSA-2048 (7.0)
    assert 2.5 < years_rsa_1536 < 7.0

def test_invalid_inputs_raise_errors():
    """Invalid algorithm types or key sizes must raise ValueError."""
    with pytest.raises(ValueError):
        estimate_years_to_break("", 2048)
        
    with pytest.raises(ValueError):
        estimate_years_to_break("RSA", -1024)
        
    with pytest.raises(ValueError):
        estimate_years_to_break("RSA", "invalid_bits")
