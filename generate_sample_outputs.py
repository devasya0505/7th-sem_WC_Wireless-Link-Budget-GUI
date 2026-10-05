"""
Sample Outputs Generator
=========================
Generates sample plots, CSV files, and PDF engineering reports
for evaluation, documentation, and project deliverables.
"""

import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for generating figures
import matplotlib.pyplot as plt
import numpy as np

from link_budget_engine import (
    PRESET_SCENARIOS,
    calculate_link_budget,
    sweep_distance,
    LinkBudgetParameters
)
from report_generator import (
    generate_pdf_report,
    export_link_budget_csv,
    export_scenario_comparison_csv
)


def generate_all_samples(output_dir: str = "sample_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating sample outputs into: {os.path.abspath(output_dir)}")

    # 1. Generate Waterfall Power Budget Chart for Wi-Fi 6
    wifi_params = PRESET_SCENARIOS["Wi-Fi 6 (802.11ax) 2.4 GHz"]
    wifi_res = calculate_link_budget(wifi_params)

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=150)
    stages = [s[0] for s in wifi_res.waterfall_stages]
    levels = [s[1] for s in wifi_res.waterfall_stages]
    deltas = [s[2] for s in wifi_res.waterfall_stages]
    
    # Bar colors: Green for gain, Red for loss, Blue for Tx power & final Rx power
    colors_list = []
    for i, (name, val, d) in enumerate(wifi_res.waterfall_stages):
        if i == 0:
            colors_list.append("#3498db")
        elif i == len(wifi_res.waterfall_stages) - 1:
            colors_list.append("#2ecc71" if wifi_res.is_link_viable else "#e74c3c")
        elif d >= 0:
            colors_list.append("#27ae60")
        else:
            colors_list.append("#e67e22")

    bars = ax.bar(stages, levels, color=colors_list, width=0.55, edgecolor="#2c3e50", linewidth=1.2)
    
    # Add horizontal line for sensitivity and noise floor
    ax.axhline(wifi_params.rx_sensitivity_dbm, color='#e74c3c', linestyle='--', linewidth=1.5,
               label=f'Rx Sensitivity ({wifi_params.rx_sensitivity_dbm:.1f} dBm)')
    ax.axhline(wifi_res.receiver_noise_floor_dbm, color='#7f8c8d', linestyle=':', linewidth=1.5,
               label=f'Noise Floor ({wifi_res.receiver_noise_floor_dbm:.1f} dBm)')

    ax.set_ylabel("Power Level (dBm)", fontsize=11, fontweight='bold')
    ax.set_title("RF Link Budget Waterfall Analysis - Wi-Fi 6 (2.4 GHz)", fontsize=12, fontweight='bold', pad=12)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    plt.xticks(rotation=25, ha='right', fontsize=9)
    ax.legend(loc='lower left', framealpha=0.9)

    # Value labels on bars
    for bar, lvl in zip(bars, levels):
        va = 'bottom' if lvl >= 0 else 'top'
        y_pos = lvl + (2 if lvl >= 0 else -4)
        ax.annotate(f"{lvl:.1f} dBm",
                    xy=(bar.get_x() + bar.get_width() / 2, y_pos),
                    ha='center', va=va, fontsize=8, fontweight='bold')

    plt.tight_layout()
    waterfall_path = os.path.join(output_dir, "sample_power_budget_waterfall.png")
    fig.savefig(waterfall_path)
    plt.close(fig)
    print(f"Saved: {waterfall_path}")

    # 2. Generate Prx vs Distance Curve
    lte_params = PRESET_SCENARIOS["4G LTE Cellular Base Station (1800 MHz)"]
    lte_res = calculate_link_budget(lte_params)
    dists, rx_powers, snrs, caps = sweep_distance(lte_params, min_dist_km=0.1, max_dist_km=10.0, points=100)

    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=150)
    ax.plot(dists, rx_powers, color='#2980b9', linewidth=2.5, label='Received Power Prx (dBm)')
    ax.axhline(lte_params.rx_sensitivity_dbm, color='#e74c3c', linestyle='--', linewidth=1.8,
               label=f'Rx Sensitivity ({lte_params.rx_sensitivity_dbm:.1f} dBm)')
    ax.axhline(lte_res.receiver_noise_floor_dbm, color='#7f8c8d', linestyle=':', linewidth=1.5,
               label=f'Thermal Noise Floor ({lte_res.receiver_noise_floor_dbm:.1f} dBm)')

    # Mark max distance
    if lte_res.max_achievable_distance_km > 0:
        ax.axvline(lte_res.max_achievable_distance_km, color='#27ae60', linestyle='-.', linewidth=1.8,
                   label=f'Max Range d_max = {lte_res.max_achievable_distance_km:.2f} km')

    ax.set_xscale('log')
    ax.set_xlabel("Distance (km, log scale)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Received Power (dBm)", fontsize=11, fontweight='bold')
    ax.set_title("Received Power vs. Distance - 4G LTE Urban Cell (COST-231)", fontsize=12, fontweight='bold')
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend(loc='best', framealpha=0.9)
    plt.tight_layout()
    prx_dist_path = os.path.join(output_dir, "sample_prx_vs_distance.png")
    fig.savefig(prx_dist_path)
    plt.close(fig)
    print(f"Saved: {prx_dist_path}")

    # 3. Generate SNR & Shannon Capacity vs Distance Curve
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=150)
    
    ax1.plot(dists, snrs, color='#8e44ad', linewidth=2.2)
    ax1.axhline(10.0, color='#e67e22', linestyle='--', label='10 dB SNR Threshold (QPSK)')
    ax1.axhline(20.0, color='#27ae60', linestyle='--', label='20 dB SNR Threshold (64-QAM)')
    ax1.set_xscale('log')
    ax1.set_xlabel("Distance (km)", fontsize=10, fontweight='bold')
    ax1.set_ylabel("SNR (dB)", fontsize=10, fontweight='bold')
    ax1.set_title("Signal-to-Noise Ratio vs Distance", fontsize=11, fontweight='bold')
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend(loc='lower left', fontsize=8.5)

    ax2.plot(dists, caps, color='#16a085', linewidth=2.2)
    ax2.set_xscale('log')
    ax2.set_xlabel("Distance (km)", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Shannon Capacity (Mbps)", fontsize=10, fontweight='bold')
    ax2.set_title("Theoretical Capacity vs Distance (B = 20 MHz)", fontsize=11, fontweight='bold')
    ax2.grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()
    snr_dist_path = os.path.join(output_dir, "sample_snr_vs_distance.png")
    fig.savefig(snr_dist_path)
    plt.close(fig)
    print(f"Saved: {snr_dist_path}")

    # 4. Generate Multi-Scenario Comparison CSV
    all_evaluated = []
    for name, p in PRESET_SCENARIOS.items():
        r = calculate_link_budget(p)
        all_evaluated.append((p, r))
    
    comparison_csv_path = os.path.join(output_dir, "link_budget_comparison.csv")
    export_scenario_comparison_csv(all_evaluated, comparison_csv_path)
    print(f"Saved: {comparison_csv_path}")

    # 5. Generate PDF Reports for Wi-Fi, Satellite, and Cellular LTE
    wifi_pdf = os.path.join(output_dir, "sample_wifi_report.pdf")
    generate_pdf_report(wifi_params, wifi_res, wifi_pdf, chart_image_path=waterfall_path)
    print(f"Saved: {wifi_pdf}")

    sat_params = PRESET_SCENARIOS["Satellite Ku-band Downlink (GEO 36,000 km)"]
    sat_res = calculate_link_budget(sat_params)
    sat_pdf = os.path.join(output_dir, "sample_satellite_report.pdf")
    generate_pdf_report(sat_params, sat_res, sat_pdf)
    print(f"Saved: {sat_pdf}")

    lte_pdf = os.path.join(output_dir, "sample_cellular_lte_report.pdf")
    generate_pdf_report(lte_params, lte_res, lte_pdf, chart_image_path=prx_dist_path)
    print(f"Saved: {lte_pdf}")

    # 6. Single link CSV export with sweep
    single_csv = os.path.join(output_dir, "sample_lte_link_budget.csv")
    export_link_budget_csv(lte_params, lte_res, single_csv, sweep_data=(dists, rx_powers, snrs, caps))
    print(f"Saved: {single_csv}")

    print("All sample outputs generated successfully!")


if __name__ == "__main__":
    generate_all_samples()
