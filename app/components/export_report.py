"""
Executive Report Export Engine
Generates downloadable C-suite briefing materials in PDF (fpdf2) and PowerPoint (python-pptx)
summarizing bank cryptographic posture, risk distribution, and PQC migration phasing.
"""

import io
from datetime import datetime, timezone
import pandas as pd
from fpdf import FPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def generate_pdf_report(df: pd.DataFrame) -> bytes:
    """
    Generates a professional executive risk briefing PDF using fpdf2.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header Banner - Navy
    pdf.set_fill_color(11, 31, 58)  # Primary Navy #0B1F3A
    pdf.rect(0, 0, 210, 36, "F")
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(15, 10)
    pdf.cell(0, 8, "Quantum-Readiness Risk Score", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 19)
    pdf.cell(0, 6, "Executive Cryptographic Asset & PQC Migration Briefing", ln=True)
    
    pdf.set_text_color(27, 31, 39)
    pdf.set_xy(15, 42)
    
    # Metadata Block
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 6, f"Generated: {now_str} | Banking Track | SAS Viya Analytical Posture", ln=True)
    pdf.ln(3)

    # Executive Summary Metrics
    total_assets = len(df)
    p1_count = len(df[df["migration_phase"] == "Phase 1"])
    p2_count = len(df[df["migration_phase"] == "Phase 2"])
    p3_count = len(df[df["migration_phase"] == "Phase 3"])
    avg_score = df["risk_score"].mean() if not df.empty else 0.0

    pdf.set_fill_color(247, 249, 252)  # #F7F9FC
    pdf.set_draw_color(226, 229, 234)  # #E2E5EA
    pdf.rect(15, 52, 180, 26, "DF")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(11, 31, 58)
    pdf.set_xy(20, 56)
    pdf.cell(42, 6, "Total Inventory", ln=False)
    pdf.cell(42, 6, "Phase 1 (Urgent)", ln=False)
    pdf.cell(42, 6, "Phase 2 (Mid-Term)", ln=False)
    pdf.cell(42, 6, "Average Risk", ln=True)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(20, 63)
    pdf.cell(42, 8, str(total_assets), ln=False)
    pdf.set_text_color(192, 57, 43)  # Critical Red
    pdf.cell(42, 8, str(p1_count), ln=False)
    pdf.set_text_color(224, 123, 57)  # High Orange
    pdf.cell(42, 8, str(p2_count), ln=False)
    pdf.set_text_color(11, 31, 58)
    pdf.cell(42, 8, f"{avg_score:.1f}/100", ln=True)
    pdf.ln(10)

    # Section 1: Phased Roadmap Breakdown
    pdf.set_text_color(11, 31, 58)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Strategic Remediation Phasing Summary", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 5, 
        "- Phase 1 (2026-2028): Focus on SWIFT transaction signing & high-volume payment gateways (ML-DSA / ML-KEM).\n"
        "- Phase 2 (2028-2031): Transition of internal PKI, core banking TLS, and column encryption keys.\n"
        "- Phase 3 (2031-2035): Root Certificate Authorities, legacy archived signing keys, and firmware roots."
    )
    pdf.ln(5)

    # Section 2: Top Urgent Phase 1 Assets Table
    pdf.set_text_color(11, 31, 58)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. High-Priority Remediation Target Assets (Phase 1)", ln=True)
    
    # Table Header
    pdf.set_fill_color(58, 110, 165)  # Secondary Steel Blue #3A6EA5
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(12, 7, "ID", 1, 0, "C", fill=True)
    pdf.cell(60, 7, "Asset Name", 1, 0, "L", fill=True)
    pdf.cell(26, 7, "System", 1, 0, "L", fill=True)
    pdf.cell(22, 7, "Legacy Algo", 1, 0, "C", fill=True)
    pdf.cell(42, 7, "Recommended PQC", 1, 0, "L", fill=True)
    pdf.cell(18, 7, "Risk Score", 1, 1, "C", fill=True)

    # Table Rows
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(27, 31, 39)
    
    top_assets = df.sort_values(by="risk_score", ascending=False).head(15)
    fill = False
    for _, row in top_assets.iterrows():
        pdf.set_fill_color(247, 249, 252) if fill else pdf.set_fill_color(255, 255, 255)
        name = str(row.get("asset_name", ""))[:32]
        algo = f"{row.get('algorithm', '')}-{row.get('key_size_bits', '')}"
        pqc = str(row.get("recommended_pqc_algorithm", "NIST PQC"))[:24]
        
        pdf.cell(12, 6, str(row.get("asset_id", "")), 1, 0, "C", fill=fill)
        pdf.cell(60, 6, name, 1, 0, "L", fill=fill)
        pdf.cell(26, 6, str(row.get("system_category", "")), 1, 0, "L", fill=fill)
        pdf.cell(22, 6, algo, 1, 0, "C", fill=fill)
        pdf.cell(42, 6, pqc, 1, 0, "L", fill=fill)
        pdf.cell(18, 6, f"{float(row.get('risk_score', 0)):.1f}", 1, 1, "C", fill=fill)
        fill = not fill

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 5, "Compliant with NIST SP 800-56B, FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA).", ln=True)

    return bytes(pdf.output())

def generate_pptx_report(df: pd.DataFrame) -> bytes:
    """
    Generates an executive PowerPoint briefing deck (.pptx) using python-pptx.
    """
    prs = Presentation()
    
    # Slide 1: Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide1 = prs.slides.add_slide(title_slide_layout)
    title = slide1.shapes.title
    subtitle = slide1.placeholders[1]
    
    title.text = "Quantum-Readiness Risk Score"
    subtitle.text = f"Bank Cryptographic Asset Inventory & PQC Roadmap\nGenerated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    
    # Slide 2: Executive Summary Slide
    bullet_slide_layout = prs.slide_layouts[1]
    slide2 = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide2.shapes
    
    title_shape = shapes.title
    title_shape.text = "Executive Risk Posture Overview"
    
    body_shape = shapes.placeholders[1]
    tf = body_shape.text_frame
    
    total_assets = len(df)
    p1 = len(df[df["migration_phase"] == "Phase 1"])
    p2 = len(df[df["migration_phase"] == "Phase 2"])
    p3 = len(df[df["migration_phase"] == "Phase 3"])
    avg_score = df["risk_score"].mean() if not df.empty else 0.0

    p = tf.add_paragraph()
    p.text = f"Total Evaluated Cryptographic Assets: {total_assets}"
    p.font.size = Pt(18)
    p.font.bold = True
    
    p = tf.add_paragraph()
    p.text = f"Average Enterprise Quantum Risk Score: {avg_score:.1f} / 100.0"
    p.font.size = Pt(16)
    
    p = tf.add_paragraph()
    p.text = f"Phase 1 Remediation (Critical Priority, 2026-2028): {p1} assets"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(192, 57, 43)
    
    p = tf.add_paragraph()
    p.text = f"Phase 2 Remediation (Medium-Term, 2028-2031): {p2} assets"
    p.font.size = Pt(14)
    
    p = tf.add_paragraph()
    p.text = f"Phase 3 Remediation (Long-Term Horizon, 2031-2035): {p3} assets"
    p.font.size = Pt(14)
    
    p = tf.add_paragraph()
    p.text = "Target Architecture: Migration to NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA)."
    p.font.size = Pt(13)
    p.font.italic = True
    
    pptx_io = io.BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()
