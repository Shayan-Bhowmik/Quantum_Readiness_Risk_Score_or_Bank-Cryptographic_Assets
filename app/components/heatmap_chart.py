"""
Risk Heatmap Plotly Component
Aggregates bank cryptographic assets by System Category and Risk Band,
rendering an interactive heatmap styled according to the UI Design System tokens.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Tuple

# UI Design System Color Palette (Rule 11)
COLOR_PALETTE = {
    "Low": "#2E8B57",       # Low Risk - Forest Green
    "Medium": "#E4B429",    # Medium Risk - Amber Yellow
    "High": "#E07B39",      # High Risk - Coral Orange
    "Critical": "#C0392B",  # Critical Risk - Deep Crimson
    "Navy": "#0B1F3A",
    "SteelBlue": "#3A6EA5",
    "Surface": "#FFFFFF",
    "Border": "#E2E5EA",
}

SYSTEM_CATEGORIES = ["Card Network", "SWIFT", "Internal PKI"]
RISK_BANDS = ["Low", "Medium", "High", "Critical"]

def classify_risk_band(score: float) -> str:
    """Classifies numeric risk score (0-100) into standardized Risk Band."""
    if score >= 75.0:
        return "Critical"
    elif score >= 50.0:
        return "High"
    elif score >= 25.0:
        return "Medium"
    else:
        return "Low"

def prepare_heatmap_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, list, list]:
    """
    Transforms asset inventory into a 2D pivot table of asset counts.
    Rows: System Category (Card Network, SWIFT, Internal PKI)
    Columns: Risk Band (Low, Medium, High, Critical)
    """
    if df.empty or "risk_score" not in df.columns or "system_category" not in df.columns:
        empty_matrix = pd.DataFrame(0, index=SYSTEM_CATEGORIES, columns=RISK_BANDS)
        return empty_matrix, SYSTEM_CATEGORIES, RISK_BANDS
        
    working_df = df.copy()
    working_df["risk_band"] = working_df["risk_score"].apply(classify_risk_band)
    
    # Create cross-tabulation
    ct = pd.crosstab(
        index=working_df["system_category"],
        columns=working_df["risk_band"]
    )
    
    # Ensure all required categories and risk bands are present even if count is 0
    matrix = ct.reindex(index=SYSTEM_CATEGORIES, columns=RISK_BANDS, fill_value=0)
    return matrix, SYSTEM_CATEGORIES, RISK_BANDS

def render_heatmap_figure(df: pd.DataFrame) -> go.Figure:
    """
    Constructs a responsive Plotly Figure representing the Cryptographic Risk Heatmap.
    """
    matrix, categories, bands = prepare_heatmap_data(df)
    z_values = matrix.values
    
    # Custom hover text with contextual details
    hover_text = [
        [
            f"<b>Category:</b> {cat}<br><b>Risk Tier:</b> {band}<br><b>Asset Count:</b> {z_values[i][j]} assets"
            for j, band in enumerate(bands)
        ]
        for i, cat in enumerate(categories)
    ]
    
    # Custom text annotations inside each cell
    annotations = []
    for i, cat in enumerate(categories):
        for j, band in enumerate(bands):
            val = z_values[i][j]
            # White text for high contrast on darker cards, dark text on lighter
            font_color = "#FFFFFF" if val > 0 else "#6B7280"
            annotations.append(
                dict(
                    x=band,
                    y=cat,
                    text=f"<b>{val}</b>",
                    font=dict(family="Inter, sans-serif", size=18, color=font_color),
                    showarrow=False,
                )
            )

    # Gradient colorscale matching Navy -> Steel Blue -> Amber -> Critical Crimson
    custom_colorscale = [
        [0.0, "#F7F9FC"],       # Empty/baseline - background color
        [0.2, "#3A6EA5"],       # Low volume - Steel Blue
        [0.5, "#E4B429"],       # Medium volume - Amber
        [0.75, "#E07B39"],      # High volume - Coral Orange
        [1.0, "#C0392B"],       # Critical volume - Deep Crimson
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=bands,
            y=categories,
            text=hover_text,
            hoverinfo="text",
            colorscale=custom_colorscale,
            showscale=True,
            colorbar=dict(
                title=dict(text="Asset Count", font=dict(family="Inter", size=12)),
                thickness=16,
                len=0.8,
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Cryptographic Exposure Heatmap</b> (Assets by Category & Risk Band)",
            font=dict(family="Inter, sans-serif", size=18, color=COLOR_PALETTE["Navy"]),
            x=0.0,
            y=0.98,
        ),
        xaxis=dict(
            title=dict(text="Risk Severity Band", font=dict(family="Inter", size=14, color=COLOR_PALETTE["Navy"])),
            tickfont=dict(family="Inter", size=13, color=COLOR_PALETTE["Navy"]),
            side="bottom",
        ),
        yaxis=dict(
            title=dict(text="Banking Infrastructure System", font=dict(family="Inter", size=14, color=COLOR_PALETTE["Navy"])),
            tickfont=dict(family="Inter", size=13, color=COLOR_PALETTE["Navy"]),
            autorange="reversed",  # Keeps Card Network at top
        ),
        annotations=annotations,
        margin=dict(l=60, r=40, t=60, b=50),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=450,
    )

    return fig
