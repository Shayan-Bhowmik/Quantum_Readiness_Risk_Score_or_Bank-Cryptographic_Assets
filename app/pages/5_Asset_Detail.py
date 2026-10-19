import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Configure Page
st.set_page_config(
    page_title="Asset Detail Drilldown | Quantum-Readiness Risk Score",
    page_icon="🔍",
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

st.markdown('<div class="page-title">Cryptographic Asset Detail & Risk Attribution</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="text-muted">Deep-dive technical specification, risk factor decomposition, '
    'and NIST Post-Quantum Cryptography transition guidance for individual assets.</p>',
    unsafe_allow_html=True,
)

df = st.session_state.assets_df

if df.empty:
    st.warning("Empty State: No assets available. Please load assets via the 'Asset Inventory' module.")
else:
    # 1. Asset Selector
    asset_options = {
        f"#{row['asset_id']} - {row['asset_name']} ({row['algorithm']}-{row['key_size_bits']})": row['asset_id']
        for _, row in df.iterrows()
    }
    
    # Check if a specific asset was pre-selected in session state
    default_idx = 0
    if "selected_asset_id" in st.session_state:
        target_id = st.session_state.selected_asset_id
        for idx, (label, a_id) in enumerate(asset_options.items()):
            if a_id == target_id:
                default_idx = idx
                break

    selected_label = st.selectbox("Select Cryptographic Asset to Inspect:", list(asset_options.keys()), index=default_idx)
    selected_asset_id = asset_options[selected_label]
    asset = df[df["asset_id"] == selected_asset_id].iloc[0]

    st.markdown("---")

    # 2. Executive Header Banner
    score = float(asset.get("risk_score", 0.0))
    if score >= 75.0:
        badge_bg = "#C0392B"
        risk_label = "CRITICAL RISK"
    elif score >= 50.0:
        badge_bg = "#E07B39"
        risk_label = "HIGH RISK"
    elif score >= 25.0:
        badge_bg = "#E4B429"
        risk_label = "MEDIUM RISK"
    else:
        badge_bg = "#2E8B57"
        risk_label = "LOW RISK"

    header_html = f"""
    <div class="quantum-card" style="display:flex; justify-content:space-between; align-items:center; background:linear-gradient(135deg, #0B1F3A 0%, #1A365D 100%); color:#FFFFFF; padding:24px;">
        <div>
            <div style="font-size:13px; text-transform:uppercase; letter-spacing:1px; color:#90CDF4; font-weight:600;">Asset #{asset['asset_id']} • {asset['system_category']}</div>
            <div style="font-size:24px; font-weight:700; color:#FFFFFF; margin-top:4px;">{asset['asset_name']}</div>
            <div style="font-size:14px; color:#E2E8F0; margin-top:6px;">
                Algorithm: <span class="mono-text" style="color:#63B3ED; font-weight:600;">{asset['algorithm']}-{asset['key_size_bits']} bits</span>
                &nbsp;|&nbsp; Target Horizon: <b>{asset['migration_phase']}</b>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:11px; text-transform:uppercase; color:#CBD5E0; font-weight:600;">Quantum Risk Score</div>
            <div style="font-size:38px; font-weight:800; color:#FFFFFF; margin-top:-2px;">{score:.1f}<span style="font-size:20px; font-weight:400; color:#CBD5E0;">/100</span></div>
            <div style="background-color:{badge_bg}; color:#FFFFFF; padding:3px 12px; border-radius:12px; font-size:12px; font-weight:700; display:inline-block; margin-top:4px;">{risk_label}</div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # 3. Two-Column Diagnostic Layout
    col_left, col_right = st.columns([1, 1])

    with col_left:
        # Technical Metadata Specifications
        st.markdown('<div class="section-title">Cryptographic Specification</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="quantum-card">
                <table style="width:100%; border-collapse:collapse; font-size:14px;">
                    <tr style="border-bottom:1px solid #E2E5EA;">
                        <td style="padding:10px 0; color:#6B7280;">System Category</td>
                        <td style="padding:10px 0; font-weight:600; text-align:right;">{asset['system_category']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E5EA;">
                        <td style="padding:10px 0; color:#6B7280;">Cryptographic Algorithm</td>
                        <td style="padding:10px 0; font-weight:600; text-align:right;" class="mono-text">{asset['algorithm']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E5EA;">
                        <td style="padding:10px 0; color:#6B7280;">Key Length</td>
                        <td style="padding:10px 0; font-weight:600; text-align:right;" class="mono-text">{asset['key_size_bits']} bits</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E5EA;">
                        <td style="padding:10px 0; color:#6B7280;">Data Sensitivity Tier</td>
                        <td style="padding:10px 0; font-weight:600; text-align:right;">{asset['data_sensitivity']}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E5EA;">
                        <td style="padding:10px 0; color:#6B7280;">Estimated Years to Quantum Break</td>
                        <td style="padding:10px 0; font-weight:600; text-align:right; color:#C0392B;">{float(asset['estimated_years_to_break']):.1f} years</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2E5EA;">
                        <td style="padding:10px 0; color:#6B7280;">Migration Complexity / Cost Rating</td>
                        <td style="padding:10px 0; font-weight:600; text-align:right;">{float(asset['migration_cost_score']):.1f} / 10.0</td>
                    </tr>
                    <tr>
                        <td style="padding:10px 0; color:#6B7280;">Last Inventory Assessment</td>
                        <td style="padding:10px 0; color:#6B7280; text-align:right; font-size:12px;">{str(asset.get('updated_at', '2026-10-20'))[:10]}</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Target NIST PQC Migration Card
        st.markdown('<div class="section-title">Recommended NIST PQC Standard</div>', unsafe_allow_html=True)
        pqc_target = asset.get("recommended_pqc_algorithm", "CRYSTALS-Dilithium (ML-DSA)")
        
        # Domain context explanation for PQC replacement
        if "Dilithium" in pqc_target or "ML-DSA" in pqc_target:
            pqc_desc = "NIST FIPS 204 Lattice-based digital signature algorithm replacing legacy RSA/DSA signing schemes with quantum-resilient module lattices."
        elif "Kyber" in pqc_target or "ML-KEM" in pqc_target:
            pqc_desc = "NIST FIPS 203 Lattice-based key encapsulation mechanism replacing discrete logarithm Diffie-Hellman and ECDH key exchanges."
        elif "SPHINCS" in pqc_target or "SLH-DSA" in pqc_target:
            pqc_desc = "NIST FIPS 205 Stateless hash-based digital signature algorithm providing defense-in-depth alternative to lattice assumptions."
        else:
            pqc_desc = "Quantum-resistant symmetric architecture requiring 256-bit key length to withstand Grover quantum speedup search."

        st.markdown(
            f"""
            <div class="quantum-card" style="border-left: 5px solid #219653; background-color:#F7F9FC;">
                <div style="font-size:12px; font-weight:700; color:#219653; text-transform:uppercase;">NIST FIPS Validated Replacement</div>
                <div style="font-size:20px; font-weight:700; color:#0B1F3A; margin:6px 0;">{pqc_target}</div>
                <div style="font-size:13px; color:#4B5563; line-height:1.5;">{pqc_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        # Risk Score Breakdown & Attribution
        st.markdown('<div class="section-title">Risk Score Attribution Breakdown</div>', unsafe_allow_html=True)
        
        # Calculate component proportions
        sens_map = {"Critical": 4.0, "High": 3.0, "Medium": 2.0, "Low": 1.0}
        s_val = sens_map.get(str(asset["data_sensitivity"]).title(), 2.0)
        years = max(float(asset["estimated_years_to_break"]), 0.25)
        time_urgency = 1.0 / years
        cost = max(float(asset["migration_cost_score"]), 1.0)
        
        # Relative weights for attribution bar
        # Raw = S * (1/T) * C
        # Log contribution breakdown or normalized weighted share
        part_sens = s_val * 20.0
        part_urgency = min(50.0, time_urgency * 15.0 * 2.5)
        part_cost = cost * 2.0
        
        # Plain-English Driver Diagnosis (Acceptance Criteria)
        if years <= 3.0 and s_val >= 3.0:
            driver_explanation = "🚨 <b>High risk mainly due to short years-to-break</b> compounded by critical/high customer financial data exposure."
            driver_color = "#FDEDEC"
            driver_border = "#C0392B"
        elif years <= 4.0:
            driver_explanation = "⚠️ <b>Elevated risk driven primarily by imminent quantum timeline</b> (< 4 years before cryptographic obsolescence)."
            driver_color = "#FDEDEC"
            driver_border = "#E07B39"
        elif cost >= 7.5:
            driver_explanation = "ℹ️ <b>Moderate risk influenced significantly by high migration complexity & HSM replacement cost</b>."
            driver_color = "#FEF9E7"
            driver_border = "#E4B429"
        else:
            driver_explanation = "🛡️ <b>Low overall risk</b> supported by healthy quantum break runway and manageable migration scope."
            driver_color = "#EAFAF1"
            driver_border = "#2E8B57"

        st.markdown(
            f"""
            <div style="background-color:{driver_color}; border-left:4px solid {driver_border}; border-radius:6px; padding:12px 16px; margin-bottom:16px; font-size:14px; color:#1B1F27;">
                {driver_explanation}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Plotly Risk Attribution Bar Chart
        factors = ["Data Sensitivity Tier", "Time-to-Break Urgency", "Migration Cost Rating"]
        values = [round(part_sens, 1), round(part_urgency, 1), round(part_cost, 1)]
        colors = ["#3A6EA5", "#C0392B", "#E4B429"]

        fig_breakdown = go.Figure(
            data=[
                go.Bar(
                    x=values,
                    y=factors,
                    orientation="h",
                    marker=dict(color=colors, line=dict(color="#0B1F3A", width=1)),
                    text=[f"{v:.1f} pts" for v in values],
                    textposition="auto",
                )
            ]
        )

        fig_breakdown.update_layout(
            title=dict(
                text="<b>Factor Impact on Total Risk Score</b>",
                font=dict(family="Inter", size=14, color="#0B1F3A"),
            ),
            xaxis=dict(title=dict(text="Relative Attribution Points", font=dict(family="Inter", size=12))),
            yaxis=dict(autorange="reversed", tickfont=dict(family="Inter", size=12)),
            margin=dict(l=20, r=20, t=40, b=30),
            height=240,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )

        st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_breakdown, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
