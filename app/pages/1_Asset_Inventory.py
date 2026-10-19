import sys
import os
from datetime import datetime, timezone
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path for robust imports across all multi-page modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.logic.sas_connector import run_scoring_pipeline
from app.logic.scoring import calculate_single_risk_score
from app.logic.roles import ROLES, get_role_permissions

# Configure Page
st.set_page_config(
    page_title="Asset Inventory | Quantum-Readiness Risk Score",
    page_icon="📋",
    layout="wide",
)

# Load UI Design System Styles
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize Session State
if "current_role" not in st.session_state:
    st.session_state.current_role = ROLES[0]  # Default to CISO / Security Architect

# Global Sidebar Role Switcher
with st.sidebar:
    st.markdown("### 👤 User Persona & Role")
    selected_role = st.selectbox(
        "Active Role:",
        ROLES,
        index=ROLES.index(st.session_state.current_role),
        help="Switch user persona to test RBAC permissions and dynamic view masking."
    )
    st.session_state.current_role = selected_role
    perms = get_role_permissions(selected_role)
    st.markdown(
        f'<div style="background-color:#F7F9FC; border-left:3px solid {perms["badge_color"]}; padding:8px; border-radius:4px; font-size:12px; color:#1B1F27;">'
        f'<b>{selected_role}</b><br><span style="color:#6B7280;">{perms["description"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

perms = get_role_permissions(st.session_state.current_role)

# Required Schema Constants
REQUIRED_COLUMNS = [
    "asset_id",
    "asset_name",
    "system_category",
    "algorithm",
    "key_size_bits",
    "data_sensitivity",
    "estimated_years_to_break",
    "migration_cost_score",
    "risk_score",
    "migration_phase",
    "recommended_pqc_algorithm",
]

VALID_CATEGORIES = ["Card Network", "SWIFT", "Internal PKI"]
VALID_SENSITIVITIES = ["Low", "Medium", "High", "Critical"]
VALID_PHASES = ["Phase 1", "Phase 2", "Phase 3"]

if "assets_df" not in st.session_state:
    sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_assets.csv")
    if os.path.exists(sample_path):
        st.session_state.assets_df = pd.read_csv(sample_path)
    else:
        st.session_state.assets_df = pd.DataFrame(columns=REQUIRED_COLUMNS + ["created_at", "updated_at"])

if "scoring_status" not in st.session_state:
    st.session_state.scoring_status = None

st.markdown('<div class="page-title">Cryptographic Asset Inventory</div>', unsafe_allow_html=True)
st.markdown(
    f'<p class="text-muted">Viewing as <b>{st.session_state.current_role}</b> • '
    f'{"Technical crypto specifications visible" if perms["see_technical_algo_keys"] else "High-level risk view (algorithm specs masked)"}.</p>',
    unsafe_allow_html=True,
)

# Tabs: View & Upload vs. Manual Entry
tab_inventory, tab_manual = st.tabs(["📂 Inventory & CSV Upload", "➕ Register New Asset"])

with tab_inventory:
    st.markdown('<div class="section-title">Upload Asset Inventory CSV</div>', unsafe_allow_html=True)
    
    # Check upload permission
    if perms["can_upload_csv"]:
        uploaded_file = st.file_uploader(
            "Upload cryptographic assets CSV file",
            type=["csv"],
            help="Upload a CSV file containing bank cryptographic assets. Must include all mandatory security columns.",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                missing_cols = [col for col in REQUIRED_COLUMNS if col not in uploaded_df.columns]
                if missing_cols:
                    st.error(f"Upload Rejected: Missing mandatory columns: {', '.join(missing_cols)}")
                else:
                    invalid_cats = uploaded_df[~uploaded_df["system_category"].isin(VALID_CATEGORIES)]["system_category"].dropna().unique()
                    invalid_sens = uploaded_df[~uploaded_df["data_sensitivity"].isin(VALID_SENSITIVITIES)]["data_sensitivity"].dropna().unique()

                    if len(invalid_cats) > 0:
                        st.error(f"Invalid row values detected: Unauthorized system_category values: {', '.join(map(str, invalid_cats))}")
                    elif len(invalid_sens) > 0:
                        st.error(f"Invalid row values detected: Unauthorized data_sensitivity values: {', '.join(map(str, invalid_sens))}")
                    else:
                        st.session_state.assets_df = uploaded_df
                        st.session_state.scoring_status = None
                        st.success(f"Successfully loaded {len(uploaded_df)} cryptographic assets from uploaded file.")
            except Exception as e:
                st.error(f"File Parsing Error: Unable to parse CSV file. Detail: {str(e)}")
    else:
        st.info(f"🔒 **Upload Disabled for {st.session_state.current_role}:** Read-only governance mode active.")

    st.markdown("---")
    
    # Action Header: Title + Run Scoring Button
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown('<div class="section-title">Current Asset Inventory</div>', unsafe_allow_html=True)
    with head_col2:
        scoring_disabled = not perms["can_run_scoring"]
        if st.button("⚡ Run Scoring Engine", disabled=scoring_disabled, use_container_width=True):
            if not st.session_state.assets_df.empty:
                with st.spinner("Executing Risk Scoring Engine..."):
                    scored_df, metadata = run_scoring_pipeline(st.session_state.assets_df)
                    st.session_state.assets_df = scored_df
                    st.session_state.scoring_status = metadata
            else:
                st.warning("Empty Inventory: Upload assets before scoring.")

    # Status Banner for Scoring
    if st.session_state.scoring_status:
        meta = st.session_state.scoring_status
        if meta["status"] == "SUCCESS":
            st.success(f"{meta['message']} (Latency: {meta['latency_seconds']}s)")
        else:
            st.warning(f"{meta['message']} (Execution time: {meta['latency_seconds']}s)")
    
    df = st.session_state.assets_df
    if df.empty:
        st.warning("Empty Inventory: No cryptographic assets registered yet.")
    else:
        # Metrics summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Assets", len(df))
        col2.metric("Critical / High Risk", len(df[df["risk_score"] >= 70.0]))
        col3.metric("Phase 1 Priority", len(df[df["migration_phase"] == "Phase 1"]))
        col4.metric("Average Risk Score", f"{df['risk_score'].mean():.1f}")

        # Search and Category Filter
        filt_col1, filt_col2 = st.columns([2, 1])
        search_query = filt_col1.text_input("Search asset name:", "")
        selected_category = filt_col2.selectbox("Filter by System Category:", ["All"] + VALID_CATEGORIES)

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["asset_name"].str.contains(search_query, case=False, na=False)]
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["system_category"] == selected_category]

        # Dynamic Column Selection based on RBAC Permissions
        if perms["see_technical_algo_keys"]:
            display_columns = [
                "asset_id", "asset_name", "system_category", "algorithm",
                "key_size_bits", "data_sensitivity", "estimated_years_to_break",
                "risk_score", "migration_phase", "recommended_pqc_algorithm"
            ]
            col_cfg = {
                "asset_id": st.column_config.NumberColumn("ID", width="small"),
                "asset_name": st.column_config.TextColumn("Asset Name", width="large"),
                "system_category": st.column_config.TextColumn("Category", width="medium"),
                "algorithm": st.column_config.TextColumn("Algorithm", width="small"),
                "key_size_bits": st.column_config.NumberColumn("Key Size", width="small"),
                "data_sensitivity": st.column_config.TextColumn("Sensitivity", width="small"),
                "estimated_years_to_break": st.column_config.NumberColumn("Years to Break", format="%.1f yrs", width="small"),
                "risk_score": st.column_config.ProgressColumn("Risk Score", format="%.1f", min_value=0, max_value=100, width="medium"),
                "migration_phase": st.column_config.TextColumn("Phase", width="small"),
                "recommended_pqc_algorithm": st.column_config.TextColumn("Target PQC", width="medium"),
            }
        else:
            # Mask technical algorithm & key_size_bits columns for Risk Officer
            display_columns = [
                "asset_id", "asset_name", "system_category",
                "data_sensitivity", "estimated_years_to_break",
                "risk_score", "migration_phase", "recommended_pqc_algorithm"
            ]
            col_cfg = {
                "asset_id": st.column_config.NumberColumn("ID", width="small"),
                "asset_name": st.column_config.TextColumn("Asset Name", width="large"),
                "system_category": st.column_config.TextColumn("Category", width="medium"),
                "data_sensitivity": st.column_config.TextColumn("Sensitivity", width="small"),
                "estimated_years_to_break": st.column_config.NumberColumn("Years to Break", format="%.1f yrs", width="small"),
                "risk_score": st.column_config.ProgressColumn("Risk Score", format="%.1f", min_value=0, max_value=100, width="medium"),
                "migration_phase": st.column_config.TextColumn("Phase", width="small"),
                "recommended_pqc_algorithm": st.column_config.TextColumn("Target PQC", width="medium"),
            }

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True,
            column_config=col_cfg,
        )

with tab_manual:
    st.markdown('<div class="section-title">Manual Asset Registration</div>', unsafe_allow_html=True)
    
    if perms["can_add_asset"]:
        st.markdown('<p class="text-muted">Enter asset metadata to compute initial posture and add to the active inventory.</p>', unsafe_allow_html=True)

        with st.form("manual_asset_form", clear_on_submit=True):
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                form_asset_name = st.text_input("Asset Name*", placeholder="e.g., SWIFT Financial Messaging Gateway Key")
                form_category = st.selectbox("System Category*", VALID_CATEGORIES)
                form_algorithm = st.selectbox("Algorithm*", ["RSA", "ECC", "AES", "DSA", "Diffie-Hellman"])
                form_key_size = st.number_input("Key Size (bits)*", min_value=128, max_value=8192, value=2048, step=128)

            with m_col2:
                form_sensitivity = st.selectbox("Data Sensitivity*", VALID_SENSITIVITIES, index=2)
                form_years_to_break = st.number_input("Estimated Years to Quantum Break*", min_value=0.5, max_value=30.0, value=7.0, step=0.5)
                form_cost_score = st.slider("Estimated Migration Complexity / Cost (1-10)*", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
                form_pqc = st.selectbox("Recommended PQC Algorithm*", ["CRYSTALS-Dilithium", "CRYSTALS-Kyber", "SPHINCS+", "FALCON", "LMS/XMSS"])

            submitted = st.form_submit_button("Register & Score Asset")

            if submitted:
                if not form_asset_name.strip():
                    st.error("Validation Error: Asset Name is required.")
                else:
                    score_res = calculate_single_risk_score(
                        data_sensitivity=form_sensitivity,
                        estimated_years_to_break=form_years_to_break,
                        migration_cost_score=form_cost_score,
                        algorithm=form_algorithm,
                        key_size_bits=form_key_size,
                    )

                    now_iso = datetime.now(timezone.utc).isoformat()
                    new_id = (st.session_state.assets_df["asset_id"].max() + 1) if not st.session_state.assets_df.empty else 1

                    new_row = {
                        "asset_id": new_id,
                        "asset_name": form_asset_name.strip(),
                        "system_category": form_category,
                        "algorithm": form_algorithm,
                        "key_size_bits": int(form_key_size),
                        "data_sensitivity": form_sensitivity,
                        "estimated_years_to_break": float(form_years_to_break),
                        "migration_cost_score": float(form_cost_score),
                        "risk_score": score_res["risk_score"],
                        "migration_phase": score_res["migration_phase"],
                        "recommended_pqc_algorithm": form_pqc,
                        "created_at": now_iso,
                        "updated_at": now_iso,
                    }

                    st.session_state.assets_df = pd.concat([st.session_state.assets_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Asset '{form_asset_name}' registered successfully! Assigned Risk Score: {score_res['risk_score']} ({score_res['migration_phase']}).")
                    st.rerun()
    else:
        st.warning(f"🚫 **Access Restricted:** {st.session_state.current_role} does not possess authorization to register cryptographic keys directly.")
