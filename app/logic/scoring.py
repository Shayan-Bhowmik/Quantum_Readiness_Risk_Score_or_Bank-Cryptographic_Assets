"""
Quantum Risk Scoring & Roadmap Phasing Engine (Python Fallback)
Mirrors the mathematical logic of:
  - `sas/risk_score_engine.sas` (Risk score normalization)
  - `sas/roadmap_phasing.sas` (Phasing thresholds & NIST PQC replacement mapping)
"""

import os
import pandas as pd
from typing import Union, Dict, Any

SENSITIVITY_WEIGHTS: Dict[str, float] = {
    "CRITICAL": 4.0,
    "HIGH": 3.0,
    "MEDIUM": 2.0,
    "LOW": 1.0,
}

NORMALIZATION_CEILING: float = 80.0

# In-memory NIST PQC cache
_PQC_MAPPING_CACHE: Dict[str, str] = {}

def load_pqc_mapping() -> Dict[str, str]:
    """
    Loads legacy-to-PQC replacement dictionary from data/nist_pqc_mapping.csv.
    """
    global _PQC_MAPPING_CACHE
    if not _PQC_MAPPING_CACHE:
        mapping_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "nist_pqc_mapping.csv")
        if os.path.exists(mapping_path):
            try:
                mapping_df = pd.read_csv(mapping_path)
                for _, row in mapping_df.iterrows():
                    key = str(row["legacy_algorithm"]).strip().upper()
                    target = str(row["recommended_pqc_algorithm"]).strip()
                    _PQC_MAPPING_CACHE[key] = target
            except Exception:
                pass
                
        # Built-in robust NIST fallback defaults
        defaults = {
            "RSA-1024": "CRYSTALS-Dilithium (ML-DSA)",
            "RSA-2048": "CRYSTALS-Dilithium (ML-DSA)",
            "RSA-3072": "CRYSTALS-Dilithium (ML-DSA)",
            "RSA-4096": "CRYSTALS-Dilithium (ML-DSA)",
            "ECC-160": "CRYSTALS-Kyber (ML-KEM)",
            "ECC-224": "CRYSTALS-Kyber (ML-KEM)",
            "ECC-256": "CRYSTALS-Kyber (ML-KEM)",
            "ECC-384": "CRYSTALS-Kyber (ML-KEM)",
            "ECC-521": "CRYSTALS-Kyber (ML-KEM)",
            "DSA-1024": "SPHINCS+ (SLH-DSA)",
            "DSA-2048": "SPHINCS+ (SLH-DSA)",
            "DIFFIE-HELLMAN-1024": "CRYSTALS-Kyber (ML-KEM)",
            "DIFFIE-HELLMAN-2048": "CRYSTALS-Kyber (ML-KEM)",
            "AES-128": "AES-256",
            "AES-192": "AES-256",
            "AES-256": "AES-256",
        }
        for k, v in defaults.items():
            _PQC_MAPPING_CACHE.setdefault(k, v)
            
    return _PQC_MAPPING_CACHE

def resolve_recommended_pqc(algorithm: str, key_size_bits: Union[int, float, str]) -> str:
    """
    Determines the recommended NIST PQC replacement algorithm for any asset.
    """
    mapping = load_pqc_mapping()
    algo_clean = str(algorithm).strip().upper()
    try:
        key_size_clean = str(int(float(key_size_bits)))
    except (ValueError, TypeError):
        key_size_clean = "2048"
        
    lookup_key = f"{algo_clean}-{key_size_clean}"
    if lookup_key in mapping:
        return mapping[lookup_key]
        
    # Heuristic family fallback
    if "RSA" in algo_clean or "DSA" in algo_clean:
        return "CRYSTALS-Dilithium (ML-DSA)"
    elif "ECC" in algo_clean or "ECDSA" in algo_clean or "DIFFIE" in algo_clean:
        return "CRYSTALS-Kyber (ML-KEM)"
    elif "AES" in algo_clean:
        return "AES-256"
        
    return "CRYSTALS-Dilithium (ML-DSA)"

def calculate_single_risk_score(
    data_sensitivity: str,
    estimated_years_to_break: Union[int, float],
    migration_cost_score: Union[int, float],
    algorithm: str = "RSA",
    key_size_bits: Union[int, float] = 2048,
) -> Dict[str, Any]:
    """
    Computes normalized quantum risk score, roadmap migration phase, and recommended PQC target.
    """
    sens_key = str(data_sensitivity).strip().upper()
    sensitivity_weight = SENSITIVITY_WEIGHTS.get(sens_key, 1.0)
    
    safe_years = max(float(estimated_years_to_break), 0.25)
    time_urgency = 1.0 / safe_years
    safe_cost = min(max(float(migration_cost_score), 1.0), 10.0)
    
    raw_risk = sensitivity_weight * time_urgency * safe_cost
    risk_score = round(min(100.0, max(0.0, (raw_risk / NORMALIZATION_CEILING) * 100.0)), 1)
    
    # Roadmap Phasing Thresholds
    if risk_score >= 70.0:
        migration_phase = "Phase 1"
    elif risk_score >= 40.0:
        migration_phase = "Phase 2"
    else:
        migration_phase = "Phase 3"
        
    recommended_pqc = resolve_recommended_pqc(algorithm, key_size_bits)
        
    return {
        "raw_risk": round(raw_risk, 3),
        "risk_score": risk_score,
        "migration_phase": migration_phase,
        "recommended_pqc_algorithm": recommended_pqc,
    }

def score_asset_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the risk scoring and roadmap phasing models to a DataFrame of assets.
    Ensures every asset receives risk_score, migration_phase, and non-empty recommended_pqc_algorithm.
    """
    scored_df = df.copy()
    
    scores = []
    phases = []
    pqc_targets = []
    
    for _, row in scored_df.iterrows():
        res = calculate_single_risk_score(
            data_sensitivity=row.get("data_sensitivity", "Medium"),
            estimated_years_to_break=row.get("estimated_years_to_break", 7.0),
            migration_cost_score=row.get("migration_cost_score", 5.0),
            algorithm=row.get("algorithm", "RSA"),
            key_size_bits=row.get("key_size_bits", 2048),
        )
        scores.append(res["risk_score"])
        phases.append(res["migration_phase"])
        
        # Use existing recommended_pqc_algorithm if present and non-empty, else resolved target
        existing_pqc = str(row.get("recommended_pqc_algorithm", "")).strip()
        if existing_pqc and existing_pqc.lower() != "nan":
            pqc_targets.append(existing_pqc)
        else:
            pqc_targets.append(res["recommended_pqc_algorithm"])
        
    scored_df["risk_score"] = scores
    scored_df["migration_phase"] = phases
    scored_df["recommended_pqc_algorithm"] = pqc_targets
    
    return scored_df
