import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.logic.scoring import calculate_single_risk_score
from app.components.heatmap_chart import render_heatmap_figure

# Configure Page
st.set_page_config(
    page_title="Scenario Simulator | Quantum-Readiness Risk Score",
    page_icon="🧪",
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

st.markdown('<div class="page-title">Quantum Threat Scenario Simulator ("What-If")</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="text-muted">Stress-test bank cryptographic assets against varying quantum hardware '
    'development trajectories and cost pressures without altering baseline inventory records.</p>',
    unsafe_allow_html=True,
)

base_df = st.session_state.assets_df

if base_df.empty:
    st.warning("Empty State: No assets available. Please load assets via the 'Asset Inventory' module.")
else:
    # 1. Simulator Controls Container
    st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="margin-top:0;">Simulation Assumptions & Levers</div>', unsafe_allow_html=True)
    
    ctrl_col1, ctrl_col2 = st.columns(2)
    
    with ctrl_col1:
        progression = st.select_slider(
            "⚡ Quantum Progress Trajectory:",
            options=["Slow", "Expected", "Fast"],
            value="Expected",
            help="Simulates geopolitical / lab breakthroughs. 'Fast' shrinks quantum break timelines by 40%."
        )
        
    with ctrl_col2:
        cost_multiplier = st.slider(
            "💰 Migration Complexity / Vendor Cost Multiplier:",
            min_value=0.8,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Simulates talent shortages or HSM supply chain inflation increasing remediation costs."
        )

    # Narrative explanation of assumption
    if progression == "Slow":
        traj_desc = "🐢 <b>Slow Trajectory:</b> Quantum error-correction engineering bottlenecks add +3.0 years to all break estimates."
        time_factor = 1.4  # Runway extended
    elif progression == "Fast":
        traj_desc = "🚀 <b>Fast / Accelerated Breakthrough:</b> Rapid progress in logical qubits compresses break timelines by 40%."
        time_factor = 0.6  # Runway compressed
    else:
        traj_desc = "⚖️ <b>Expected Consensus:</b> Standard NIST & academic Mosca theorem timelines."
        time_factor = 1.0

    st.markdown(
        f'<div style="background-color:#F7F9FC; border-left:4px solid #3A6EA5; padding:8px 12px; border-radius:4px; font-size:13px; color:#1B1F27;">'
        f'{traj_desc} &nbsp;|&nbsp; Cost inflation factor: <b>{cost_multiplier:.1f}x</b>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Dynamic Live Re-Scoring Engine (In-Memory What-If Simulation)
    sim_df = base_df.copy()
    sim_scores = []
    sim_phases = []
    
    for _, row in sim_df.iterrows():
        base_years = float(row.get("estimated_years_to_break", 7.0))
        sim_years = max(0.5, base_years * time_factor)
        
        base_cost = float(row.get("migration_cost_score", 5.0))
        sim_cost = min(10.0, max(1.0, base_cost * cost_multiplier))
        
        res = calculate_single_risk_score(
            data_sensitivity=row.get("data_sensitivity", "Medium"),
            estimated_years_to_break=sim_years,
            migration_cost_score=sim_cost,
            algorithm=row.get("algorithm", "RSA"),
            key_size_bits=row.get("key_size_bits", 2048),
        )
        sim_scores.append(res["risk_score"])
        sim_phases.append(res["migration_phase"])
        
    sim_df["risk_score"] = sim_scores
    sim_df["migration_phase"] = sim_phases

    # 3. Before-and-After Comparative KPI Delta Cards
    base_p1 = len(base_df[base_df["migration_phase"] == "Phase 1"])
    sim_p1 = len(sim_df[sim_df["migration_phase"] == "Phase 1"])
    p1_delta = sim_p1 - base_p1

    base_p2 = len(base_df[base_df["migration_phase"] == "Phase 2"])
    sim_p2 = len(sim_df[sim_df["migration_phase"] == "Phase 2"])
    p2_delta = sim_p2 - base_p2

    base_p3 = len(base_df[base_df["migration_phase"] == "Phase 3"])
    sim_p3 = len(sim_df[sim_df["migration_phase"] == "Phase 3"])
    p3_delta = sim_p3 - base_p3

    base_avg = base_df["risk_score"].mean()
    sim_avg = sim_df["risk_score"].mean()
    avg_delta = sim_avg - base_avg

    st.markdown('<div class="section-title">Scenario Impact vs. Baseline Posture</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric(
        "🚨 Phase 1 Assets",
        f"{sim_p1}",
        delta=f"{p1_delta:+d} assets" if p1_delta != 0 else "0 (No change)",
        delta_color="inverse"
    )
    c2.metric(
        "⚠️ Phase 2 Assets",
        f"{sim_p2}",
        delta=f"{p2_delta:+d} assets" if p2_delta != 0 else "0 (No change)",
        delta_color="off"
    )
    c3.metric(
        "🛡️ Phase 3 Assets",
        f"{sim_p3}",
        delta=f"{p3_delta:+d} assets" if p3_delta != 0 else "0 (No change)",
        delta_color="normal"
    )
    c4.metric(
        "Average Risk Score",
        f"{sim_avg:.1f}",
        delta=f"{avg_delta:+.1f} pts" if abs(avg_delta) >= 0.1 else "0.0 pts",
        delta_color="inverse"
    )

    # 4. Comparative Heatmap & Live Phasing Shift Analysis
    heat_col, chart_col = st.columns([1, 1])

    with heat_col:
        st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
        st.markdown('<b>Simulated Cryptographic Exposure Heatmap</b>', unsafe_allow_html=True)
        sim_heat_fig = render_heatmap_figure(sim_df)
        st.plotly_chart(sim_heat_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col:
        st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
        st.markdown('<b>Phase Distribution: Baseline vs. Simulated</b>', unsafe_allow_html=True)
        
        phase_labels = ["Phase 1 (Urgent)", "Phase 2 (Mid-Term)", "Phase 3 (Long-Term)"]
        baseline_counts = [base_p1, base_p2, base_p3]
        simulated_counts = [sim_p1, sim_p2, sim_p3]
        
        fig_bar = go.Figure(data=[
            go.Bar(name='Baseline Inventory', x=phase_labels, y=baseline_counts, marker_color='#3A6EA5'),
            go.Bar(name='Simulated Scenario', x=phase_labels, y=simulated_counts, marker_color='#C0392B' if progression == 'Fast' else '#2E8B57')
        ])
        fig_bar.update_layout(
            barmode='group',
            margin=dict(l=20, r=20, t=30, b=30),
            height=370,
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title=dict(text="Number of Assets", font=dict(family="Inter", size=12)))
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. Live Assets Transition Table
    st.markdown('<div class="section-title">Assets Experiencing Phase Transition</div>', unsafe_allow_html=True)
    
    # Merge baseline and simulated to identify changed assets
    compare_df = pd.DataFrame({
        "asset_id": base_df["asset_id"],
        "asset_name": base_df["asset_name"],
        "system_category": base_df["system_category"],
        "algorithm": base_df["algorithm"],
        "key_size_bits": base_df["key_size_bits"],
        "baseline_phase": base_df["migration_phase"],
        "simulated_phase": sim_df["migration_phase"],
        "baseline_score": base_df["risk_score"],
        "simulated_score": sim_df["risk_score"],
        "score_delta": (sim_df["risk_score"] - base_df["risk_score"]).round(1),
        "target_pqc": sim_df["recommended_pqc_algorithm"],
    })
    
    shifted_assets = compare_df[compare_df["baseline_phase"] != compare_df["simulated_phase"]]

    if shifted_assets.empty:
        st.info("Under current simulation levers, all assets remain in their baseline phases.")
    else:
        st.warning(f"🚨 **{len(shifted_assets)} assets have shifted phases** under this '{progression}' scenario!")
        st.dataframe(
            shifted_assets,
            use_container_width=True,
            hide_index=True,
            column_config={
                "asset_id": st.column_config.NumberColumn("ID", width="small"),
                "asset_name": st.column_config.TextColumn("Asset Name", width="large"),
                "system_category": st.column_config.TextColumn("Category", width="medium"),
                "baseline_phase": st.column_config.TextColumn("Baseline Phase", width="small"),
                "simulated_phase": st.column_config.TextColumn("Simulated Phase", width="small"),
                "baseline_score": st.column_config.NumberColumn("Base Score", format="%.1f", width="small"),
                "simulated_score": st.column_config.NumberColumn("Sim Score", format="%.1f", width="small"),
                "score_delta": st.column_config.NumberColumn("Delta", format="%+0.1f", width="small"),
                "target_pqc": st.column_config.TextColumn("Target PQC", width="medium"),
            }
        )
