"""
Supabase Database Client (Free-Tier Postgres)
Per Rule 9 & Rule 10:
Connects to Supabase via `supabase-py` using environment variables or st.secrets.
Never hardcodes credentials; supports graceful fallback if database is unconfigured.
"""

import os
import streamlit as st
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Global cached client
_SUPABASE_CLIENT = None

def get_supabase_client():
    """
    Retrieves or initializes the Supabase client.
    Checks st.secrets first (for Streamlit Community Cloud), then os.getenv (for local .env).
    """
    global _SUPABASE_CLIENT
    if _SUPABASE_CLIENT is not None:
        return _SUPABASE_CLIENT

    # 1. Check Streamlit Secrets (Cloud Deployment)
    url = None
    key = None
    
    try:
        if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
    except Exception:
        pass

    # 2. Check local environment variables (.env)
    if not url or not key:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

    # If credentials are not dummy placeholders
    if url and key and "your-project" not in url:
        try:
            from supabase import create_client, Client
            _SUPABASE_CLIENT = create_client(url, key)
            return _SUPABASE_CLIENT
        except Exception as e:
            st.warning(f"Database Connection Warning: Unable to connect to Supabase: {e}")
            return None
    
    return None

def fetch_crypto_assets() -> Optional[list]:
    """Fetches all assets from the 'crypto_assets' table if Supabase is connected."""
    client = get_supabase_client()
    if client:
        try:
            response = client.table("crypto_assets").select("*").execute()
            return response.data
        except Exception as e:
            st.warning(f"Database query error: {e}")
            return None
    return None

def upsert_crypto_assets(records: list) -> bool:
    """Upserts cryptographic asset records into the 'crypto_assets' table."""
    client = get_supabase_client()
    if client and records:
        try:
            client.table("crypto_assets").upsert(records).execute()
            return True
        except Exception as e:
            st.warning(f"Database upsert error: {e}")
            return False
    return False
