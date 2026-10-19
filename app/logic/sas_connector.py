"""
SAS Viya / Python Connector
Manages execution of the Quantum Risk Scoring Engine on SAS Viya for Learners,
featuring automatic connection retry and resilient zero-downtime Python fallback.
"""

import os
import time
import logging
import pandas as pd
from typing import Tuple, Dict, Any
from dotenv import load_dotenv

from app.logic.scoring import score_asset_dataframe

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sas_connector")

# Security & Access Document User-Facing Message Constants
SAS_FALLBACK_WARNING = (
    "SAS Viya Engine Unreachable: Automated fallback activated. "
    "Assets scored using local Python analytical engine (identical normalization)."
)
SAS_SUCCESS_MESSAGE = "Scoring Complete: Successfully processed via SAS Viya for Learners analytical engine."

def run_scoring_pipeline(df: pd.DataFrame, max_retries: int = 2) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes the scoring pipeline on the asset inventory DataFrame.
    Attempts SAS Viya connection via saspy if credentials exist.
    Falls back gracefully to local Python scoring engine if SAS Viya is unreachable.
    
    Parameters:
        df (pd.DataFrame): Input asset inventory.
        max_retries (int): Number of connection attempts before falling back.
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]:
            - Scored DataFrame with updated 'risk_score' and 'migration_phase'
            - Metadata dict: {
                'engine': 'SAS_VIYA' | 'PYTHON_FALLBACK',
                'status': 'SUCCESS' | 'FALLBACK',
                'message': str,
                'latency_seconds': float
              }
    """
    start_time = time.time()
    
    sas_host = os.getenv("SAS_HOST")
    sas_user = os.getenv("SAS_USER")
    sas_password = os.getenv("SAS_PASSWORD")
    
    # Check if SAS credentials are fully configured in .env
    sas_configured = bool(sas_host and sas_user and sas_password and "your-viya" not in sas_host)
    
    if sas_configured:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Connecting to SAS Viya for Learners (Attempt {attempt}/{max_retries})...")
                import saspy
                
                # Initialize SAS session (HTTP connection to SAS Viya)
                sas_session = saspy.SASsession(cfgname='viya')
                
                # Upload dataframe to SAS WORK library
                sas_data = sas_session.df2sd(df, table='crypto_assets_raw')
                
                # Read and execute SAS scoring script
                sas_script_path = os.path.join(os.path.dirname(__file__), "..", "..", "sas", "risk_score_engine.sas")
                with open(sas_script_path, "r", encoding="utf-8") as f:
                    sas_code = f.read()
                    
                sas_session.submit(sas_code)
                
                # Download scored dataset back into pandas
                scored_df = sas_session.sd2df(table='crypto_assets_scored', libref='work')
                sas_session.disconnect()
                
                elapsed = round(time.time() - start_time, 2)
                logger.info(f"SAS Viya scoring completed in {elapsed}s.")
                
                return scored_df, {
                    "engine": "SAS_VIYA",
                    "status": "SUCCESS",
                    "message": SAS_SUCCESS_MESSAGE,
                    "latency_seconds": elapsed,
                }
            except Exception as e:
                logger.warning(f"SAS Viya connection attempt {attempt} failed: {e}")
                time.sleep(0.5)

    # Fallback to local Python analytical engine
    logger.info("Executing Python fallback scoring engine...")
    fallback_start = time.time()
    scored_df = score_asset_dataframe(df)
    elapsed = round(time.time() - fallback_start, 3)
    
    return scored_df, {
        "engine": "PYTHON_FALLBACK",
        "status": "FALLBACK",
        "message": SAS_FALLBACK_WARNING,
        "latency_seconds": elapsed,
    }
