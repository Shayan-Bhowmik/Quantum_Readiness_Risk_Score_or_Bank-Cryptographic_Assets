import sys
import os
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.components.export_report import generate_pdf_report, generate_pptx_report

# Configure the Streamlit application page
st.set_page_config(
    page_title="Quantum-Readiness Risk Score",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load UI Design System Styles
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize Session State
if "assets_df" not in st.session_state:
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_assets.csv")
    if os.path.exists(sample_path):
        st.session_state.assets_df = pd.read_csv(sample_path)
    else:
        st.session_state.assets_df = pd.DataFrame()

def main():
    st.markdown('<div class="page-title">Quantum-Readiness Risk Score for Bank Cryptographic Assets</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="text-muted">SAS Hackathon 2026 Submission • Banking Track • Automated Post-Quantum Cryptography (PQC) Modernization</p>',
        unsafe_allow_html=True,
    )

    df = st.session_state.assets_df

    # Executive Summary Hero Cards
    if not df.empty:
        total = len(df)
        p1 = len(df[df["migration_phase"] == "Phase 1"])
        p2 = len(df[df["migration_phase"] == "Phase 2"])
        p3 = len(df[df["migration_phase"] == "Phase 3"])
        avg_risk = df["risk_score"].mean()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<div class="quantum-card">'
                f'<div class="text-muted">EVALUATED ASSETS</div>'
                f'<div style="font-size:32px; font-weight:700; color:#0B1F3A;">{total}</div>'
                f'<div class="text-muted" style="font-size:12px;">Active Bank Cryptographic Keys</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="quantum-card">'
                f'<div class="text-muted">PHASE 1 (CRITICAL)</div>'
                f'<div style="font-size:32px; font-weight:700; color:#C0392B;">{p1}</div>'
                f'<div class="text-muted" style="font-size:12px;">Immediate Remediation (2026–2028)</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f'<div class="quantum-card">'
                f'<div class="text-muted">PHASE 2 (MEDIUM-TERM)</div>'
                f'<div style="font-size:32px; font-weight:700; color:#E07B39;">{p2}</div>'
                f'<div class="text-muted" style="font-size:12px;">Scheduled Transition (2028–2031)</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f'<div class="quantum-card">'
                f'<div class="text-muted">AVERAGE RISK POSTURE</div>'
                f'<div style="font-size:32px; font-weight:700; color:#3A6EA5;">{avg_risk:.1f}/100</div>'
                f'<div class="text-muted" style="font-size:12px;">Normalized Viya Analytical Index</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Export Executive Briefing Section (Ticket 12 Acceptance Criteria)
    st.markdown('<div class="section-title">Executive Briefing & Audit Export</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="quantum-card">'
        '<p style="font-size:14px; margin-bottom:16px;">Generate boardroom-ready executive briefing summaries '
        'reflecting current cryptographic posture, risk distributions, and prioritized NIST PQC roadmaps.</p>',
        unsafe_allow_html=True,
    )
    
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    
    if not df.empty:
        # Generate PDF bytes
        pdf_data = generate_pdf_report(df)
        with btn_col1:
            st.download_button(
                label="📄 Download Executive Report (PDF)",
                data=pdf_data,
                file_name="Aurelia_Bank_Quantum_Risk_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        # Generate PPTX bytes
        pptx_data = generate_pptx_report(df)
        with btn_col2:
            st.download_button(
                label="📊 Download Briefing Deck (PPTX)",
                data=pptx_data,
                file_name="Aurelia_Bank_Quantum_Risk_Briefing.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
            )
    else:
        st.info("No asset inventory loaded to export.")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Core Navigation Overview
    st.markdown('<div class="section-title">Application Modules</div>', unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(
            """
            <div class="quantum-card">
                <div style="font-size:16px; font-weight:700; color:#0B1F3A;">📋 1. Asset Inventory</div>
                <p style="font-size:13px; color:#6B7280; margin:6px 0;">
                    Manage bank cryptographic assets across Card Networks, SWIFT, and Internal PKI.
                    Supports CSV ingestion, manual key registration, and triggers the SAS Viya Scoring Engine.
                </p>
                <div style="font-size:16px; font-weight:700; color:#0B1F3A; margin-top:16px;">🗺️ 2. Risk Exposure Heatmap</div>
                <p style="font-size:13px; color:#6B7280; margin:6px 0;">
                    Interactive cross-tabulation mapping asset volume across business system categories
                    and risk severity tiers (Critical, High, Medium, Low).
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m_col2:
        st.markdown(
            """
            <div class="quantum-card">
                <div style="font-size:16px; font-weight:700; color:#0B1F3A;">🚀 3. Migration Roadmap & Phasing</div>
                <p style="font-size:13px; color:#6B7280; margin:6px 0;">
                    Three-phase strategic remediation board bucketing assets into Phase 1 (urgent),
                    Phase 2 (mid-term), and Phase 3 with target NIST FIPS 203/204/205 replacements.
                </p>
                <div style="font-size:16px; font-weight:700; color:#0B1F3A; margin-top:16px;">🧪 4. Scenario Simulator ("What-If")</div>
                <p style="font-size:13px; color:#6B7280; margin:6px 0;">
                    Stress-test risk postures under Accelerated Quantum Breakthrough or hardware
                    bottleneck scenarios, observing real-time phase migration shifts.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
