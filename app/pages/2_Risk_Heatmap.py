import sys
import os
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.components.heatmap_chart import render_heatmap_figure, classify_risk_band

# Configure Page
st.set_page_config(
    page_title="Risk Heatmap | Quantum-Readiness Risk Score",
    page_icon="🗺️",
    layout="wide",
)

# Load UI Design System Styles
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize Session State fallback if user visits this page directly
if "assets_df" not in st.session_state:
    sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_assets.csv")
    if os.path.exists(sample_path):
        st.session_state.assets_df = pd.read_csv(sample_path)
    else:
        st.session_state.assets_df = pd.DataFrame()

st.markdown('<div class="page-title">Cryptographic Risk Exposure Heatmap</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="text-muted">High-level executive matrix visualizing vulnerability distribution '
    'across banking infrastructure tiers and risk severity bands.</p>',
    unsafe_allow_html=True,
)

df = st.session_state.assets_df

if df.empty:
    st.warning("Empty State: No assets available to plot. Please go to the 'Asset Inventory' page to upload or register assets.")
else:
    # Top KPI Metrics Cards
    df_with_band = df.copy()
    df_with_band["risk_band"] = df_with_band["risk_score"].apply(classify_risk_band)
    
    crit_count = len(df_with_band[df_with_band["risk_band"] == "Critical"])
    high_count = len(df_with_band[df_with_band["risk_band"] == "High"])
    med_count = len(df_with_band[df_with_band["risk_band"] == "Medium"])
    low_count = len(df_with_band[df_with_band["risk_band"] == "Low"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="quantum-card">'
            f'<div class="text-muted">CRITICAL RISK</div>'
            f'<div style="font-size:32px; font-weight:700; color:#C0392B;">{crit_count}</div>'
            f'<div class="text-muted" style="font-size:12px;">Score ≥ 75 | Immediate Phase 1</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="quantum-card">'
            f'<div class="text-muted">HIGH RISK</div>'
            f'<div style="font-size:32px; font-weight:700; color:#E07B39;">{high_count}</div>'
            f'<div class="text-muted" style="font-size:12px;">Score 50–74.9 | Near-term transition</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="quantum-card">'
            f'<div class="text-muted">MEDIUM RISK</div>'
            f'<div style="font-size:32px; font-weight:700; color:#E4B429;">{med_count}</div>'
            f'<div class="text-muted" style="font-size:12px;">Score 25–49.9 | Phase 2 candidate</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="quantum-card">'
            f'<div class="text-muted">LOW RISK</div>'
            f'<div style="font-size:32px; font-weight:700; color:#2E8B57;">{low_count}</div>'
            f'<div class="text-muted" style="font-size:12px;">Score &lt; 25 | Quantum runway safe</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Render Plotly Heatmap
    st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
    heatmap_fig = render_heatmap_figure(df)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Interactive Cell Drill-Down Table
    st.markdown('<div class="section-title">Drill-Down: Inspect Assets by Cell</div>', unsafe_allow_html=True)
    filter_col1, filter_col2 = st.columns(2)
    selected_cat = filter_col1.selectbox("Filter by Category:", ["All Categories"] + sorted(df["system_category"].unique().tolist()))
    selected_band = filter_col2.selectbox("Filter by Risk Band:", ["All Bands", "Critical", "High", "Medium", "Low"])

    drill_df = df_with_band.copy()
    if selected_cat != "All Categories":
        drill_df = drill_df[drill_df["system_category"] == selected_cat]
    if selected_band != "All Bands":
        drill_df = drill_df[drill_df["risk_band"] == selected_band]

    st.markdown(f"**Displaying {len(drill_df)} matching cryptographic assets:**")
    st.dataframe(
        drill_df[[
            "asset_id", "asset_name", "system_category", "algorithm",
            "key_size_bits", "data_sensitivity", "estimated_years_to_break",
            "risk_score", "risk_band", "migration_phase", "recommended_pqc_algorithm"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "asset_id": st.column_config.NumberColumn("ID", width="small"),
            "asset_name": st.column_config.TextColumn("Asset Name", width="large"),
            "system_category": st.column_config.TextColumn("Category", width="medium"),
            "algorithm": st.column_config.TextColumn("Algorithm", width="small"),
            "key_size_bits": st.column_config.NumberColumn("Key Size", width="small"),
            "data_sensitivity": st.column_config.TextColumn("Sensitivity", width="small"),
            "estimated_years_to_break": st.column_config.NumberColumn("Years to Break", format="%.1f yrs", width="small"),
            "risk_score": st.column_config.ProgressColumn("Risk Score", format="%.1f", min_value=0, max_value=100, width="medium"),
            "risk_band": st.column_config.TextColumn("Risk Tier", width="small"),
            "migration_phase": st.column_config.TextColumn("Phase", width="small"),
            "recommended_pqc_algorithm": st.column_config.TextColumn("Target PQC", width="medium"),
        }
    )
