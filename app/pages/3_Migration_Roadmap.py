import sys
import os
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.components.roadmap_timeline import render_roadmap_gantt

# Configure Page
st.set_page_config(
    page_title="Migration Roadmap | Quantum-Readiness Risk Score",
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

# Initialize Session State fallback
if "assets_df" not in st.session_state:
    sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_assets.csv")
    if os.path.exists(sample_path):
        st.session_state.assets_df = pd.read_csv(sample_path)
    else:
        st.session_state.assets_df = pd.DataFrame()

st.markdown('<div class="page-title">PQC Migration Roadmap & Phasing</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="text-muted">Prioritized remediation plan bucketing bank cryptographic assets '
    'into strategic migration phases based on quantum risk and complexity.</p>',
    unsafe_allow_html=True,
)

df = st.session_state.assets_df

if df.empty:
    st.warning("Empty State: No assets available. Please upload or register assets in the 'Asset Inventory' module.")
else:
    # 1. Executive Timeline Gantt Chart
    st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
    gantt_fig = render_roadmap_gantt()
    st.plotly_chart(gantt_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Filter Controls
    f_col1, f_col2 = st.columns([2, 1])
    search_term = f_col1.text_input("Filter roadmap cards by asset name or algorithm:", "")
    selected_category = f_col2.selectbox("Filter by Category:", ["All Categories"] + sorted(df["system_category"].unique().tolist()))

    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[
            filtered_df["asset_name"].str.contains(search_term, case=False, na=False) |
            filtered_df["algorithm"].str.contains(search_term, case=False, na=False) |
            filtered_df["recommended_pqc_algorithm"].str.contains(search_term, case=False, na=False)
        ]
    if selected_category != "All Categories":
        filtered_df = filtered_df[filtered_df["system_category"] == selected_category]

    # Partition assets into the three phases
    phase1_assets = filtered_df[filtered_df["migration_phase"] == "Phase 1"].sort_values(by="risk_score", ascending=False)
    phase2_assets = filtered_df[filtered_df["migration_phase"] == "Phase 2"].sort_values(by="risk_score", ascending=False)
    phase3_assets = filtered_df[filtered_df["migration_phase"] == "Phase 3"].sort_values(by="risk_score", ascending=False)

    # Helper function to render an asset card per the UI Design System (Rule 11)
    def render_asset_card(row):
        score = row.get("risk_score", 0.0)
        if score >= 75.0:
            badge_class = "risk-critical-bg"
        elif score >= 50.0:
            badge_class = "risk-high-bg"
        elif score >= 25.0:
            badge_class = "risk-medium-bg"
        else:
            badge_class = "risk-low-bg"

        algo_display = f"{row.get('algorithm', '')}-{row.get('key_size_bits', '')}"
        years = row.get("estimated_years_to_break", 0.0)
        pqc = row.get("recommended_pqc_algorithm", "NIST PQC Target")
        cat = row.get("system_category", "Banking System")
        name = row.get("asset_name", "Cryptographic Key")
        cost = row.get("migration_cost_score", 5.0)

        html = f"""
        <div class="quantum-card" style="padding:16px; margin-bottom:16px; border-top: 4px solid var(--secondary-steelblue);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                <span class="text-muted" style="font-size:12px; font-weight:600; text-transform:uppercase;">{cat}</span>
                <span class="risk-badge {badge_class}">{score:.1f}</span>
            </div>
            <div style="font-size:15px; font-weight:700; color:#0B1F3A; margin-bottom:6px; line-height:1.3;">{name}</div>
            <div style="font-size:13px; margin-bottom:10px;">
                <span class="text-muted">Legacy Key:</span> <span class="mono-text" style="font-weight:600; color:#1B1F27;">{algo_display}</span>
                <span style="color:#6B7280; margin:0 6px;">•</span>
                <span class="text-muted">Runway:</span> <span style="font-weight:600;">{years:.1f} yrs</span>
            </div>
            <div style="background-color:#F7F9FC; border-radius:6px; padding:8px 10px; border-left:3px solid #3A6EA5;">
                <div style="font-size:11px; text-transform:uppercase; color:#6B7280; font-weight:600;">Target NIST PQC Standard</div>
                <div style="font-size:13px; font-weight:700; color:#0B1F3A;">{pqc}</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px; font-size:12px; color:#6B7280;">
                <span>Migration Cost: <b>{cost:.1f}/10</b></span>
                <span style="font-size:11px; font-weight:500;">Asset ID: #{row.get('asset_id', '-')}</span>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    # 3. Three-Column Phase Board
    st.markdown('<div class="section-title">Strategic Remediation Phases</div>', unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.markdown(
            f'<div style="background-color:#FDEDEC; border:1px solid #F5B7B1; border-radius:8px; padding:12px; margin-bottom:16px;">'
            f'<div style="font-weight:700; color:#922B21; font-size:16px;">🚨 Phase 1 (Score ≥ 70)</div>'
            f'<div style="font-size:12px; color:#78281F;"><b>{len(phase1_assets)} assets</b> • Immediate Priority (2026–2028)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if phase1_assets.empty:
            st.info("No Phase 1 assets under current filter.")
        else:
            for _, asset in phase1_assets.iterrows():
                render_asset_card(asset)

    with col_p2:
        st.markdown(
            f'<div style="background-color:#FEF9E7; border:1px solid #F9E79F; border-radius:8px; padding:12px; margin-bottom:16px;">'
            f'<div style="font-weight:700; color:#9A7D0A; font-size:16px;">⚠️ Phase 2 (Score 40–69)</div>'
            f'<div style="font-size:12px; color:#7D6608;"><b>{len(phase2_assets)} assets</b> • Medium-Term (2028–2031)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if phase2_assets.empty:
            st.info("No Phase 2 assets under current filter.")
        else:
            for _, asset in phase2_assets.iterrows():
                render_asset_card(asset)

    with col_p3:
        st.markdown(
            f'<div style="background-color:#EAFAF1; border:1px solid #A9DFBF; border-radius:8px; padding:12px; margin-bottom:16px;">'
            f'<div style="font-weight:700; color:#1E8449; font-size:16px;">🛡️ Phase 3 (Score &lt; 40)</div>'
            f'<div style="font-size:12px; color:#145A32;"><b>{len(phase3_assets)} assets</b> • Long-Term (2031–2035)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if phase3_assets.empty:
            st.info("No Phase 3 assets under current filter.")
        else:
            for _, asset in phase3_assets.iterrows():
                render_asset_card(asset)
