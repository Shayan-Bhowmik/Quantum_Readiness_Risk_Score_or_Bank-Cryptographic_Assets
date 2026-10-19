"""
Roadmap Timeline Component
Generates an executive Gantt-style transition timeline for Phase 1, 2, and 3
migration horizons, aligning banking cryptographic modernization with NIST PQC milestones.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_roadmap_gantt() -> go.Figure:
    """
    Renders an executive high-level timeline showing migration horizons:
    - Phase 1 (Urgent/Critical): 2026 - 2028
    - Phase 2 (Medium-term): 2028 - 2031
    - Phase 3 (Long-term / Root PKI): 2031 - 2035
    """
    timeline_data = [
        dict(
            Phase="Phase 1: Critical Urgency",
            Start="2026-01-01",
            End="2028-12-31",
            Focus="SWIFT Transaction Signing & High-Volume Card Network Keys (ML-DSA / ML-KEM)",
            Color="#C0392B",  # Risk Critical Crimson
        ),
        dict(
            Phase="Phase 2: Medium-Term",
            Start="2028-01-01",
            End="2031-12-31",
            Focus="Internal Application TLS, VPNs & Database Column Keys",
            Color="#E07B39",  # Risk High Coral
        ),
        dict(
            Phase="Phase 3: Long-Term Horizon",
            Start="2031-01-01",
            End="2035-12-31",
            Focus="Offline Root CAs, Archived Master Signing & Firmware Roots",
            Color="#2E8B57",  # Risk Low Green
        ),
    ]
    
    df_timeline = pd.DataFrame(timeline_data)
    
    fig = px.timeline(
        df_timeline,
        x_start="Start",
        x_end="End",
        y="Phase",
        color="Phase",
        color_discrete_map={row["Phase"]: row["Color"] for row in timeline_data},
        hover_data={"Focus": True, "Start": True, "End": True, "Phase": False},
    )
    
    fig.update_yaxes(autorange="reversed")  # Phase 1 on top
    fig.update_layout(
        title=dict(
            text="<b>Bank Migration Execution Horizon (2026 – 2035)</b>",
            font=dict(family="Inter, sans-serif", size=16, color="#0B1F3A"),
            x=0.0,
        ),
        xaxis=dict(
            title=dict(text="Target Completion Timeline", font=dict(family="Inter", size=13)),
            tickfont=dict(family="Inter", size=12),
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(family="Inter", size=13, color="#0B1F3A"),
        ),
        height=260,
        margin=dict(l=20, r=20, t=50, b=30),
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    )
    
    return fig
