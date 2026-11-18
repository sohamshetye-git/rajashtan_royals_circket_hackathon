"""
Official Competition Submission Generator (ReportLab PDF)
Strictly aligned with Round 1 Problem Statement:
- Pure pressure performance measurement and reliability.
- Zero auction/retention commentary.
- Clearly explains:
  1. How pressure is defined (continuous pre-delivery formula).
  2. How performance is evaluated (RAE, RPA, regularized metrics).
  3. The exact methodology used to arrive at the Top 10 lists.
  4. Robustness, validation, and sample size governance.
"""
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PROJ_DIR = r"C:\rajsathan_royals"
OUT_REPORTS = os.path.join(PROJ_DIR, "outputs", "reports")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")
OUT_CHARTS = os.path.join(PROJ_DIR, "outputs", "charts")

os.makedirs(OUT_REPORTS, exist_ok=True)

top10_bat = pd.read_csv(os.path.join(OUT_RANK, "batter_top10.csv"))
top10_bowl = pd.read_csv(os.path.join(OUT_RANK, "bowler_top10.csv"))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        if self._pageNumber > 1:
            self.drawString(54, 755, "CRISP: Context-Aware Framework for Evaluating Pressure Performance in T20 Cricket")
            self.drawRightString(612 - 54, 755, "SupeRR Selector Season 2 — Round 1 Technical Submission")
            self.setStrokeColor(colors.HexColor("#dddddd"))
            self.setLineWidth(0.5)
            self.line(54, 750, 612 - 54, 750)
            
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "ROUND 1 OFFICIAL METHODOLOGY REPORT — PRESSURE PERFORMANCE ANALYTICS")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf_report():
    pdf_path = os.path.join(OUT_REPORTS, "methodology_report.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0B2265"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#E6007E"),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#0B2265"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#222222"),
        spaceAfter=6
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#222222")
    )
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.white, alignment=1)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor("#222222"), alignment=1)
    td_left = ParagraphStyle('TDLeft', fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor("#222222"), alignment=0)

    story = []

    # Title & Header
    story.append(Paragraph("CRISP: Context-Aware Framework for Evaluating Pressure Performance in T20 Cricket", title_style))
    story.append(Paragraph("<b>SupeRR Selector Season 2 — Round 1 Technical Submission Report</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0B2265"), spaceAfter=8))

    # 1. Understanding the Problem Statement
    story.append(Paragraph("1. Competition Problem Statement & Core Objective", h1_style))
    story.append(Paragraph(
        "<b>What is Round 1 asking?</b><br/>"
        "The official Round 1 challenge is to build a data-driven system that measures how batters and bowlers perform in high-pressure match situations "
        "compared with their usual performance levels across historical IPL and T20 International data from 2022 onwards (200,999 ball-by-ball deliveries across 883 matches). "
        "The submission requires two ordered Top 10 lists (Top 10 Batters, Top 10 Bowlers) entered on Unstop, accompanied by a rigorous methodology report.<br/>"
        "<b>What is explicitly NOT required:</b> This is <i>not</i> an auction recommendation, retention, or player valuation exercise. The core evaluative objective is purely "
        "understanding how pressure is defined, how performance under pressure is mathematically measured, and proving why the Top 10 players genuinely deserve their rank.", body_style
    ))

    # Callout Box of Top 10 Selections
    summary_box = (
        "<b>Official Top 10 Selections (Entered in Unstop Dropdowns):</b><br/>"
        "• <b>Top 10 Batters:</b> 1. Sanju Samson, 2. Reeza Hendricks, 3. Suryakumar Yadav, 4. Tim David, 5. Naman Dhir, 6. Ashutosh Sharma, 7. David Miller, 8. Rishabh Pant, 9. Glenn Phillips, 10. Jos Buttler.<br/>"
        "• <b>Top 10 Bowlers:</b> 1. Sunil Narine, 2. Abrar Ahmed, 3. Mohammad Nawaz, 4. Mustafizur Rahman, 5. Jamie Overton, 6. Jasprit Bumrah, 7. Salman Mirza, 8. Mohit Sharma, 9. Matheesha Pathirana, 10. Sufiyan Muqeem."
    )
    story.append(Table([[Paragraph(summary_box, callout_style)]], colWidths=[504], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F4F6FA")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#0B2265")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(Spacer(1, 6))

    # 2. How We Define Pressure
    story.append(Paragraph("2. How Pressure is Defined: The Pre-Delivery Mathematical Formulation", h1_style))
    story.append(Paragraph(
        "We reject arbitrary heuristics like naively treating overs 16–20 as high pressure regardless of match context. A 20th over needing 4 runs with 8 wickets in hand is low pressure; "
        "an over in the 4th over after losing 3 early wickets is acute crisis. In CRISP, pressure is formulated as a continuous state variable ($P_t \\in [0.05, 0.99]$) computed immediately "
        "<b>before each delivery</b> using strictly pre-delivery variables $S_t$ (zero lookahead leakage):<br/>"
        "• <b>Innings 2 (Chasing Pressure):</b> Jointly models required acceleration via a logistic function of Required Run Rate (RRR) centered around T20 par (8.5 RPO), "
        "resource scarcity ($R_{\\text{req}} / W_{\\text{rem}}$), and closing time scarcity ($B_{\\text{rem}} / 120$). If $W_{\\text{rem}} \\le 2$ and runs are needed, $P_t \\ge 0.85$.<br/>"
        "• <b>Innings 1 (Setting Pressure):</b> Models top-order collapse depth ($W_{\\text{lost}} \\ge 3$ in powerplay or $\\ge 5$ before over 12) relative to historical par and death-overs maximization.<br/>"
        "Deliveries are categorized into: Low ($<0.40$), Moderate ($[0.40, 0.65)$), High ($[0.65, 0.80)$), and Extreme ($\\ge 0.80$). High-pressure situations constitute 22.3% of the dataset.", body_style
    ))

    p_chart = os.path.join(OUT_CHARTS, "pressure_distribution.png")
    if os.path.exists(p_chart):
        story.append(Image(p_chart, width=504, height=165))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # 3. How Performance Under Pressure is Evaluated
    story.append(Paragraph("3. How Performance Under Pressure is Evaluated", h1_style))
    story.append(Paragraph(
        "Evaluating pressure performance requires isolating context difficulty from raw execution:<br/>"
        "1. <b>Expected Performance Baselines (RAE & RPA):</b> Expected runs and wicket probabilities are conditioned on $(\\text{Innings}, \\text{Over}, W_{\\text{lost}}, \\text{Format})$. "
        "<b>Runs Above Expected (RAE)</b> measures batter run production above situational expectation; <b>Runs Prevented Above Expected (RPA)</b> measures bowler runs saved relative to situational expectation.<br/>"
        "2. <b>Sample-Size Regularization (Empirical Bayes Shrinkage):</b> To prevent 1- or 2-match flukes from outranking consistent veterans, observed strike rates and economy rates are "
        "regressed toward population priors ($w_i = n_i / (n_i + 60)$). At the minimum qualification cutoff of 100 pressure balls, player data carries 62.5% weight, safely dampening small-sample volatility.<br/>"
        "3. <b>Match Consistency:</b> Match-level variance is explicitly penalized so steady contributors outrank boom-or-bust outliers.", body_style
    ))

    # 4. Top 10 Batters Table
    story.append(Paragraph("4. Official Top 10 Batters Under Pressure (BPRI Index)", h1_style))
    bat_headers = ["Rk", "Player Name", "Mat", "Balls", "Runs", "P.SR", "P.Avg", "Norm.SR", "SR Delta", "P.RAE", "BPRI"]
    bat_data = [[Paragraph(h, th_style) for h in bat_headers]]
    for _, r in top10_bat.iterrows():
        bat_data.append([
            Paragraph(str(int(r['Rank'])), td_style),
            Paragraph(str(r['player_name']), td_left),
            Paragraph(str(int(r['p_matches'])), td_style),
            Paragraph(str(int(r['p_balls'])), td_style),
            Paragraph(str(int(r['p_runs'])), td_style),
            Paragraph(f"{r['p_sr']:.1f}", td_style),
            Paragraph(f"{r['p_avg']:.1f}", td_style),
            Paragraph(f"{r['n_sr']:.1f}", td_style),
            Paragraph(f"{r['sr_delta']:+.1f}", td_style),
            Paragraph(f"{r['p_rae']:+.1f}", td_style),
            Paragraph(f"{r['BPRI']:.2f}", td_style)
        ])

    bat_table = Table(bat_data, colWidths=[18, 105, 25, 30, 32, 38, 38, 42, 45, 45, 46])
    bat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B2265")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(bat_table)
    story.append(Spacer(1, 6))

    # 5. Top 10 Bowlers Table
    story.append(Paragraph("5. Official Top 10 Bowlers Under Pressure (Bowler_PRI Index)", h1_style))
    bowl_headers = ["Rk", "Player Name", "Mat", "Balls", "Overs", "Runs", "P.Econ", "Wkts", "Norm.Econ", "Econ Delta", "P.RPA", "PRI"]
    bowl_data = [[Paragraph(h, th_style) for h in bowl_headers]]
    for _, r in top10_bowl.iterrows():
        bowl_data.append([
            Paragraph(str(int(r['Rank'])), td_style),
            Paragraph(str(r['player_name']), td_left),
            Paragraph(str(int(r['p_matches'])), td_style),
            Paragraph(str(int(r['p_legal_balls'])), td_style),
            Paragraph(f"{r['p_overs']:.1f}", td_style),
            Paragraph(str(int(r['p_runs_conceded'])), td_style),
            Paragraph(f"{r['p_econ']:.2f}", td_style),
            Paragraph(str(int(r['p_wickets'])), td_style),
            Paragraph(f"{r['n_econ']:.2f}", td_style),
            Paragraph(f"{r['econ_delta']:+.2f}", td_style),
            Paragraph(f"{r['p_rpa']:+.1f}", td_style),
            Paragraph(f"{r['Bowler_PRI']:.2f}", td_style)
        ])

    bowl_table = Table(bowl_data, colWidths=[18, 102, 25, 28, 30, 30, 38, 28, 45, 45, 45, 45])
    bowl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B2265")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(bowl_table)
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # 6. Statistical Reliability & Bootstrap Validation
    story.append(Paragraph("6. Statistical Reliability, ML Validation & Stability Audit", h1_style))
    story.append(Paragraph(
        "<b>Predictive Out-of-Sample Validation:</b> Chronological train/test split (Train: 2022–2024, 116,228 balls; Test: 2025–2026, 77,786 balls) verified zero future leakage "
        "and accurate calibration (Test MAE: 1.31 runs, Test RMSE: 1.76 runs, Wicket Brier Score: 0.0489).<br/>"
        "<b>2,000 Match-Clustered Bootstrap Iterations:</b> Vectorized cluster resampling verified ranking robustness. Multi-season anchors demonstrated extraordinary stability: "
        "Sunil Narine (99.9% Top-15 appearance), Suryakumar Yadav (96.3%), Tim David (91.2%), Mustafizur Rahman (94.4%), and Jasprit Bumrah (79.4%). Specialized finishers "
        "(Naman Dhir, Ashutosh Sharma, Salman Mirza) show expected context sensitivity across resampled matches while remaining elite in their dedicated roles.", body_style
    ))

    stab_chart = os.path.join(OUT_CHARTS, "ranking_stability.png")
    if os.path.exists(stab_chart):
        story.append(Image(stab_chart, width=504, height=175))
        story.append(Spacer(1, 6))

    # 7. Limitations & Scientific Transparency
    story.append(Paragraph("7. Methodological Limitations & Transparency", h1_style))
    story.append(Paragraph(
        "1. <b>Tracking Limitations:</b> Ball speed and delivery style are provided, but pitch tracking coordinates and seam/swing measurements are absent from the dataset.<br/>"
        "2. <b>Asymmetry in Chasing vs Setting:</b> In T20 cricket, chasing provides hard mathematical boundaries (known RRR and wickets in hand), resulting in 33.6% high-pressure deliveries "
        "compared to 12.1% in the first innings. CRISP accounts for this by conditioning expected runs directly on innings number.<br/>"
        "3. <b>Conclusion:</b> This methodology is transparent, statistically grounded, fully reproducible, and aligned strictly with the official Round 1 problem statement.", body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Official Competition Methodology PDF Report rebuilt: {pdf_path}")

if __name__ == '__main__':
    build_pdf_report()
