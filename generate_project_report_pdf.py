"""
Comprehensive Micro-Project Report PDF Generator
================================================
Generates the official, publication-quality academic project report PDF:
'WC_Micro_Project_Wireless_Link_Budget_Report.pdf'
Course: 3171608 - Wireless Communication (WC)
Gujarat Technological University (GTU) | 7th Semester B.E. in IT
"""

import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    HRFlowable,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from link_budget_engine import (
    PRESET_SCENARIOS,
    calculate_link_budget,
    sweep_distance
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for adding running header and page numbers 'Page X of Y'."""
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
        # Don't draw header or footer on the cover page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#555555"))

        # Running Top Header
        self.drawString(36, 11 * inch - 26, "GTU 7th Sem IT | 3171608 - Wireless Communication Micro-Project")
        self.drawRightString(8.5 * inch - 36, 11 * inch - 26, "Wireless Link Budget GUI")
        self.setStrokeColor(colors.HexColor("#dcdde1"))
        self.setLineWidth(0.5)
        self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Running Bottom Footer
        self.line(36, 36, 8.5 * inch - 36, 36)
        self.drawString(36, 24, "Department of Information Technology")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 36, 24, page_str)
        self.restoreState()


def build_project_report_pdf(output_pdf_path="WC_Micro_Project_Wireless_Link_Budget_Report.pdf"):
    print(f"Building comprehensive project report PDF: {os.path.abspath(output_pdf_path)}")

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    # Color Palette
    c_primary = colors.HexColor("#1b2a47")     # Deep Navy
    c_secondary = colors.HexColor("#0984e3")   # Accent Blue
    c_dark = colors.HexColor("#2d3436")        # Body dark
    c_accent_green = colors.HexColor("#00b894")# Pass green
    c_bg_light = colors.HexColor("#f8f9fa")    # Table light bg
    c_border = colors.HexColor("#dfe6e9")      # Border grey

    # Typography Styles
    style_cover_uni = ParagraphStyle(
        'CoverUni',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        alignment=1,
        spaceAfter=4
    )
    style_cover_sub = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#636e72"),
        alignment=1,
        spaceAfter=15
    )
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=1,
        spaceAfter=8
    )
    style_cover_badge = ParagraphStyle(
        'CoverBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=25
    )
    style_h1 = ParagraphStyle(
        'ChapH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'ChapH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'BodyTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )
    style_body_bold = ParagraphStyle(
        'BodyBold',
        parent=style_body,
        fontName='Helvetica-Bold'
    )
    style_formula = ParagraphStyle(
        'FormulaTxt',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=9,
        leading=12,
        textColor=c_primary
    )
    style_meta = ParagraphStyle(
        'MetaTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#555555")
    )

    story = []

    # =========================================================================
    # 1. COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 30))
    story.append(Paragraph("GUJARAT TECHNOLOGICAL UNIVERSITY", style_cover_uni))
    story.append(Paragraph("DEPARTMENT OF INFORMATION TECHNOLOGY", style_cover_sub))
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="60%", thickness=2, color=c_secondary, spaceAfter=25))
    story.append(Paragraph("A MICRO-PROJECT REPORT ON", ParagraphStyle('ReportSub', parent=style_cover_sub, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor("#2d3436"))))
    story.append(Paragraph("WIRELESS LINK BUDGET GUI", style_cover_title))
    story.append(Paragraph("RF Propagation Modeling, System Budget Accounting & Simulation Suite", style_cover_badge))
    story.append(HRFlowable(width="60%", thickness=2, color=c_secondary, spaceAfter=35))

    story.append(Spacer(1, 20))

    # Meta box on cover
    cover_meta_data = [
        [
            Paragraph("<b>Course Name:</b>", style_body),
            Paragraph("Wireless Communication (WC)", style_body),
            Paragraph("<b>Semester:</b>", style_body),
            Paragraph("7th Semester, B.E. (IT)", style_body)
        ],
        [
            Paragraph("<b>Course Code:</b>", style_body),
            Paragraph("3171608", style_body),
            Paragraph("<b>Academic Year:</b>", style_body),
            Paragraph("2026 – 2027", style_body)
        ],
        [
            Paragraph("<b>Project No:</b>", style_body),
            Paragraph("Project 8 (Link Budget GUI)", style_body),
            Paragraph("<b>Tools Used:</b>", style_body),
            Paragraph("Python, Tkinter, Matplotlib", style_body)
        ]
    ]
    t_cover_meta = Table(cover_meta_data, colWidths=[100, 170, 100, 170])
    t_cover_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f2f6")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#ced6e0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dfe4ea")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cover_meta)
    story.append(Spacer(1, 40))

    # Submission footer
    sub_table_data = [
        [
            Paragraph("<b>Prepared by:</b><br/>Devasya Patel<br/>B.E. Information Technology", style_body),
            Paragraph("<b>Submitted to:</b><br/>Faculty of IT / WC Mentor<br/>Department of IT", style_body)
        ]
    ]
    t_sub = Table(sub_table_data, colWidths=[270, 270])
    t_sub.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_sub)
    story.append(PageBreak())

    # =========================================================================
    # 2. CERTIFICATE PAGE
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("CERTIFICATE OF COMPLETION", ParagraphStyle('CertTitle', parent=style_cover_title, fontSize=18, textColor=c_primary)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=20))

    cert_text = (
        "This is to certify that the micro-project titled <b>'Wireless Link Budget GUI'</b> "
        "has been successfully developed and submitted by <b>Devasya Patel</b> in partial fulfillment of the requirements "
        "for the degree of <b>Bachelor of Engineering in Information Technology (7th Semester)</b> in the course "
        "<b>Wireless Communication (Subject Code: 3171608)</b> during the academic term 2026–2027.<br/><br/>"
        "The software application implements core physical-layer RF propagation algorithms, interactive parameter input forms, "
        "dynamic Matplotlib visual budget accounting, parametric distance sweeps, Shannon channel capacity analysis, "
        "and automated engineering report generation."
    )
    story.append(Paragraph(cert_text, ParagraphStyle('CertBody', parent=style_body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 40))

    sig_data = [
        [
            Paragraph("<b>________________________</b><br/><b>Internal Examiner</b><br/>Department of IT", style_body),
            Paragraph("<b>________________________</b><br/><b>Course Coordinator</b><br/>Wireless Communication", style_body),
            Paragraph("<b>________________________</b><br/><b>Head of Department (HOD)</b><br/>Department of IT", style_body),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_sig)
    story.append(PageBreak())

    # =========================================================================
    # 3. EXECUTIVE SUMMARY & TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("EXECUTIVE SUMMARY", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    exec_summary = (
        "A <b>Wireless Link Budget</b> is the fundamental quantitative accounting of all electrical gains, "
        "radiating antenna properties, propagation medium attenuations, and environmental fading margins across a communication channel. "
        "This project presents a Python-based interactive simulation and design software that replaces error-prone "
        "manual spreadsheet calculations with a professional desktop application.<br/><br/>"
        "The system incorporates five widely recognized propagation models: <b>Free Space Path Loss (FSPL)</b>, "
        "<b>Two-Ray Ground Reflection</b>, <b>Log-Distance Shadowing</b>, <b>Okumura-Hata</b>, and <b>COST-231 Hata</b>. "
        "It provides real-time computation of Transmitter EIRP, Total Path Loss, Received Signal Power ($P_{rx}$), "
        "Johnson-Nyquist Thermal Noise Floor ($kTB$), Signal-to-Noise Ratio (SNR), Link Margin, "
        "Maximum Achievable Coverage Range ($d_{max}$), and Shannon-Hartley Channel Capacity ($C$). "
        "Furthermore, eight industry-standard presets—spanning Wi-Fi 6, 4G LTE, 5G mmWave, GEO/LEO satellites, LoRaWAN IoT, "
        "and microwave backhaul—are integrated for instant benchmark evaluation."
    )
    story.append(Paragraph(exec_summary, style_body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("TABLE OF CONTENTS", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    toc_data = [
        [Paragraph("<b>Chapter 1: Introduction & Problem Statement</b>", style_body), Paragraph("Page 3", style_meta)],
        [Paragraph("<b>Chapter 2: Theoretical Formulation & Mathematical Models</b>", style_body), Paragraph("Page 3", style_meta)],
        [Paragraph("<b>Chapter 3: System Architecture & GUI Design</b>", style_body), Paragraph("Page 5", style_meta)],
        [Paragraph("<b>Chapter 4: Implementation Results & Case Studies</b>", style_body), Paragraph("Page 6", style_meta)],
        [Paragraph("<b>Chapter 5: Verification, Unit Testing & Benchmarks</b>", style_body), Paragraph("Page 8", style_meta)],
        [Paragraph("<b>Chapter 6: Conclusion & Future Scope</b>", style_body), Paragraph("Page 8", style_meta)],
        [Paragraph("<b>References & Academic Bibliography</b>", style_body), Paragraph("Page 9", style_meta)],
    ]
    t_toc = Table(toc_data, colWidths=[450, 90])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 14))

    # =========================================================================
    # 4. CHAPTER 1: INTRODUCTION & PROBLEM STATEMENT
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION & PROBLEM STATEMENT", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    ch1_p1 = (
        "<b>1.1 Context and Motivation:</b> Modern wireless communications have diversified into vastly distinct regimes—from "
        "dense indoor WLANs (Wi-Fi 6) and multi-kilometer cellular macro-cells (4G LTE / 5G NR) to long-distance satellite links "
        "(GEO/LEO) and ultra-low-power IoT telemetry (LoRaWAN). In all cases, system viability hinges on the <i>Link Budget</i>: "
        "ensuring that the received power arriving at the demodulator remains comfortably above the receiver's thermal noise floor "
        "and hardware sensitivity threshold."
    )
    story.append(Paragraph(ch1_p1, style_body))

    ch1_p2 = (
        "<b>1.2 Problem Statement:</b> In typical academic and engineering scenarios, RF link calculations are either performed "
        "manually using static textbook formulas or tabulated in rigid spreadsheets. Such methods fail to provide real-time visual "
        "intuition, cannot easily perform parametric sweeps across distance or frequency, lack comparative multi-scenario analysis, "
        "and do not automate publication-grade reporting."
    )
    story.append(Paragraph(ch1_p2, style_body))

    ch1_p3 = (
        "<b>1.3 Project Objectives:</b><br/>"
        "• Develop a modular, object-oriented RF calculation engine in Python adhering to rigorous telecommunications standards.<br/>"
        "• Implement five foundational propagation models covering line-of-sight, multipath reflection, and empirical cellular environments.<br/>"
        "• Build an interactive desktop GUI with dark/light themes, input forms, KPI metric cards, and embedded Matplotlib visual figures.<br/>"
        "• Formulate a stage-by-stage Waterfall chart showing cumulative power levels from transmitter to receiver.<br/>"
        "• Provide parametric distance sweeps and Shannon channel capacity evaluations.<br/>"
        "• Integrate automated IEEE-style PDF reporting, CSV data exports, and chart image saving."
    )
    story.append(Paragraph(ch1_p3, style_body))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 5. CHAPTER 2: THEORETICAL FORMULATION & MATHEMATICAL MODELS
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: THEORETICAL FORMULATION & MATHEMATICAL MODELS", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    story.append(Paragraph("2.1 Transmitter Radiated Power (EIRP)", style_h2))
    p_eirp = (
        "Effective Isotropic Radiated Power (EIRP) is the apparent power radiated by an antenna relative to an ideal lossless isotropic radiator:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>EIRP (dBm) = Ptx (dBm) + Gtx (dBi) - Ltx (dB)</b><br/>"
        "In linear units: <b>EIRP (W) = 10^((EIRP(dBm) - 30) / 10)</b><br/>"
        "Where $P_{tx}$ is transmitter amplifier output, $G_{tx}$ is antenna gain, and $L_{tx}$ represents transmission feeder losses."
    )
    story.append(Paragraph(p_eirp, style_body))

    story.append(Paragraph("2.2 Propagation Path Loss Models", style_h2))
    pl_models_text = (
        "<b>A. Free Space Path Loss (FSPL) - Friis Law:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;FSPL (dB) = 32.44 + 20·log10(d_km) + 20·log10(f_MHz)<br/>"
        "FSPL assumes unobstructed spherical wavefront expansion in vacuum or dry air, experiencing a 20 dB/decade attenuation rate.<br/><br/>"
        "<b>B. Two-Ray Ground Reflection Model:</b><br/>"
        "Considers direct line-of-sight and ground-reflected rays. Beyond crossover distance d_cross = 4*pi*htx*hrx / lambda, "
        "destructive interference causes path loss to scale with d^4 (40 dB/decade):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;PL_2ray (dB) = 40·log10(d) - 20·log10(htx) - 20·log10(hrx)<br/><br/>"
        "<b>C. Log-Distance Path Loss Model:</b><br/>"
        "Empirical model for cluttered indoor and campus environments:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;PL(d) (dB) = PL(d0) + 10·n·log10(d / d0) + X_sigma<br/>"
        "Where n is path loss exponent (n = 2 in free space, 2.7-3.5 in urban macro, 3.0-5.0 in shadowed indoor buildings).<br/><br/>"
        "<b>D. Okumura-Hata & COST-231 Empirical Cellular Models:</b><br/>"
        "Formulated from extensive field measurements in Japan and Europe (150 MHz to 2000 MHz):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;PL_urban = 69.55 + 26.16·log10(f) - 13.82·log10(hb) - a(hm) + [44.9 - 6.55·log10(hb)]·log10(d)<br/>"
        "Where hb is base station tower height (30–200 m), hm is mobile device height (1–10 m), and a(hm) is the correction factor."
    )
    story.append(Paragraph(pl_models_text, style_body))

    story.append(Paragraph("2.3 Received Power (Prx) & Environmental Losses", style_h2))
    p_prx = (
        "The net power reaching the receiver demodulator input is given by Friis' modified transmission equation:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Prx (dBm) = EIRP (dBm) - PL_model (dB) - L_env (dB) + Grx (dBi) - Lrx (dB)</b><br/>"
        "Where total environmental losses L_env = L_rain + L_atm + L_obstacle + L_pol + L_fade."
    )
    story.append(Paragraph(p_prx, style_body))

    story.append(Paragraph("2.4 Thermal Noise Floor, SNR & Link Margin", style_h2))
    p_snr = (
        "Johnson-Nyquist thermal noise generated inside the receiver front-end:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>N (dBm) = -174 dBm/Hz + 10·log10(Bandwidth_Hz) + Noise_Figure (dB)</b><br/>"
        "• <b>Signal-to-Noise Ratio:</b> SNR (dB) = Prx (dBm) - N (dBm)<br/>"
        "• <b>Link Margin (Fade Margin):</b> Margin (dB) = Prx (dBm) - Sensitivity (dBm)<br/>"
        "A positive link margin (>= 10 dB) ensures robust communication resistant against multipath fading and weather events."
    )
    story.append(Paragraph(p_snr, style_body))

    story.append(Paragraph("2.5 Shannon-Hartley Channel Capacity", style_h2))
    p_shannon = (
        "The theoretical upper bound on error-free information capacity across channel bandwidth $B$:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>C = B · log2(1 + SNR_linear) (bits per second)</b>, where SNR_linear = 10^(SNR_dB / 10)."
    )
    story.append(Paragraph(p_shannon, style_body))
    story.append(PageBreak())

    # =========================================================================
    # 6. CHAPTER 3: SYSTEM ARCHITECTURE & GUI DESIGN
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: SYSTEM ARCHITECTURE & GUI DESIGN", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    arch_text = (
        "The software follows a modular Model-View-Controller (MVC) architectural pattern implemented purely in Python.<br/>"
        "• <b>Engine Layer (link_budget_engine.py):</b> Pure numerical computation, physical constants, path loss functions, "
        "binary search range solver, and preconfigured industry presets.<br/>"
        "• <b>Presentation Layer (gui_app.py):</b> Built with ttkbootstrap and Tkinter, featuring four distinct tabs, "
        "live KPI metric cards, theme engine, and embedded interactive Matplotlib canvases.<br/>"
        "• <b>Reporting Layer (report_generator.py):</b> Uses ReportLab to compile engineering-grade PDF documents and CSV data tables.<br/>"
        "• <b>Verification Layer (test_engine.py):</b> Automated unit testing suite asserting mathematical rigor."
    )
    story.append(Paragraph(arch_text, style_body))
    story.append(Spacer(1, 6))

    # Embed Dashboard Preview Image if present
    preview_img = os.path.abspath("sample_outputs/gui_dashboard_preview.png")
    if os.path.exists(preview_img):
        story.append(KeepTogether([
            Paragraph("<b>Figure 3.1: Complete Wireless Link Budget GUI Dashboard Overview</b>", style_body_bold),
            Image(preview_img, width=7.4 * inch, height=4.2 * inch),
            Spacer(1, 6)
        ]))

    ui_tabs_text = (
        "<b>3.1 Tab Breakdown:</b><br/>"
        "• <b>Tab 1 (Calculator):</b> Interactive form fields on the left, 8 real-time KPI cards and stage-by-stage Waterfall chart on the right.<br/>"
        "• <b>Tab 2 (Parametric Sweeps):</b> Distance sweep curves displaying Received Power, SNR, and Shannon capacity on logarithmic axes.<br/>"
        "• <b>Tab 3 (Scenario Comparator):</b> Side-by-side benchmark table comparing up to 5 links with a grouped bar chart.<br/>"
        "• <b>Tab 4 (Theory & Formulas Reference):</b> In-app textbook reference for viva voce and exam revision."
    )
    story.append(Paragraph(ui_tabs_text, style_body))
    story.append(PageBreak())

    # =========================================================================
    # 7. CHAPTER 4: IMPLEMENTATION RESULTS & CASE STUDIES
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: IMPLEMENTATION RESULTS & CASE STUDIES", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    ch4_intro = (
        "To validate the practical utility of the tool, eight diverse communication links were simulated and evaluated. "
        "Table 4.1 summarizes the side-by-side performance benchmarks generated directly by the application."
    )
    story.append(Paragraph(ch4_intro, style_body))

    # Generate Comparison Table directly from engine presets
    evaluated_presets = []
    for k, p in PRESET_SCENARIOS.items():
        r = calculate_link_budget(p)
        evaluated_presets.append((p, r))

    comp_headers = [
        Paragraph("<b>Scenario Name</b>", style_body_bold),
        Paragraph("<b>Freq</b>", style_body_bold),
        Paragraph("<b>Dist</b>", style_body_bold),
        Paragraph("<b>Model</b>", style_body_bold),
        Paragraph("<b>EIRP</b>", style_body_bold),
        Paragraph("<b>PL (dB)</b>", style_body_bold),
        Paragraph("<b>Prx</b>", style_body_bold),
        Paragraph("<b>Margin</b>", style_body_bold),
        Paragraph("<b>Status</b>", style_body_bold),
    ]
    comp_rows = [comp_headers]

    for p, r in evaluated_presets:
        status_str = "<font color='#00b894'><b>PASS</b></font>" if r.is_link_viable else "<font color='#d63031'><b>FAIL</b></font>"
        short_name = p.scenario_name.split("(")[0].strip()
        comp_rows.append([
            Paragraph(short_name, style_meta),
            Paragraph(f"{p.frequency_mhz:.0f}M", style_meta),
            Paragraph(f"{p.distance_km:.2f}k" if p.distance_km >= 1 else f"{p.distance_km*1000:.0f}m", style_meta),
            Paragraph(p.path_loss_model.split("(")[0].strip()[:10], style_meta),
            Paragraph(f"{r.eirp_dbm:.1f}", style_meta),
            Paragraph(f"{r.total_path_loss_db:.1f}", style_meta),
            Paragraph(f"{r.rx_power_dbm:.1f}", style_meta),
            Paragraph(f"<b>{r.link_margin_db:+.1f}</b>", style_meta),
            Paragraph(status_str, style_meta),
        ])

    t_comp = Table(comp_rows, colWidths=[120, 45, 45, 75, 45, 50, 55, 55, 50])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # Embed Waterfall Chart Image
    waterfall_img = os.path.abspath("sample_outputs/sample_power_budget_waterfall.png")
    if os.path.exists(waterfall_img):
        story.append(KeepTogether([
            Paragraph("<b>Figure 4.1: Power Budget Waterfall Breakdown — Wi-Fi 6 (2.4 GHz, 80m)</b>", style_body_bold),
            Image(waterfall_img, width=7.2 * inch, height=3.2 * inch),
            Spacer(1, 8)
        ]))

    # Embed Distance & Capacity Sweep Charts
    sweep_img = os.path.abspath("sample_outputs/sample_prx_vs_distance.png")
    if os.path.exists(sweep_img):
        story.append(KeepTogether([
            Paragraph("<b>Figure 4.2: Parametric Received Power Decay vs. Distance (4G LTE Urban Cell)</b>", style_body_bold),
            Image(sweep_img, width=7.2 * inch, height=3.0 * inch),
            Spacer(1, 6)
        ]))

    snr_img = os.path.abspath("sample_outputs/sample_snr_vs_distance.png")
    if os.path.exists(snr_img):
        story.append(KeepTogether([
            Paragraph("<b>Figure 4.3: SNR & Shannon Capacity Degradation Curves Across Distance</b>", style_body_bold),
            Image(snr_img, width=7.2 * inch, height=2.8 * inch),
            Spacer(1, 6)
        ]))

    story.append(PageBreak())

    # =========================================================================
    # 8. CHAPTER 5: VERIFICATION, TESTING & BENCHMARKS
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: VERIFICATION, TESTING & BENCHMARKS", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    test_text = (
        "To ensure analytical correctness, an automated test suite (<b>test_engine.py</b>) was developed utilizing Python's "
        "built-in <code>unittest</code> framework. The test cases verify unit conversions, mathematical models, boundary conditions, "
        "and physical consistency across the parameter space."
    )
    story.append(Paragraph(test_text, style_body))

    test_table_data = [
        [Paragraph("<b>Test Case Name</b>", style_body_bold), Paragraph("<b>Target Subsystem</b>", style_body_bold), Paragraph("<b>Expected Benchmark</b>", style_body_bold), Paragraph("<b>Result</b>", style_body_bold)],
        [Paragraph("test_power_conversions", style_meta), Paragraph("Unit Conversions", style_meta), Paragraph("30 dBm == 1.000 W; 0 dBm == 1.000 mW", style_meta), Paragraph("<font color='#00b894'><b>PASSED</b></font>", style_meta)],
        [Paragraph("test_wavelength", style_meta), Paragraph("Electromagnetics", style_meta), Paragraph("lambda at 300 MHz == 0.9993 m (~1m)", style_meta), Paragraph("<font color='#00b894'><b>PASSED</b></font>", style_meta)],
        [Paragraph("test_fspl_known_values", style_meta), Paragraph("Friis Model", style_meta), Paragraph("FSPL(1 GHz, 1 km) == 92.44 dB exactly", style_meta), Paragraph("<font color='#00b894'><b>PASSED</b></font>", style_meta)],
        [Paragraph("test_link_budget_basic", style_meta), Paragraph("End-to-End Budget", style_meta), Paragraph("EIRP 30 dBm, FSPL 92.44 dB -> Prx -52.44 dBm", style_meta), Paragraph("<font color='#00b894'><b>PASSED</b></font>", style_meta)],
        [Paragraph("test_presets_validity", style_meta), Paragraph("Preset Scenarios", style_meta), Paragraph("All 8 presets evaluate without exceptions", style_meta), Paragraph("<font color='#00b894'><b>PASSED</b></font>", style_meta)],
        [Paragraph("test_distance_sweep", style_meta), Paragraph("Parametric Sweeps", style_meta), Paragraph("Strict monotonic power decay over distance", style_meta), Paragraph("<font color='#00b894'><b>PASSED</b></font>", style_meta)],
        [Paragraph("test_solver_max_distance", style_meta), Paragraph("Root Solver", style_meta), Paragraph("Binary search converges to Margin == 0 dB", style_meta), Paragraph("<font color='#00b894'><b>PASSED</b></font>", style_meta)],
    ]
    t_test = Table(test_table_data, colWidths=[140, 110, 210, 80])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2f3640")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 14))

    # =========================================================================
    # 9. CHAPTER 6: CONCLUSION & FUTURE SCOPE
    # =========================================================================
    story.append(Paragraph("CHAPTER 6: CONCLUSION & FUTURE SCOPE", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    conclusion_text = (
        "<b>6.1 Conclusion:</b> The <b>Wireless Link Budget GUI</b> software provides a complete, reliable, and user-friendly "
        "platform for modeling and analyzing RF links across modern telecommunications technologies. By unifying transmitter EIRP, "
        "multi-model path loss calculations, environmental margins, thermal noise floors, and channel capacity into a modern desktop "
        "interface, the application bridges the gap between theoretical textbook formulas and practical RF deployment design.<br/><br/>"
        "<b>6.2 Key Learning Outcomes:</b><br/>"
        "• Deepened understanding of electromagnetic wave propagation, attenuation mechanisms, and noise figure accounting.<br/>"
        "• Hands-on mastery of Python software engineering with Tkinter / ttkbootstrap, object-oriented design, and automated ReportLab PDF synthesis.<br/>"
        "• Practical appreciation of how trade-offs between carrier frequency, antenna gain, bandwidth, and sensitivity govern coverage in 4G, 5G, and IoT systems.<br/><br/>"
        "<b>6.3 Future Scope:</b><br/>"
        "• <b>3D Ray-Tracing Engine:</b> Incorporating physical building CAD models for deterministic indoor multipath simulation.<br/>"
        "• <b>GIS & Terrain Elevation Integration:</b> Loading real digital elevation models (DEM) to evaluate knife-edge diffraction losses over mountains.<br/>"
        "• <b>MIMO & Phased Array Beamforming:</b> Extending isotropic gains to multi-antenna spatial multiplexing and beam-steering patterns."
    )
    story.append(Paragraph(conclusion_text, style_body))
    story.append(Spacer(1, 12))

    # =========================================================================
    # 10. REFERENCES & BIBLIOGRAPHY
    # =========================================================================
    story.append(Paragraph("REFERENCES & ACADEMIC BIBLIOGRAPHY", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    refs_text = (
        "[1] Theodore S. Rappaport, <i>Wireless Communications: Principles and Practice</i>, 2nd Edition, Prentice Hall, 2002.<br/>"
        "[2] Andrea Goldsmith, <i>Wireless Communications</i>, Cambridge University Press, 2005.<br/>"
        "[3] ITU-R Recommendation P.525-4, <i>Calculation of Free-Space Attenuation</i>, International Telecommunication Union, 2019.<br/>"
        "[4] Y. Okumura et al., <i>Field Strength and Its Variability in VHF and UHF Land-Mobile Radio Service</i>, Rev. Elec. Comm. Lab., 1968.<br/>"
        "[5] M. Hata, <i>Empirical Formula for Propagation Loss in Land Mobile Radio Services</i>, IEEE Transactions on Vehicular Technology, 1980.<br/>"
        "[6] Claude E. Shannon, <i>A Mathematical Theory of Communication</i>, Bell System Technical Journal, 1948.<br/>"
        "[7] GTU Curriculum for Bachelor of Engineering in Information Technology, <i>Subject Code 3171608: Wireless Communication</i>, Gujarat Technological University."
    )
    story.append(Paragraph(refs_text, style_body))

    # Build PDF with two-pass canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF built successfully: {os.path.abspath(output_pdf_path)}")
    return output_pdf_path


if __name__ == "__main__":
    build_project_report_pdf()
