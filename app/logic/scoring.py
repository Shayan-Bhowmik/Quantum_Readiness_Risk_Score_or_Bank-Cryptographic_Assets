"""
Quantum Risk Scoring Engine (Python Fallback)
Mirrors the mathematical logic of `sas/risk_score_engine.sas`.

Formula:
    raw_risk = sensitivity_weight * (1 / max(estimated_years_to_break, 0.25)) * migration_cost_score
    risk_score = min(100.0, max(0.0, (raw_risk / normalizer) * 100.0))
"""

import pandas as pd
from typing import Union, Dict, Any

SENSITIVITY_WEIGHTS: Dict[str, float] = {
    "CRITICAL": 4.0,
    "HIGH": 3.0,
    "MEDIUM": 2.0,
    "LOW": 1.0,
}

# Normalizer calibrated to theoretical ceiling:
# 4.0 (Critical) * (1 / 0.5 yrs) * 10.0 (Cost) = 80.0
NORMALIZATION_CEILING: float = 80.0

def calculate_single_risk_score(
    data_sensitivity: str,
    estimated_years_to_break: Union[int, float],
    migration_cost_score: Union[int, float],
) -> Dict[str, Any]:
    """
    Computes normalized quantum risk score and migration phase for a single asset.
    
    Parameters:
        data_sensitivity (str): Sensitivity tier ('Low', 'Medium', 'High', 'Critical').
        estimated_years_to_break (float): Projected years until quantum feasibility.
        migration_cost_score (float): Migration complexity/cost rating (1-10 scale).
        
    Returns:
        dict: {
            'raw_risk': float,
            'risk_score': float, # 0.0 to 100.0
            'migration_phase': str # 'Phase 1', 'Phase 2', or 'Phase 3'
        }
    """
    sens_key = str(data_sensitivity).strip().upper()
    sensitivity_weight = SENSITIVITY_WEIGHTS.get(sens_key, 1.0)
    
    # Defensive lower-bound threshold to avoid division by zero
    safe_years = max(float(estimated_years_to_break), 0.25)
    time_urgency = 1.0 / safe_years
    
    # Bounded cost score (1.0 to 10.0)
    safe_cost = min(max(float(migration_cost_score), 1.0), 10.0)
    
    raw_risk = sensitivity_weight * time_urgency * safe_cost
    
    # Scale to 0-100 range and round to 1 decimal place
    risk_score = round(min(100.0, max(0.0, (raw_risk / NORMALIZATION_CEILING) * 100.0)), 1)
    
    # Assign migration phase based on risk score thresholds
    if risk_score >= 70.0:
        migration_phase = "Phase 1"
    elif risk_score >= 40.0:
        migration_phase = "Phase 2"
    else:
        migration_phase = "Phase 3"
        
    return {
        "raw_risk": round(raw_risk, 3),
        "risk_score": risk_score,
        "migration_phase": migration_phase,
    }

def score_asset_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the risk scoring model to an entire pandas DataFrame of assets.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing columns:
            ['data_sensitivity', 'estimated_years_to_break', 'migration_cost_score']
            
    Returns:
        pd.DataFrame: A copy of the DataFrame with updated 'risk_score' and 'migration_phase'.
    """
    scored_df = df.copy()
    
    scores = []
    phases = []
    
    for _, row in scored_df.iterrows():
        res = calculate_single_risk_score(
            data_sensitivity=row.get("data_sensitivity", "Medium"),
            estimated_years_to_break=row.get("estimated_years_to_break", 7.0),
            migration_cost_score=row.get("migration_cost_score", 5.0),
        )
        scores.append(res["risk_score"])
        phases.append(res["migration_phase"])
        
    scored_df["risk_score"] = scores
    scored_df["migration_phase"] = phases
    
    return scored_df
