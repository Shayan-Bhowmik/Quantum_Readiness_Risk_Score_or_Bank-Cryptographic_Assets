import os
import pandas as pd
import pytest
from app.logic.scoring import calculate_single_risk_score, score_asset_dataframe

def test_single_risk_score_bounds():
    """Risk scores must always be strictly bounded between 0.0 and 100.0."""
    res_low = calculate_single_risk_score(data_sensitivity="Low", estimated_years_to_break=20.0, migration_cost_score=1.0)
    assert 0.0 <= res_low["risk_score"] <= 100.0
    assert res_low["migration_phase"] == "Phase 3"
    
    res_high = calculate_single_risk_score(data_sensitivity="Critical", estimated_years_to_break=0.5, migration_cost_score=10.0)
    assert 0.0 <= res_high["risk_score"] <= 100.0
    assert res_high["migration_phase"] == "Phase 1"

def test_all_sample_assets_scored_between_0_and_100():
    """All assets in the dataset must receive valid scores between 0 and 100."""
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_assets.csv")
    assert os.path.exists(sample_path), f"Missing dataset at {sample_path}"
    
    df = pd.read_csv(sample_path)
    scored_df = score_asset_dataframe(df)
    
    assert "risk_score" in scored_df.columns
    assert "migration_phase" in scored_df.columns
    assert scored_df["risk_score"].min() >= 0.0
    assert scored_df["risk_score"].max() <= 100.0
    assert not scored_df["risk_score"].isna().any()

def test_top_10_percent_benchmark():
    """
    Acceptance Criteria: A manually-verified critical asset 
    (RSA-1024 on SWIFT, Critical sensitivity, near-term break <= 2.5 yrs, high cost >= 8.0)
    must score in the top 10% of the entire inventory.
    """
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_assets.csv")
    df = pd.read_csv(sample_path)
    
    # Define benchmark critical asset
    benchmark_asset = {
        "asset_id": 9999,
        "asset_name": "SWIFT Primary Transaction Signing Key",
        "system_category": "SWIFT",
        "algorithm": "RSA",
        "key_size_bits": 1024,
        "data_sensitivity": "Critical",
        "estimated_years_to_break": 2.5,
        "migration_cost_score": 8.5,
        "recommended_pqc_algorithm": "CRYSTALS-Dilithium",
        "created_at": "2026-10-20T00:00:00Z",
        "updated_at": "2026-10-20T00:00:00Z",
    }
    
    # Append benchmark asset to dataset
    test_df = pd.concat([df, pd.DataFrame([benchmark_asset])], ignore_index=True)
    scored_df = score_asset_dataframe(test_df)
    
    # Calculate 90th percentile threshold (top 10%)
    p90_threshold = scored_df["risk_score"].quantile(0.90)
    benchmark_score = scored_df[scored_df["asset_id"] == 9999]["risk_score"].iloc[0]
    
    assert benchmark_score >= p90_threshold, f"Benchmark score {benchmark_score} was not >= 90th percentile threshold {p90_threshold}"
