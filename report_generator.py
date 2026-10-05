"""
Report Generator Module
=======================
Generates PDF and CSV reports for the Wireless Link Budget GUI application.
Produces engineering-grade documentation suitable for academic submissions
(Wireless Communication - 3171608 Micro-Project) and professional RF design.
"""

import os
import csv
from datetime import datetime
from typing import Optional, List, Dict, Any

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
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from link_budget_engine import LinkBudgetParameters, LinkBudgetResults


def generate_pdf_report(
    params: LinkBudgetParameters,
    results: LinkBudgetResults,
    output_filepath: str,
    chart_image_path: Optional[str] = None
) -> str:
    """
    Generate a formatted multi-page PDF engineering report using ReportLab.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    primary_color = colors.HexColor("#1e3d59")
    accent_color = colors.HexColor("#17b978") if results.is_link_viable else colors.HexColor("#e74c3c")
    text_dark = colors.HexColor("#2c3e50")
    light_bg = colors.HexColor("#f8f9fa")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=text_dark
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#666666")
    )

    story = []

    # Title & Header
    story.append(Paragraph("WIRELESS LINK BUDGET ANALYSIS REPORT", title_style))
    story.append(Paragraph("Course: 3171608 - Wireless Communication (WC) | Micro-Project", subtitle_style))
    
    # Metadata bar
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_text = f"<b>Scenario:</b> {params.scenario_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Generated:</b> {gen_time} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Model:</b> {params.path_loss_model}"
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=12))

    # Executive Status Banner
    status_bg = colors.HexColor("#e8f8f5") if results.is_link_viable else colors.HexColor("#fdedec")
    status_border = colors.HexColor("#2ecc71") if results.is_link_viable else colors.HexColor("#e74c3c")
    status_symbol = "✔ PASS" if results.is_link_viable else "✖ FAIL / MARGIN DEFICIT"
    
    status_p = Paragraph(
        f"<b>LINK STATUS: {status_symbol} &mdash; {results.status_text}</b><br/>"
        f"Received Power: <b>{results.rx_power_dbm:.2f} dBm</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Sensitivity: <b>{params.rx_sensitivity_dbm:.2f} dBm</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Fade / Link Margin: <b>{results.link_margin_db:+.2f} dB</b>",
        ParagraphStyle(
            'StatusBanner',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=status_border,
            alignment=1
        )
    )
    banner_table = Table([[status_p]], colWidths=[540])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), status_bg),
        ('BOX', (0, 0), (-1, -1), 1.5, status_border),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    # Executive Metrics Summary Grid
    story.append(Paragraph("Executive Performance Metrics", h2_style))
    summary_data = [
        [
            Paragraph("<b>EIRP</b>", body_style),
            Paragraph(f"{results.eirp_dbm:.2f} dBm ({results.eirp_w:.3f} W)", body_style),
            Paragraph("<b>Received Power (Prx)</b>", body_style),
            Paragraph(f"{results.rx_power_dbm:.2f} dBm ({results.rx_power_pw:.2f} pW)", body_style),
        ],
        [
            Paragraph("<b>Free Space Path Loss</b>", body_style),
            Paragraph(f"{results.free_space_path_loss_db:.2f} dB", body_style),
            Paragraph("<b>Model Path Loss</b>", body_style),
            Paragraph(f"{results.model_path_loss_db:.2f} dB", body_style),
        ],
        [
            Paragraph("<b>Total Environmental Loss</b>", body_style),
            Paragraph(f"{results.total_environmental_losses_db:.2f} dB", body_style),
            Paragraph("<b>Total Attenuation</b>", body_style),
            Paragraph(f"{results.total_attenuation_db:.2f} dB", body_style),
        ],
        [
            Paragraph("<b>Thermal Noise Floor</b>", body_style),
            Paragraph(f"{results.receiver_noise_floor_dbm:.2f} dBm", body_style),
            Paragraph("<b>Signal-to-Noise Ratio (SNR)</b>", body_style),
            Paragraph(f"<b>{results.snr_db:.2f} dB</b>", body_style),
        ],
        [
            Paragraph("<b>Max Achievable Distance</b>", body_style),
            Paragraph(f"<b>{results.max_achievable_distance_km:.3f} km</b>", body_style),
            Paragraph("<b>Shannon Capacity</b>", body_style),
            Paragraph(f"<b>{results.shannon_capacity_mbps:.2f} Mbps</b>", body_style),
        ],
        [
            Paragraph("<b>Max Allowable Path Loss</b>", body_style),
            Paragraph(f"{results.max_allowable_path_loss_db:.2f} dB", body_style),
            Paragraph("<b>Carrier Wavelength (λ)</b>", body_style),
            Paragraph(f"{results.wavelength_m:.4f} m ({results.wavelength_m*100:.2f} cm)", body_style),
        ],
    ]
    summary_table = Table(summary_data, colWidths=[135, 135, 135, 135])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdde1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # Detailed Parameter Tables (Tx, Channel, Rx)
    story.append(Paragraph("System Input Parameters", h2_style))
    param_data = [
        [
            Paragraph("<b>Subsystem</b>", body_style),
            Paragraph("<b>Parameter Name</b>", body_style),
            Paragraph("<b>Value</b>", body_style),
            Paragraph("<b>Units / Notes</b>", body_style),
        ],
        # Transmitter
        [Paragraph("Transmitter (Tx)", body_style), Paragraph("Tx Output Power (Ptx)", body_style), Paragraph(f"{params.tx_power_dbm:.2f}", body_style), Paragraph("dBm", body_style)],
        [Paragraph("", body_style), Paragraph("Tx Antenna Gain (Gtx)", body_style), Paragraph(f"{params.tx_antenna_gain_dbi:.2f}", body_style), Paragraph("dBi", body_style)],
        [Paragraph("", body_style), Paragraph("Tx Cable & Connector Losses", body_style), Paragraph(f"{params.tx_cable_loss_db:.2f}", body_style), Paragraph("dB", body_style)],
        [Paragraph("", body_style), Paragraph("Tx Antenna Height (hb)", body_style), Paragraph(f"{params.tx_antenna_height_m:.1f}", body_style), Paragraph("meters", body_style)],
        # Channel
        [Paragraph("Channel / Path", body_style), Paragraph("Carrier Frequency (f)", body_style), Paragraph(f"{params.frequency_mhz:.2f}", body_style), Paragraph("MHz", body_style)],
        [Paragraph("", body_style), Paragraph("Link Distance (d)", body_style), Paragraph(f"{params.distance_km:.3f}", body_style), Paragraph("km", body_style)],
        [Paragraph("", body_style), Paragraph("Propagation Model", body_style), Paragraph(params.path_loss_model, body_style), Paragraph("Empirical/Analytical", body_style)],
        [Paragraph("", body_style), Paragraph("Path Loss Exponent (n)", body_style), Paragraph(f"{params.path_loss_exponent:.2f}", body_style), Paragraph("Dimensionless", body_style)],
        [Paragraph("", body_style), Paragraph("Rain Attenuation", body_style), Paragraph(f"{params.rain_attenuation_db:.2f}", body_style), Paragraph("dB", body_style)],
        [Paragraph("", body_style), Paragraph("Atmospheric & Gas Loss", body_style), Paragraph(f"{params.atmospheric_loss_db:.2f}", body_style), Paragraph("dB", body_style)],
        [Paragraph("", body_style), Paragraph("Obstacle / Penetration Loss", body_style), Paragraph(f"{params.obstacle_loss_db:.2f}", body_style), Paragraph("dB", body_style)],
        [Paragraph("", body_style), Paragraph("Fade Margin Allocation", body_style), Paragraph(f"{params.fade_margin_db:.2f}", body_style), Paragraph("dB", body_style)],
        # Receiver
        [Paragraph("Receiver (Rx)", body_style), Paragraph("Rx Antenna Gain (Grx)", body_style), Paragraph(f"{params.rx_antenna_gain_dbi:.2f}", body_style), Paragraph("dBi", body_style)],
        [Paragraph("", body_style), Paragraph("Rx Cable & Filter Loss", body_style), Paragraph(f"{params.rx_cable_loss_db:.2f}", body_style), Paragraph("dB", body_style)],
        [Paragraph("", body_style), Paragraph("Rx Sensitivity Threshold", body_style), Paragraph(f"{params.rx_sensitivity_dbm:.2f}", body_style), Paragraph("dBm", body_style)],
        [Paragraph("", body_style), Paragraph("Front-End Noise Figure (NF)", body_style), Paragraph(f"{params.noise_figure_db:.2f}", body_style), Paragraph("dB", body_style)],
        [Paragraph("", body_style), Paragraph("Channel Bandwidth (B)", body_style), Paragraph(f"{params.bandwidth_mhz:.2f}", body_style), Paragraph("MHz", body_style)],
        [Paragraph("", body_style), Paragraph("Noise Temperature (T)", body_style), Paragraph(f"{params.temperature_k:.1f}", body_style), Paragraph("Kelvin (K)", body_style)],
    ]
    param_table = Table(param_data, colWidths=[110, 190, 80, 160])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdde1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(param_table)
    story.append(Spacer(1, 10))

    # Stage-by-Stage Waterfall Budget
    story.append(Paragraph("Link Budget Stage-by-Stage Power Accounting", h2_style))
    stage_rows = [
        [
            Paragraph("<b>Stage Description</b>", body_style),
            Paragraph("<b>Incremental Gain/Loss (dB)</b>", body_style),
            Paragraph("<b>Cumulative Power Level (dBm)</b>", body_style),
        ]
    ]
    for stage_name, cum_level, delta in results.waterfall_stages:
        delta_str = f"+{delta:.2f} dB" if delta > 0 else f"{delta:.2f} dB" if delta < 0 else "0.00 dB"
        stage_rows.append([
            Paragraph(stage_name, body_style),
            Paragraph(delta_str, body_style),
            Paragraph(f"<b>{cum_level:.2f} dBm</b>", body_style)
        ])
    
    stage_table = Table(stage_rows, colWidths=[240, 150, 150])
    stage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2f3640")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dcdde1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(stage_table)
    story.append(Spacer(1, 12))

    # Embed Chart Image if available
    if chart_image_path and os.path.exists(chart_image_path):
        story.append(KeepTogether([
            Paragraph("RF Link Budget Visual Plots", h2_style),
            Image(chart_image_path, width=7.2 * inch, height=3.5 * inch),
            Spacer(1, 8)
        ]))

    # Mathematical Formula Reference Box
    formula_box_text = (
        "<b>Core Mathematical Formulas Applied:</b><br/>"
        "• <b>Friis Received Power:</b> Prx (dBm) = Ptx + Gtx - Ltx - PL + Grx - Lrx - Lenv<br/>"
        "• <b>Free Space Path Loss:</b> FSPL (dB) = 32.44 + 20·log10(d_km) + 20·log10(f_MHz)<br/>"
        "• <b>Thermal Noise Floor:</b> N (dBm) = -174 dBm/Hz + 10·log10(B_Hz) + NF (dB)<br/>"
        "• <b>Link Margin:</b> Margin (dB) = Prx (dBm) - Prx,sens (dBm)<br/>"
        "• <b>Shannon Capacity:</b> C = B · log2(1 + SNR_linear) (bps)"
    )
    formula_table = Table([[Paragraph(formula_box_text, meta_style)]], colWidths=[540])
    formula_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f2f6")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#ced6e0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([formula_table]))

    doc.build(story)
    return output_filepath


def export_link_budget_csv(
    params: LinkBudgetParameters,
    results: LinkBudgetResults,
    output_filepath: str,
    sweep_data: Optional[Tuple[List[float], List[float], List[float], List[float]]] = None
) -> str:
    """Export single link budget summary and optional distance sweep data to CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    with open(output_filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["=== WIRELESS LINK BUDGET ANALYSIS REPORT ==="])
        writer.writerow(["Scenario Name", params.scenario_name])
        writer.writerow(["Timestamp", datetime.now().isoformat()])
        writer.writerow([])
        writer.writerow(["--- EXECUTIVE SUMMARY ---"])
        writer.writerow(["Parameter", "Value", "Unit"])
        writer.writerow(["Link Status", results.status_text, ""])
        writer.writerow(["Is Link Viable", results.is_link_viable, ""])
        writer.writerow(["EIRP", round(results.eirp_dbm, 2), "dBm"])
        writer.writerow(["EIRP (Watts)", round(results.eirp_w, 4), "Watts"])
        writer.writerow(["Total Path Loss", round(results.total_path_loss_db, 2), "dB"])
        writer.writerow(["Received Power (Prx)", round(results.rx_power_dbm, 2), "dBm"])
        writer.writerow(["Received Power (Watts)", f"{results.rx_power_w:.4e}", "Watts"])
        writer.writerow(["Rx Sensitivity Threshold", round(params.rx_sensitivity_dbm, 2), "dBm"])
        writer.writerow(["Link Margin", round(results.link_margin_db, 2), "dB"])
        writer.writerow(["Noise Floor", round(results.receiver_noise_floor_dbm, 2), "dBm"])
        writer.writerow(["Signal-to-Noise Ratio (SNR)", round(results.snr_db, 2), "dB"])
        writer.writerow(["Max Achievable Distance", round(results.max_achievable_distance_km, 3), "km"])
        writer.writerow(["Shannon Channel Capacity", round(results.shannon_capacity_mbps, 2), "Mbps"])
        writer.writerow([])

        writer.writerow(["--- DETAILED INPUT PARAMETERS ---"])
        writer.writerow(["Parameter", "Value", "Unit"])
        writer.writerow(["Tx Power", params.tx_power_dbm, "dBm"])
        writer.writerow(["Tx Antenna Gain", params.tx_antenna_gain_dbi, "dBi"])
        writer.writerow(["Tx Cable Loss", params.tx_cable_loss_db, "dB"])
        writer.writerow(["Carrier Frequency", params.frequency_mhz, "MHz"])
        writer.writerow(["Distance", params.distance_km, "km"])
        writer.writerow(["Path Loss Model", params.path_loss_model, ""])
        writer.writerow(["Path Loss Exponent", params.path_loss_exponent, ""])
        writer.writerow(["Rain Attenuation", params.rain_attenuation_db, "dB"])
        writer.writerow(["Atmospheric Loss", params.atmospheric_loss_db, "dB"])
        writer.writerow(["Obstacle Loss", params.obstacle_loss_db, "dB"])
        writer.writerow(["Fade Margin", params.fade_margin_db, "dB"])
        writer.writerow(["Rx Antenna Gain", params.rx_antenna_gain_dbi, "dBi"])
        writer.writerow(["Rx Cable Loss", params.rx_cable_loss_db, "dB"])
        writer.writerow(["Rx Noise Figure", params.noise_figure_db, "dB"])
        writer.writerow(["Channel Bandwidth", params.bandwidth_mhz, "MHz"])
        writer.writerow(["System Temperature", params.temperature_k, "K"])
        writer.writerow([])

        # Waterfall Stages
        writer.writerow(["--- POWER BUDGET WATERFALL STAGES ---"])
        writer.writerow(["Stage Name", "Cumulative Level (dBm)", "Delta (dB)"])
        for stage_name, level, delta in results.waterfall_stages:
            writer.writerow([stage_name, round(level, 2), round(delta, 2)])
        writer.writerow([])

        # Sweep data if provided
        if sweep_data:
            dists, rx_powers, snrs, caps = sweep_data
            writer.writerow(["--- PARAMETRIC DISTANCE SWEEP DATA ---"])
            writer.writerow(["Distance (km)", "Rx Power (dBm)", "SNR (dB)", "Shannon Capacity (Mbps)"])
            for d, prx, snr, cap in zip(dists, rx_powers, snrs, caps):
                writer.writerow([round(d, 4), round(prx, 2), round(snr, 2), round(cap, 2)])

    return output_filepath


def export_scenario_comparison_csv(
    scenarios: List[Tuple[LinkBudgetParameters, LinkBudgetResults]],
    output_filepath: str
) -> str:
    """Export comparison of multiple scenarios to CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    with open(output_filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ["Metric / Parameter"] + [p.scenario_name for p, _ in scenarios]
        writer.writerow(header)

        metrics = [
            ("Carrier Frequency (MHz)", lambda p, r: f"{p.frequency_mhz:.1f}"),
            ("Link Distance (km)", lambda p, r: f"{p.distance_km:.3f}"),
            ("Path Loss Model", lambda p, r: p.path_loss_model),
            ("Tx Power (dBm)", lambda p, r: f"{p.tx_power_dbm:.1f}"),
            ("EIRP (dBm)", lambda p, r: f"{r.eirp_dbm:.2f}"),
            ("Total Path Loss (dB)", lambda p, r: f"{r.total_path_loss_db:.2f}"),
            ("Rx Antenna Gain (dBi)", lambda p, r: f"{p.rx_antenna_gain_dbi:.2f}"),
            ("Received Power Prx (dBm)", lambda p, r: f"{r.rx_power_dbm:.2f}"),
            ("Rx Sensitivity (dBm)", lambda p, r: f"{p.rx_sensitivity_dbm:.2f}"),
            ("Link Margin (dB)", lambda p, r: f"{r.link_margin_db:+.2f}"),
            ("Link Status", lambda p, r: "PASS" if r.is_link_viable else "FAIL"),
            ("Noise Floor (dBm)", lambda p, r: f"{r.receiver_noise_floor_dbm:.2f}"),
            ("SNR (dB)", lambda p, r: f"{r.snr_db:.2f}"),
            ("Max Achievable Dist (km)", lambda p, r: f"{r.max_achievable_distance_km:.3f}"),
            ("Shannon Capacity (Mbps)", lambda p, r: f"{r.shannon_capacity_mbps:.2f}"),
        ]

        for label, extractor in metrics:
            row = [label] + [extractor(p, r) for p, r in scenarios]
            writer.writerow(row)

    return output_filepath
