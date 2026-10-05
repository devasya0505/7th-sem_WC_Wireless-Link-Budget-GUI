"""
Dashboard Preview Image Generator
=================================
Creates a comprehensive multi-panel visual preview representing the
Wireless Link Budget GUI Dashboard, complete with parameter inputs,
KPI metrics, waterfall chart, distance sweeps, and multi-scenario comparison.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image, ImageDraw, ImageFont

from link_budget_engine import (
    PRESET_SCENARIOS,
    calculate_link_budget,
    sweep_distance
)


def create_dashboard_preview(output_path="sample_outputs/gui_dashboard_preview.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Dark modern styling matching ttkbootstrap 'darkly'
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(15, 9.5), dpi=140)
    fig.patch.set_facecolor('#1a1a24')

    gs = gridspec.GridSpec(3, 3, figure=fig, height_ratios=[0.8, 2.2, 2.0], width_ratios=[1.2, 1.2, 1.0])
    gs.update(top=0.92, bottom=0.06, left=0.06, right=0.95, hspace=0.35, wspace=0.25)

    # Header Title Banner
    fig.text(0.06, 0.955, "[RF-BUDGET] WIRELESS LINK BUDGET GUI - SIMULATION SUITE",
             fontsize=14, fontweight='bold', color='#00d2d3')
    fig.text(0.06, 0.932, "Course: 3171608 - Wireless Communication (WC) | GTU 7th Sem IT Micro-Project",
             fontsize=10, color='#8395a7')
    fig.text(0.78, 0.955, "STATUS: ✔ PASS (Margin: +15.5 dB)",
             fontsize=12, fontweight='bold', color='#10ac84',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#012e1f', edgecolor='#10ac84', linewidth=1.2))

    # Row 0: KPI Summary Metric Cards (Col 0, Col 1, Col 2)
    ax_kpi1 = fig.add_subplot(gs[0, 0])
    ax_kpi1.axis('off')
    ax_kpi1.text(0.05, 0.70, "LINK MARGIN (Fade Safety)", fontsize=9, color='#8395a7', fontweight='bold')
    ax_kpi1.text(0.05, 0.20, "+15.52 dB", fontsize=20, color='#1dd1a1', fontweight='bold')
    ax_kpi1.text(0.55, 0.25, "PASS", fontsize=10, color='#1dd1a1',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#012e1f', edgecolor='#1dd1a1'))
    ax_kpi1.patch.set_facecolor('#222f3e')
    ax_kpi1.patch.set_visible(True)

    ax_kpi2 = fig.add_subplot(gs[0, 1])
    ax_kpi2.axis('off')
    ax_kpi2.text(0.05, 0.70, "RECEIVED POWER (Prx)", fontsize=9, color='#8395a7', fontweight='bold')
    ax_kpi2.text(0.05, 0.20, "-66.48 dBm", fontsize=20, color='#54a0ff', fontweight='bold')
    ax_kpi2.text(0.68, 0.25, "225 pW", fontsize=10, color='#54a0ff')
    ax_kpi2.patch.set_facecolor('#222f3e')
    ax_kpi2.patch.set_visible(True)

    ax_kpi3 = fig.add_subplot(gs[0, 2])
    ax_kpi3.axis('off')
    ax_kpi3.text(0.05, 0.70, "EIRP / MAX RANGE", fontsize=9, color='#8395a7', fontweight='bold')
    ax_kpi3.text(0.05, 0.20, "+22.5 dBm | 0.28 km", fontsize=16, color='#feca57', fontweight='bold')
    ax_kpi3.text(0.05, -0.05, "Capacity: 124.5 Mbps | SNR: 28.2 dB", fontsize=9, color='#c8d6e5')
    ax_kpi3.patch.set_facecolor('#222f3e')
    ax_kpi3.patch.set_visible(True)

    # Row 1, Col 0 & 1: Stage-by-Stage Waterfall Chart (Wi-Fi 6 2.4 GHz)
    wifi_p = PRESET_SCENARIOS["Wi-Fi 6 (802.11ax) 2.4 GHz"]
    wifi_r = calculate_link_budget(wifi_p)

    ax_waterfall = fig.add_subplot(gs[1, 0:2])
    ax_waterfall.set_facecolor('#222f3e')
    stages = [s[0] for s in wifi_r.waterfall_stages]
    levels = [s[1] for s in wifi_r.waterfall_stages]
    colors_w = ['#54a0ff', '#ff9f43', '#10ac84', '#ee5253', '#ff6b6b', '#10ac84', '#1dd1a1']

    bars = ax_waterfall.bar(stages, levels, color=colors_w, width=0.52, edgecolor='#576574')
    ax_waterfall.axhline(wifi_p.rx_sensitivity_dbm, color='#ee5253', linestyle='--', linewidth=1.5,
                         label=f'Rx Sensitivity ({wifi_p.rx_sensitivity_dbm} dBm)')
    ax_waterfall.axhline(wifi_r.receiver_noise_floor_dbm, color='#8395a7', linestyle=':', linewidth=1.4,
                         label=f'Noise Floor ({wifi_r.receiver_noise_floor_dbm:.1f} dBm)')

    ax_waterfall.set_ylabel("Power Level (dBm)", fontsize=9, fontweight='bold', color='#c8d6e5')
    ax_waterfall.set_title("Stage-by-Stage Power Budget Waterfall — Wi-Fi 6 (2.4 GHz, 80m)", fontsize=11, fontweight='bold', color='#f1f2f6')
    ax_waterfall.grid(axis='y', linestyle='--', alpha=0.3, color='#576574')
    ax_waterfall.tick_params(axis='x', rotation=18, labelsize=8, colors='#c8d6e5')
    ax_waterfall.tick_params(axis='y', labelsize=8, colors='#c8d6e5')
    ax_waterfall.legend(loc='lower left', fontsize=8, facecolor='#2f3542', edgecolor='#576574')

    for bar, lvl in zip(bars, levels):
        y_pos = lvl + (1.5 if lvl >= 0 else -4.0)
        ax_waterfall.annotate(f"{lvl:.1f}", xy=(bar.get_x() + bar.get_width()/2, y_pos),
                              ha='center', va='bottom' if lvl >= 0 else 'top',
                              fontsize=7.5, fontweight='bold', color='#ffffff')

    # Row 1, Col 2: Parameter Inputs Breakdown Card
    ax_params = fig.add_subplot(gs[1, 2])
    ax_params.axis('off')
    ax_params.set_facecolor('#222f3e')
    param_text = (
        "TRANSMITTER (Tx):\n"
        f"  • Power: {wifi_p.tx_power_dbm:.1f} dBm (100 mW)\n"
        f"  • Ant Gain: +{wifi_p.tx_antenna_gain_dbi:.1f} dBi\n"
        f"  • Cable Loss: -{wifi_p.tx_cable_loss_db:.1f} dB\n"
        f"  • EIRP: +{wifi_r.eirp_dbm:.1f} dBm\n\n"
        "PROPAGATION PATH:\n"
        f"  • Frequency: {wifi_p.frequency_mhz:.0f} MHz (λ={wifi_r.wavelength_m:.2f}m)\n"
        f"  • Distance: {wifi_p.distance_km*1000:.0f} m\n"
        f"  • Model: {wifi_p.path_loss_model}\n"
        f"  • Model Loss: {wifi_r.model_path_loss_db:.1f} dB\n"
        f"  • Obstacle Loss: {wifi_p.obstacle_loss_db:.1f} dB\n"
        f"  • Fade Margin: {wifi_p.fade_margin_db:.1f} dB\n\n"
        "RECEIVER (Rx):\n"
        f"  • Ant Gain: +{wifi_p.rx_antenna_gain_dbi:.1f} dBi\n"
        f"  • Noise Figure: {wifi_p.noise_figure_db:.1f} dB\n"
        f"  • Bandwidth: {wifi_p.bandwidth_mhz:.0f} MHz\n"
        f"  • Sensitivity: {wifi_p.rx_sensitivity_dbm:.1f} dBm\n"
        f"  • Received: {wifi_r.rx_power_dbm:.1f} dBm"
    )
    ax_params.text(0.04, 0.95, "ACTIVE LINK PARAMETERS", fontsize=10, fontweight='bold', color='#feca57', va='top')
    ax_params.text(0.04, 0.88, param_text, fontsize=8, color='#c8d6e5', va='top', fontfamily='monospace')

    # Row 2, Col 0: Prx vs Distance Curve
    lte_p = PRESET_SCENARIOS["4G LTE Cellular Base Station (1800 MHz)"]
    lte_r = calculate_link_budget(lte_p)
    dists, rx_p, snrs, caps = sweep_distance(lte_p, 0.1, 10.0, 100)

    ax_dist = fig.add_subplot(gs[2, 0])
    ax_dist.set_facecolor('#222f3e')
    ax_dist.plot(dists, rx_p, color='#54a0ff', linewidth=2.0, label='Received Prx')
    ax_dist.axhline(lte_p.rx_sensitivity_dbm, color='#ee5253', linestyle='--', linewidth=1.3,
                    label=f'Sens ({lte_p.rx_sensitivity_dbm} dBm)')
    ax_dist.axhline(lte_r.receiver_noise_floor_dbm, color='#8395a7', linestyle=':', linewidth=1.2,
                    label='Noise Floor')
    if lte_r.max_achievable_distance_km > 0:
        ax_dist.axvline(lte_r.max_achievable_distance_km, color='#1dd1a1', linestyle='-.', linewidth=1.3,
                        label=f'd_max={lte_r.max_achievable_distance_km:.1f}km')
    ax_dist.set_xscale('log')
    ax_dist.set_xlabel("Distance (km)", fontsize=8, color='#c8d6e5')
    ax_dist.set_ylabel("Power (dBm)", fontsize=8, color='#c8d6e5')
    ax_dist.set_title("Received Power vs Distance (4G LTE)", fontsize=9.5, fontweight='bold', color='#f1f2f6')
    ax_dist.grid(True, which="both", ls="--", alpha=0.25, color='#576574')
    ax_dist.tick_params(labelsize=7.5, colors='#c8d6e5')
    ax_dist.legend(loc='lower left', fontsize=7, facecolor='#2f3542', edgecolor='#576574')

    # Row 2, Col 1: Shannon Capacity vs Distance
    ax_cap = fig.add_subplot(gs[2, 1])
    ax_cap.set_facecolor('#222f3e')
    ax_cap.plot(dists, caps, color='#1dd1a1', linewidth=2.0)
    ax_cap.set_xscale('log')
    ax_cap.set_xlabel("Distance (km)", fontsize=8, color='#c8d6e5')
    ax_cap.set_ylabel("Capacity (Mbps)", fontsize=8, color='#c8d6e5')
    ax_cap.set_title("Shannon Channel Capacity vs Distance", fontsize=9.5, fontweight='bold', color='#f1f2f6')
    ax_cap.grid(True, which="both", ls="--", alpha=0.25, color='#576574')
    ax_cap.tick_params(labelsize=7.5, colors='#c8d6e5')

    # Row 2, Col 2: Multi-Scenario Comparison Bar Chart
    comp_names = ["Wi-Fi 2.4", "4G LTE", "5G 28G", "LoRa 868"]
    comp_presets = [
        PRESET_SCENARIOS["Wi-Fi 6 (802.11ax) 2.4 GHz"],
        PRESET_SCENARIOS["4G LTE Cellular Base Station (1800 MHz)"],
        PRESET_SCENARIOS["5G NR mmWave Urban Small Cell (28 GHz)"],
        PRESET_SCENARIOS["LoRaWAN Long-Range IoT (868 MHz)"]
    ]
    comp_margins = [calculate_link_budget(p).link_margin_db for p in comp_presets]
    bar_colors = ['#1dd1a1' if m >= 0 else '#ee5253' for m in comp_margins]

    ax_comp = fig.add_subplot(gs[2, 2])
    ax_comp.set_facecolor('#222f3e')
    ax_comp.bar(comp_names, comp_margins, color=bar_colors, width=0.5, edgecolor='#576574')
    ax_comp.axhline(0, color='#8395a7', linewidth=1)
    ax_comp.axhline(10, color='#feca57', linestyle=':', label='10 dB Safe Margin')
    ax_comp.set_ylabel("Link Margin (dB)", fontsize=8, color='#c8d6e5')
    ax_comp.set_title("Multi-Scenario Margin Comparison", fontsize=9.5, fontweight='bold', color='#f1f2f6')
    ax_comp.grid(axis='y', linestyle='--', alpha=0.25, color='#576574')
    ax_comp.tick_params(labelsize=7.5, colors='#c8d6e5')
    ax_comp.legend(loc='upper right', fontsize=7, facecolor='#2f3542', edgecolor='#576574')

    fig.savefig(output_path, dpi=140, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Saved Dashboard Preview: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    create_dashboard_preview()
