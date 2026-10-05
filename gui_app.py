"""
Wireless Link Budget GUI Application
====================================
Course: 3171608 - Wireless Communication (WC)
Project: Micro-Project - Wireless Link Budget GUI

Modern, responsive RF engineering desktop application built with
Python, ttkbootstrap / Tkinter, and Matplotlib.
"""

import os
import sys
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List, Optional, Tuple

import warnings
warnings.filterwarnings("ignore", message=".*non-positive xlim.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from link_budget_engine import (
    LinkBudgetParameters,
    LinkBudgetResults,
    calculate_link_budget,
    sweep_distance,
    solve_max_achievable_distance,
    evaluate_path_loss,
    PRESET_SCENARIOS,
    dbm_to_watts,
    watts_to_dbm
)
from report_generator import (
    generate_pdf_report,
    export_link_budget_csv,
    export_scenario_comparison_csv
)


class WirelessLinkBudgetApp:
    """Main Application GUI for Wireless Link Budget Analysis."""

    THEMES = ["darkly", "superhero", "flatly", "cosmo", "dracula-dark", "nord-dark", "bootstrap-dark", "bootstrap-light"]

    PATH_LOSS_MODELS = [
        "Free Space Path Loss (FSPL)",
        "Two-Ray Ground Reflection Model",
        "Log-Distance Model",
        "Okumura-Hata Model",
        "COST-231 Hata Model"
    ]

    ENVIRONMENTS = [
        "Urban Small/Medium City",
        "Urban Large City",
        "Suburban Area",
        "Open / Rural Area"
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Wireless Link Budget GUI - WC Micro-Project (3171608)")
        self.root.geometry("1280x820")
        self.root.minsize(1024, 700)

        # Current state
        self.current_params = LinkBudgetParameters()
        self.current_results = LinkBudgetResults()
        self.comparison_scenarios: List[Tuple[LinkBudgetParameters, LinkBudgetResults]] = []

        # Setup GUI Components
        self._build_header_toolbar()
        self._build_main_notebook()
        self._build_status_bar()

        # Load initial preset and compute
        self._load_preset("Wi-Fi 6 (802.11ax) 2.4 GHz")

    def _build_header_toolbar(self):
        """Top banner with title, presets dropdown, theme switcher, and calculate button."""
        header_frame = ttk.Frame(self.root, padding=(12, 8))
        header_frame.pack(side=tk.TOP, fill=tk.X)

        # Title Block
        title_box = ttk.Frame(header_frame)
        title_box.pack(side=tk.LEFT, fill=tk.Y)

        title_lbl = ttk.Label(
            title_box,
            text="📡 Wireless Link Budget GUI",
            font=("Helvetica", 14, "bold")
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ttk.Label(
            title_box,
            text="GTU 7th Sem IT | 3171608 - Wireless Communication Micro-Project",
            font=("Helvetica", 8)
        )
        subtitle_lbl.pack(anchor="w")

        # Action / Preset Controls on Right
        ctrl_box = ttk.Frame(header_frame)
        ctrl_box.pack(side=tk.RIGHT, fill=tk.Y)

        # Preset Dropdown
        ttk.Label(ctrl_box, text="Scenario Preset:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(8, 4))
        self.preset_var = tk.StringVar(value="Wi-Fi 6 (802.11ax) 2.4 GHz")
        self.preset_combo = ttk.Combobox(
            ctrl_box,
            textvariable=self.preset_var,
            values=list(PRESET_SCENARIOS.keys()),
            state="readonly",
            width=28
        )
        self.preset_combo.pack(side=tk.LEFT, padx=4)
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

        # Calculate Button
        calc_btn = ttk.Button(
            ctrl_box,
            text="⚡ Compute Link Budget",
            command=self.compute_and_update_ui
        )
        calc_btn.pack(side=tk.LEFT, padx=8)

        # Theme Switcher (if ttkbootstrap available)
        if HAS_TTKBOOTSTRAP and isinstance(self.root, tb.Window):
            ttk.Label(ctrl_box, text="Theme:", font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(8, 4))
            self.theme_var = tk.StringVar(value=self.root.style.theme.name)
            theme_combo = ttk.Combobox(
                ctrl_box,
                textvariable=self.theme_var,
                values=self.THEMES,
                state="readonly",
                width=10
            )
            theme_combo.pack(side=tk.LEFT, padx=4)
            theme_combo.bind("<<ComboboxSelected>>", self._on_theme_changed)

    def _on_theme_changed(self, event=None):
        theme = self.theme_var.get()
        if HAS_TTKBOOTSTRAP and isinstance(self.root, tb.Window):
            self.root.style.theme_use(theme)
            self._update_all_charts()

    def _build_main_notebook(self):
        """Build tabbed interface."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 4))

        # Tab 1: Single Link Calculator
        self.tab_calculator = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_calculator, text=" 📊 Link Budget Calculator ")
        self._build_calculator_tab()

        # Tab 2: Distance Sweep & Channel Capacity
        self.tab_sweeps = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sweeps, text=" 📈 Parametric Sweeps & Capacity ")
        self._build_sweeps_tab()

        # Tab 3: Multi-Scenario Comparison
        self.tab_compare = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_compare, text=" ⚖ Scenario Comparator ")
        self._build_comparison_tab()

        # Tab 4: Theory & Formulas
        self.tab_theory = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_theory, text=" 📖 WC Theory & Formulas Reference ")
        self._build_theory_tab()

    def _build_calculator_tab(self):
        """Split pane: Left panel for parameters, Right panel for results & waterfall chart."""
        paned = ttk.Panedwindow(self.tab_calculator, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: Scrollable Input Form Frame
        left_container = ttk.Frame(paned, width=420)
        paned.add(left_container, weight=1)

        # Canvas for scrollable inputs
        canvas = tk.Canvas(left_container, highlightthickness=0, width=410)
        scrollbar = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=canvas.yview)
        self.input_scroll_frame = ttk.Frame(canvas, padding=8)

        self.input_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.input_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate Input Form Widgets
        self._build_input_fields(self.input_scroll_frame)

        # Right: Results Cards + Embedded Plot + Export Toolbar
        right_container = ttk.Frame(paned)
        paned.add(right_container, weight=3)
        self._build_results_and_charts_panel(right_container)

    def _build_input_fields(self, parent):
        """Construct transmitter, channel, receiver, and environmental input controls."""
        # 1. Transmitter Parameters Section
        tx_box = ttk.LabelFrame(parent, text=" 🚀 Transmitter (Tx) Parameters ", padding=8)
        tx_box.pack(fill=tk.X, pady=4)

        self.var_tx_power_dbm = tk.DoubleVar(value=20.0)
        self.var_tx_antenna_gain = tk.DoubleVar(value=2.15)
        self.var_tx_cable_loss = tk.DoubleVar(value=1.0)
        self.var_tx_height = tk.DoubleVar(value=30.0)

        self._create_num_entry(tx_box, "Tx Power (dBm):", self.var_tx_power_dbm, 0, unit="dBm")
        self._create_num_entry(tx_box, "Tx Antenna Gain:", self.var_tx_antenna_gain, 1, unit="dBi")
        self._create_num_entry(tx_box, "Tx Cable / Filter Loss:", self.var_tx_cable_loss, 2, unit="dB")
        self._create_num_entry(tx_box, "Tx Antenna Height (hb):", self.var_tx_height, 3, unit="meters")

        # 2. Channel & Path Loss Section
        ch_box = ttk.LabelFrame(parent, text=" 🌐 Channel & Propagation Model ", padding=8)
        ch_box.pack(fill=tk.X, pady=4)

        self.var_frequency_mhz = tk.DoubleVar(value=2400.0)
        self.var_distance_km = tk.DoubleVar(value=0.5)
        self.var_path_loss_model = tk.StringVar(value="Free Space Path Loss (FSPL)")
        self.var_path_loss_exp = tk.DoubleVar(value=3.0)
        self.var_rx_height = tk.DoubleVar(value=1.5)
        self.var_env_type = tk.StringVar(value="Urban Small/Medium City")

        self._create_num_entry(ch_box, "Carrier Frequency:", self.var_frequency_mhz, 0, unit="MHz")
        self._create_num_entry(ch_box, "Link Distance:", self.var_distance_km, 1, unit="km")

        # Propagation Model Dropdown
        row = 2
        ttk.Label(ch_box, text="Path Loss Model:").grid(row=row, column=0, sticky="w", pady=2)
        model_cb = ttk.Combobox(
            ch_box,
            textvariable=self.var_path_loss_model,
            values=self.PATH_LOSS_MODELS,
            state="readonly",
            width=22
        )
        model_cb.grid(row=row, column=1, sticky="ew", pady=2, padx=4)
        model_cb.bind("<<ComboboxSelected>>", self._on_model_changed)

        # Path Loss Exponent (for log-distance)
        self.row_ple = self._create_num_entry(ch_box, "Path Loss Exponent (n):", self.var_path_loss_exp, 3, unit="2-5")

        # Antenna height Rx (for Hata & Two-Ray)
        self.row_rx_h = self._create_num_entry(ch_box, "Rx Antenna Height (hm):", self.var_rx_height, 4, unit="meters")

        # Environment Type (for Okumura-Hata)
        row = 5
        self.lbl_env = ttk.Label(ch_box, text="Environment:")
        self.lbl_env.grid(row=row, column=0, sticky="w", pady=2)
        self.env_cb = ttk.Combobox(
            ch_box,
            textvariable=self.var_env_type,
            values=self.ENVIRONMENTS,
            state="readonly",
            width=22
        )
        self.env_cb.grid(row=row, column=1, sticky="ew", pady=2, padx=4)

        # 3. Environmental & Margins Section
        env_box = ttk.LabelFrame(parent, text=" 🌧 Environmental & Extra Margins ", padding=8)
        env_box.pack(fill=tk.X, pady=4)

        self.var_rain_loss = tk.DoubleVar(value=0.0)
        self.var_atm_loss = tk.DoubleVar(value=0.0)
        self.var_obstacle_loss = tk.DoubleVar(value=0.0)
        self.var_fade_margin = tk.DoubleVar(value=10.0)

        self._create_num_entry(env_box, "Rain Attenuation:", self.var_rain_loss, 0, unit="dB")
        self._create_num_entry(env_box, "Atmospheric Gas Loss:", self.var_atm_loss, 1, unit="dB")
        self._create_num_entry(env_box, "Obstacle / Wall Loss:", self.var_obstacle_loss, 2, unit="dB")
        self._create_num_entry(env_box, "Log-Normal Fade Margin:", self.var_fade_margin, 3, unit="dB")

        # 4. Receiver Parameters Section
        rx_box = ttk.LabelFrame(parent, text=" 🎯 Receiver (Rx) Parameters ", padding=8)
        rx_box.pack(fill=tk.X, pady=4)

        self.var_rx_antenna_gain = tk.DoubleVar(value=2.15)
        self.var_rx_cable_loss = tk.DoubleVar(value=1.0)
        self.var_rx_sensitivity = tk.DoubleVar(value=-90.0)
        self.var_noise_figure = tk.DoubleVar(value=5.0)
        self.var_bandwidth_mhz = tk.DoubleVar(value=20.0)
        self.var_temperature_k = tk.DoubleVar(value=290.0)

        self._create_num_entry(rx_box, "Rx Antenna Gain:", self.var_rx_antenna_gain, 0, unit="dBi")
        self._create_num_entry(rx_box, "Rx Cable / Filter Loss:", self.var_rx_cable_loss, 1, unit="dB")
        self._create_num_entry(rx_box, "Rx Sensitivity:", self.var_rx_sensitivity, 2, unit="dBm")
        self._create_num_entry(rx_box, "Rx Noise Figure (NF):", self.var_noise_figure, 3, unit="dB")
        self._create_num_entry(rx_box, "Channel Bandwidth:", self.var_bandwidth_mhz, 4, unit="MHz")
        self._create_num_entry(rx_box, "System Temp (T):", self.var_temperature_k, 5, unit="Kelvin")

        # Bottom Action Buttons
        btn_frame = ttk.Frame(parent, padding=(0, 8))
        btn_frame.pack(fill=tk.X)

        recalc_btn = ttk.Button(btn_frame, text="⚡ Recalculate", command=self.compute_and_update_ui)
        recalc_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        add_comp_btn = ttk.Button(
            btn_frame,
            text="➕ Add to Comparison",
            command=self._add_current_to_comparison
        )
        add_comp_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    def _create_num_entry(self, parent, label_text, var, row, unit=""):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(parent, textvariable=var, width=12)
        entry.grid(row=row, column=1, sticky="e", pady=2, padx=4)
        if unit:
            ttk.Label(parent, text=unit, font=("Helvetica", 8)).grid(row=row, column=2, sticky="w", pady=2)
        return (row, entry)

    def _on_model_changed(self, event=None):
        """Dynamically enable/disable fields relevant to selected model."""
        pass  # Kept active for all models to allow continuous exploration

    def _build_results_and_charts_panel(self, parent):
        """Build result cards at the top, embedded matplotlib waterfall at bottom, and export buttons."""
        top_results_frame = ttk.Frame(parent, padding=8)
        top_results_frame.pack(fill=tk.X)

        # Status Banner
        self.banner_frame = ttk.Frame(top_results_frame, padding=6)
        self.banner_frame.pack(fill=tk.X, pady=(0, 6))

        self.lbl_status_main = ttk.Label(
            self.banner_frame,
            text="LINK STATUS: READY",
            font=("Helvetica", 11, "bold")
        )
        self.lbl_status_main.pack(anchor="w")

        self.lbl_status_sub = ttk.Label(
            self.banner_frame,
            text="Press Compute or select a Preset scenario to analyze.",
            font=("Helvetica", 9)
        )
        self.lbl_status_sub.pack(anchor="w")

        # KPI Metric Cards Grid
        kpi_grid = ttk.Frame(top_results_frame)
        kpi_grid.pack(fill=tk.X)

        self.card_margin = self._create_kpi_card(kpi_grid, "LINK MARGIN", "0.00 dB", 0, 0)
        self.card_prx = self._create_kpi_card(kpi_grid, "RECEIVED POWER", "0.00 dBm", 0, 1)
        self.card_eirp = self._create_kpi_card(kpi_grid, "EIRP (TX POWER)", "0.00 dBm", 0, 2)
        self.card_path_loss = self._create_kpi_card(kpi_grid, "TOTAL PATH LOSS", "0.00 dB", 0, 3)

        self.card_snr = self._create_kpi_card(kpi_grid, "SNR (SIGNAL/NOISE)", "0.00 dB", 1, 0)
        self.card_max_d = self._create_kpi_card(kpi_grid, "MAX COVERAGE RANGE", "0.00 km", 1, 1)
        self.card_capacity = self._create_kpi_card(kpi_grid, "SHANNON CAPACITY", "0.00 Mbps", 1, 2)
        self.card_noise_floor = self._create_kpi_card(kpi_grid, "NOISE FLOOR", "-174 dBm", 1, 3)

        # Matplotlib Embedded Figure for Waterfall Analysis
        chart_frame = ttk.Frame(parent, padding=4)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        self.fig_waterfall = Figure(figsize=(7, 3.8), dpi=100)
        self.ax_waterfall = self.fig_waterfall.add_subplot(111)
        self.fig_waterfall.tight_layout()

        self.canvas_waterfall = FigureCanvasTkAgg(self.fig_waterfall, master=chart_frame)
        self.canvas_waterfall.draw()
        self.canvas_waterfall.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Export & Action Bar at Bottom of Panel
        export_bar = ttk.Frame(parent, padding=(8, 4))
        export_bar.pack(fill=tk.X)

        pdf_btn = ttk.Button(export_bar, text="📄 Export PDF Report", command=self._export_pdf)
        pdf_btn.pack(side=tk.LEFT, padx=4)

        csv_btn = ttk.Button(export_bar, text="📊 Export CSV Data", command=self._export_csv)
        csv_btn.pack(side=tk.LEFT, padx=4)

        img_btn = ttk.Button(export_bar, text="🖼 Save Plot (PNG)", command=self._export_chart_png)
        img_btn.pack(side=tk.LEFT, padx=4)

    def _create_kpi_card(self, parent, title, initial_val, row, col):
        card = ttk.LabelFrame(parent, padding=4)
        card.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
        parent.columnconfigure(col, weight=1)

        title_lbl = ttk.Label(card, text=title, font=("Helvetica", 8, "bold"))
        title_lbl.pack(anchor="w")

        val_lbl = ttk.Label(card, text=initial_val, font=("Helvetica", 11, "bold"))
        val_lbl.pack(anchor="w", pady=(2, 0))

        return val_lbl

    def _build_sweeps_tab(self):
        """Parametric sweep tab across distance, SNR, and Shannon channel capacity."""
        top_ctrl = ttk.Frame(self.tab_sweeps, padding=8)
        top_ctrl.pack(fill=tk.X)

        ttk.Label(top_ctrl, text="Distance Range:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=4)

        ttk.Label(top_ctrl, text="Min (km):").pack(side=tk.LEFT, padx=2)
        self.var_sweep_min = tk.DoubleVar(value=0.05)
        ttk.Entry(top_ctrl, textvariable=self.var_sweep_min, width=7).pack(side=tk.LEFT, padx=4)

        ttk.Label(top_ctrl, text="Max (km):").pack(side=tk.LEFT, padx=2)
        self.var_sweep_max = tk.DoubleVar(value=10.0)
        ttk.Entry(top_ctrl, textvariable=self.var_sweep_max, width=7).pack(side=tk.LEFT, padx=4)

        ttk.Label(top_ctrl, text="Points:").pack(side=tk.LEFT, padx=2)
        self.var_sweep_points = tk.IntVar(value=100)
        ttk.Entry(top_ctrl, textvariable=self.var_sweep_points, width=6).pack(side=tk.LEFT, padx=4)

        sweep_btn = ttk.Button(top_ctrl, text="🔄 Run Distance Sweep", command=self._update_sweep_plot)
        sweep_btn.pack(side=tk.LEFT, padx=8)

        # Plot area
        sweep_plot_frame = ttk.Frame(self.tab_sweeps, padding=4)
        sweep_plot_frame.pack(fill=tk.BOTH, expand=True)

        self.fig_sweep = Figure(figsize=(9, 5), dpi=100)
        self.ax_sweep_prx = self.fig_sweep.add_subplot(121)
        self.ax_sweep_snr = self.fig_sweep.add_subplot(122)
        self.fig_sweep.tight_layout()

        self.canvas_sweep = FigureCanvasTkAgg(self.fig_sweep, master=sweep_plot_frame)
        self.canvas_sweep.draw()
        self.canvas_sweep.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas_sweep, sweep_plot_frame)
        toolbar.update()

    def _build_comparison_tab(self):
        """Side-by-side comparison of multiple link budget scenarios."""
        top_ctrl = ttk.Frame(self.tab_compare, padding=8)
        top_ctrl.pack(fill=tk.X)

        ttk.Label(
            top_ctrl,
            text="Multi-Scenario Comparison Matrix",
            font=("Helvetica", 11, "bold")
        ).pack(side=tk.LEFT, padx=4)

        add_all_presets_btn = ttk.Button(
            top_ctrl,
            text="Load All Standard Presets",
            command=self._load_all_presets_for_comparison
        )
        add_all_presets_btn.pack(side=tk.LEFT, padx=6)

        clear_comp_btn = ttk.Button(
            top_ctrl,
            text="Clear Comparison List",
            command=self._clear_comparison
        )
        clear_comp_btn.pack(side=tk.LEFT, padx=6)

        export_comp_btn = ttk.Button(
            top_ctrl,
            text="Export Comparison CSV",
            command=self._export_comparison_csv
        )
        export_comp_btn.pack(side=tk.LEFT, padx=6)

        # Split pane for comparison: Table on Top, Comparative Bar Chart on Bottom
        paned_comp = ttk.Panedwindow(self.tab_compare, orient=tk.VERTICAL)
        paned_comp.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Table container
        tree_frame = ttk.Frame(paned_comp, height=220)
        paned_comp.add(tree_frame, weight=1)

        cols = ("Metric", "Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4")
        self.comp_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.comp_tree.heading(col, text=col)
            self.comp_tree.column(col, width=140, anchor="center")
        self.comp_tree.column("Metric", width=220, anchor="w")

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.comp_tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.comp_tree.xview)
        self.comp_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.comp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Comparison Bar Chart Container
        chart_comp_frame = ttk.Frame(paned_comp, height=240)
        paned_comp.add(chart_comp_frame, weight=1)

        self.fig_comp = Figure(figsize=(8, 3.5), dpi=100)
        self.ax_comp = self.fig_comp.add_subplot(111)
        self.fig_comp.tight_layout()

        self.canvas_comp = FigureCanvasTkAgg(self.fig_comp, master=chart_comp_frame)
        self.canvas_comp.draw()
        self.canvas_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _build_theory_tab(self):
        """Educational documentation and theory guide for academic evaluation."""
        text_container = ttk.Frame(self.tab_theory, padding=12)
        text_container.pack(fill=tk.BOTH, expand=True)

        txt_scroll = ttk.Scrollbar(text_container)
        txt_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        theory_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            yscrollcommand=txt_scroll.set,
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        theory_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt_scroll.config(command=theory_text.yview)

        theory_content = """
========================================================================================
WIRELESS LINK BUDGET ANALYSIS - THEORY, MATHEMATICAL EQUATIONS & RF DESIGN GUIDE
Course: 3171608 - Wireless Communication (WC) | GTU 7th Semester IT
========================================================================================

1. INTRODUCTION TO RF LINK BUDGET
----------------------------------------------------------------------------------------
A wireless link budget is the accounting of all gains and losses from the transmitter,
through the wireless medium (free space, atmosphere, buildings), to the receiver in a 
telecommunication system. It evaluates whether the received signal strength (Prx) is
sufficient for reliable demodulation above the receiver's thermal noise floor and
sensitivity threshold.

2. TRANSMITTER EFFECTIVE ISOTROPIC RADIATED POWER (EIRP)
----------------------------------------------------------------------------------------
EIRP represents the total radiated power of an equivalent isotropic antenna emitting
uniform radiation in all directions:

    EIRP (dBm) = Ptx (dBm) + Gtx (dBi) - Ltx (dB)
    EIRP (Watts) = 10 ^ ((EIRP(dBm) - 30) / 10)

Where:
  - Ptx: Transmitter power output (dBm or Watts: P(dBm) = 10*log10(P(W)*1000))
  - Gtx: Transmit antenna gain relative to isotropic radiator (dBi)
  - Ltx: Transmitter cable, filter, and connector insertion losses (dB)

3. PROPAGATION PATH LOSS MODELS
----------------------------------------------------------------------------------------
A. Free Space Path Loss (FSPL) - Friis Transmission Equation
    Models ideal propagation in vacuum without obstacles or reflections:
    
    FSPL (dB) = 20 * log10(d) + 20 * log10(f) + 20 * log10(4*pi / c)
    In practical RF engineering units (distance in km, frequency in MHz):
    
    FSPL (dB) = 32.44 + 20 * log10(d_km) + 20 * log10(f_MHz)

B. Two-Ray Ground Reflection Model
    Accounts for line-of-sight (LOS) direct wave and ground-reflected multipath wave:
    Crossover distance: d_cross = (4 * pi * htx * hrx) / lambda
    
    For d >= d_cross (far-field roll-off 40 dB/decade):
    PL_2ray (dB) = 40 * log10(d) - 20 * log10(htx) - 20 * log10(hrx)

C. Log-Distance Path Loss Model
    Characterizes empirical indoor / cluttered outdoor environments with shadowing:
    
    PL(d) (dB) = PL(d0) + 10 * n * log10(d / d0) + X_sigma
    Where:
      - n: Path loss exponent (2.0 = Free space, 2.7-3.5 = Urban micro, 3.0-5.0 = Shadowed indoor)
      - d0: Reference distance (typically 1 meter indoors, 1 km outdoors)
      - X_sigma: Zero-mean Gaussian distributed random variable for log-normal shadowing

D. Okumura-Hata Model (150 MHz - 1500 MHz Cellular)
    Standard empirical model for cellular macro-cells:
    PL_urban = 69.55 + 26.16*log10(f) - 13.82*log10(hb) - a(hm) + [44.9 - 6.55*log10(hb)]*log10(d)
    
    Mobile height correction factor a(hm):
    a(hm) = [1.1*log10(f) - 0.7]*hm - [1.56*log10(f) - 0.8] (Medium/Small city)

E. COST-231 Hata Model (1500 MHz - 2000 MHz PCS)
    Extends Hata to 2 GHz personal communication systems:
    PL_cost = 46.3 + 33.9*log10(f) - 13.82*log10(hb) - a(hm) + [44.9 - 6.55*log10(hb)]*log10(d) + Cm

4. RECEIVED POWER (Prx) & FRIIS EQUATION
----------------------------------------------------------------------------------------
The net power arriving at the receiver input terminals:

    Prx (dBm) = EIRP (dBm) - PL_model (dB) - L_environmental (dB) + Grx (dBi) - Lrx (dB)

Where:
  - L_environmental = Rain Loss + Atmospheric Loss + Obstacle Loss + Fade Margin
  - Grx: Receiver antenna gain (dBi)
  - Lrx: Receiver cable, connector, and RF front-end loss (dB)

5. THERMAL NOISE FLOOR & NOISE FIGURE
----------------------------------------------------------------------------------------
Johnson-Nyquist thermal noise generated in the receiver front-end:
    N = k * T * B  (Watts)
    
In logarithmic units (dBm):
    N (dBm) = -174 dBm/Hz + 10 * log10(B_Hz) + NF (dB)

Where:
  - k = 1.380649e-23 J/K (Boltzmann's constant)
  - T: System noise temperature in Kelvin (Standard 290 K)
  - B: Effective receiver noise bandwidth in Hz
  - NF: Receiver Noise Figure in dB (degradation relative to ideal noiseless receiver)

6. SIGNAL-TO-NOISE RATIO (SNR) & LINK MARGIN
----------------------------------------------------------------------------------------
A. Signal-to-Noise Ratio:
    SNR (dB) = Prx (dBm) - N (dBm)

B. Link Margin (Fade Margin):
    Link Margin (dB) = Prx (dBm) - Prx_sensitivity (dBm)

Criteria for Link Viability:
  - Margin >= 10 dB: EXCELLENT link, resilient against rain, shadowing, and fading.
  - 0 dB <= Margin < 10 dB: MARGINAL link, operational but sensitive to environmental variations.
  - Margin < 0 dB: LINK DOWN / FAILED, insufficient signal power arriving at demodulator.

7. SHANNON-HARTLEY CHANNEL CAPACITY THEOREM
----------------------------------------------------------------------------------------
The maximum theoretical error-free data rate over a continuous channel of bandwidth B:

    C = B * log2(1 + SNR_linear)   (bits per second)
    Where SNR_linear = 10 ^ (SNR_dB / 10)

========================================================================================
APPLICATION PRESETS QUICK GUIDE:
• Wi-Fi 6 (2.4 GHz & 5 GHz): Indoor WLAN with multi-wall penetration losses.
• 4G LTE Urban Macro: 20W cellular base station serving smartphones over 2 km.
• 5G NR mmWave: 28 GHz high-throughput micro-cell with phased array beamforming.
• GEO Satellite: 36,000 km Ku-band link with 120+ dB free space loss.
• LoRaWAN IoT: Long-range Sub-GHz sensor link operating at -137 dBm sensitivity.
• Microwave Backhaul: Point-to-point 18 GHz high-reliability telecom tower link.
========================================================================================
"""
        theory_text.insert(tk.END, theory_content)
        theory_text.config(state=tk.DISABLED)

    def _build_status_bar(self):
        """Bottom status bar with information text."""
        status_bar = ttk.Frame(self.root, padding=(8, 2))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_text_var = tk.StringVar(value="System Ready. Course: 3171608 - Wireless Communication.")
        ttk.Label(
            status_bar,
            textvariable=self.status_text_var,
            font=("Helvetica", 8)
        ).pack(side=tk.LEFT)

    def _on_preset_selected(self, event=None):
        name = self.preset_var.get()
        self._load_preset(name)

    def _load_preset(self, preset_name: str):
        if preset_name not in PRESET_SCENARIOS:
            return
        p = PRESET_SCENARIOS[preset_name]

        # Populate form variables
        self.var_tx_power_dbm.set(p.tx_power_dbm)
        self.var_tx_antenna_gain.set(p.tx_antenna_gain_dbi)
        self.var_tx_cable_loss.set(p.tx_cable_loss_db)
        self.var_tx_height.set(p.tx_antenna_height_m)

        self.var_frequency_mhz.set(p.frequency_mhz)
        self.var_distance_km.set(p.distance_km)
        self.var_path_loss_model.set(p.path_loss_model)
        self.var_path_loss_exp.set(p.path_loss_exponent)
        self.var_rx_height.set(p.rx_antenna_height_m)
        self.var_env_type.set(p.environment_type)

        self.var_rain_loss.set(p.rain_attenuation_db)
        self.var_atm_loss.set(p.atmospheric_loss_db)
        self.var_obstacle_loss.set(p.obstacle_loss_db)
        self.var_fade_margin.set(p.fade_margin_db)

        self.var_rx_antenna_gain.set(p.rx_antenna_gain_dbi)
        self.var_rx_cable_loss.set(p.rx_cable_loss_db)
        self.var_rx_sensitivity.set(p.rx_sensitivity_dbm)
        self.var_noise_figure.set(p.noise_figure_db)
        self.var_bandwidth_mhz.set(p.bandwidth_mhz)
        self.var_temperature_k.set(p.temperature_k)

        # Set sweep bounds according to scenario scale
        if p.distance_km > 100:
            self.var_sweep_min.set(100.0)
            self.var_sweep_max.set(p.distance_km * 1.5)
        elif p.distance_km < 0.2:
            self.var_sweep_min.set(0.005)
            self.var_sweep_max.set(0.5)
        else:
            self.var_sweep_min.set(0.1)
            self.var_sweep_max.set(max(p.distance_km * 3.0, 5.0))

        self.compute_and_update_ui()

    def _read_current_params(self) -> LinkBudgetParameters:
        """Read values from UI widgets into LinkBudgetParameters."""
        return LinkBudgetParameters(
            scenario_name=self.preset_var.get(),
            tx_power_dbm=float(self.var_tx_power_dbm.get()),
            tx_antenna_gain_dbi=float(self.var_tx_antenna_gain.get()),
            tx_cable_loss_db=float(self.var_tx_cable_loss.get()),
            tx_antenna_height_m=float(self.var_tx_height.get()),
            frequency_mhz=float(self.var_frequency_mhz.get()),
            distance_km=float(self.var_distance_km.get()),
            path_loss_model=self.var_path_loss_model.get(),
            path_loss_exponent=float(self.var_path_loss_exp.get()),
            rx_antenna_height_m=float(self.var_rx_height.get()),
            environment_type=self.var_env_type.get(),
            rain_attenuation_db=float(self.var_rain_loss.get()),
            atmospheric_loss_db=float(self.var_atm_loss.get()),
            obstacle_loss_db=float(self.var_obstacle_loss.get()),
            fade_margin_db=float(self.var_fade_margin.get()),
            rx_antenna_gain_dbi=float(self.var_rx_antenna_gain.get()),
            rx_cable_loss_db=float(self.var_rx_cable_loss.get()),
            rx_sensitivity_dbm=float(self.var_rx_sensitivity.get()),
            noise_figure_db=float(self.var_noise_figure.get()),
            bandwidth_mhz=float(self.var_bandwidth_mhz.get()),
            temperature_k=float(self.var_temperature_k.get())
        )

    def compute_and_update_ui(self):
        """Execute calculation and refresh all UI displays and plots."""
        try:
            self.current_params = self._read_current_params()
            self.current_results = calculate_link_budget(self.current_params)
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Invalid parameters entered:\n{e}")
            return

        # Update KPI Cards
        r = self.current_results
        p = self.current_params

        self.card_margin.config(text=f"{r.link_margin_db:+.2f} dB")
        self.card_prx.config(text=f"{r.rx_power_dbm:.2f} dBm")
        self.card_eirp.config(text=f"{r.eirp_dbm:.2f} dBm ({r.eirp_w:.2f} W)")
        self.card_path_loss.config(text=f"{r.total_path_loss_db:.2f} dB")

        self.card_snr.config(text=f"{r.snr_db:.2f} dB")
        self.card_max_d.config(text=f"{r.max_achievable_distance_km:.3f} km")
        self.card_capacity.config(text=f"{r.shannon_capacity_mbps:.2f} Mbps")
        self.card_noise_floor.config(text=f"{r.receiver_noise_floor_dbm:.2f} dBm")

        # Update Status Banner
        if r.is_link_viable:
            status_text = f"✔ PASS &mdash; {r.status_text}"
            sub_text = f"Received Power ({r.rx_power_dbm:.2f} dBm) exceeds Sensitivity ({p.rx_sensitivity_dbm:.2f} dBm) by {r.link_margin_db:.2f} dB."
        else:
            status_text = f"✖ FAIL &mdash; {r.status_text}"
            sub_text = f"Signal is {abs(r.link_margin_db):.2f} dB below receiver sensitivity threshold."

        self.lbl_status_main.config(text=status_text)
        self.lbl_status_sub.config(text=sub_text)

        # Redraw Waterfall Chart
        self._draw_waterfall_chart()

        # Update Sweep Tab
        self._update_sweep_plot()

        self.status_text_var.set(
            f"Calculated: {p.scenario_name} | Margin: {r.link_margin_db:+.2f} dB | Prx: {r.rx_power_dbm:.2f} dBm | Max Dist: {r.max_achievable_distance_km:.2f} km"
        )

    def _draw_waterfall_chart(self):
        """Render the power budget waterfall breakdown bar chart."""
        self.ax_waterfall.clear()
        r = self.current_results
        p = self.current_params

        stages = [s[0] for s in r.waterfall_stages]
        levels = [s[1] for s in r.waterfall_stages]
        deltas = [s[2] for s in r.waterfall_stages]

        colors_list = []
        for i, (name, val, d) in enumerate(r.waterfall_stages):
            if i == 0:
                colors_list.append("#3498db")
            elif i == len(r.waterfall_stages) - 1:
                colors_list.append("#2ecc71" if r.is_link_viable else "#e74c3c")
            elif d >= 0:
                colors_list.append("#27ae60")
            else:
                colors_list.append("#e67e22")

        bars = self.ax_waterfall.bar(stages, levels, color=colors_list, width=0.55, edgecolor="#2c3e50")

        # Threshold lines
        self.ax_waterfall.axhline(
            p.rx_sensitivity_dbm,
            color="#e74c3c",
            linestyle="--",
            linewidth=1.5,
            label=f"Sensitivity ({p.rx_sensitivity_dbm:.1f} dBm)"
        )
        self.ax_waterfall.axhline(
            r.receiver_noise_floor_dbm,
            color="#7f8c8d",
            linestyle=":",
            linewidth=1.4,
            label=f"Noise Floor ({r.receiver_noise_floor_dbm:.1f} dBm)"
        )

        self.ax_waterfall.set_ylabel("Power Level (dBm)", fontsize=9, fontweight="bold")
        self.ax_waterfall.set_title(
            f"RF Link Budget Waterfall: {p.scenario_name}",
            fontsize=10,
            fontweight="bold",
            pad=10
        )
        self.ax_waterfall.grid(axis="y", linestyle="--", alpha=0.4)
        self.ax_waterfall.tick_params(axis="x", rotation=20, labelsize=8)
        self.ax_waterfall.tick_params(axis="y", labelsize=8)
        self.ax_waterfall.legend(loc="lower left", fontsize=8, framealpha=0.85)

        # Annotations on bars
        for bar, lvl in zip(bars, levels):
            y_pos = lvl + (1.5 if lvl >= 0 else -3.5)
            self.ax_waterfall.annotate(
                f"{lvl:.1f}",
                xy=(bar.get_x() + bar.get_width() / 2, y_pos),
                ha="center",
                va="bottom" if lvl >= 0 else "top",
                fontsize=7.5,
                fontweight="bold"
            )

        self.fig_waterfall.tight_layout()
        self.canvas_waterfall.draw()

    def _update_sweep_plot(self):
        """Recalculate parametric distance sweep and plot."""
        try:
            min_d = float(self.var_sweep_min.get())
            max_d = float(self.var_sweep_max.get())
            points = int(self.var_sweep_points.get())
        except ValueError:
            return

        p = self.current_params
        r = self.current_results
        dists, rx_powers, snrs, caps = sweep_distance(p, min_d, max_d, points)

        # Clear and recreate subplots to prevent twinx stacking
        self.fig_sweep.clear()
        self.ax_sweep_prx = self.fig_sweep.add_subplot(121)
        self.ax_sweep_snr = self.fig_sweep.add_subplot(122)

        # Subplot 1: Received Power vs Distance
        self.ax_sweep_prx.plot(dists, rx_powers, color="#2980b9", linewidth=2.2, label="Received Power (Prx)")
        self.ax_sweep_prx.axhline(
            p.rx_sensitivity_dbm,
            color="#e74c3c",
            linestyle="--",
            linewidth=1.5,
            label=f"Sensitivity ({p.rx_sensitivity_dbm:.1f} dBm)"
        )
        self.ax_sweep_prx.axhline(
            r.receiver_noise_floor_dbm,
            color="#7f8c8d",
            linestyle=":",
            linewidth=1.2,
            label=f"Noise Floor ({r.receiver_noise_floor_dbm:.1f} dBm)"
        )

        if r.max_achievable_distance_km > 0 and min_d <= r.max_achievable_distance_km <= max_d:
            self.ax_sweep_prx.axvline(
                r.max_achievable_distance_km,
                color="#27ae60",
                linestyle="-.",
                linewidth=1.5,
                label=f"d_max = {r.max_achievable_distance_km:.2f} km"
            )

        self.ax_sweep_prx.set_xscale("log")
        self.ax_sweep_prx.set_xlabel("Distance (km, log scale)", fontsize=9, fontweight="bold")
        self.ax_sweep_prx.set_ylabel("Received Power (dBm)", fontsize=9, fontweight="bold")
        self.ax_sweep_prx.set_title("Received Power vs. Distance", fontsize=10, fontweight="bold")
        self.ax_sweep_prx.grid(True, which="both", ls="--", alpha=0.4)
        self.ax_sweep_prx.legend(loc="best", fontsize=7.5)
        self.ax_sweep_prx.tick_params(labelsize=8)

        # Subplot 2: SNR & Channel Capacity vs Distance
        self.ax_sweep_snr.plot(dists, snrs, color="#8e44ad", linewidth=2.0, label="SNR (dB)")
        self.ax_sweep_snr.set_xscale("log")
        self.ax_sweep_snr.set_xlabel("Distance (km, log scale)", fontsize=9, fontweight="bold")
        self.ax_sweep_snr.set_ylabel("SNR (dB)", fontsize=9, fontweight="bold", color="#8e44ad")
        self.ax_sweep_snr.tick_params(axis="y", labelcolor="#8e44ad", labelsize=8)
        self.ax_sweep_snr.grid(True, which="both", ls="--", alpha=0.4)

        # Secondary y-axis for capacity
        ax_cap = self.ax_sweep_snr.twinx()
        ax_cap.plot(dists, caps, color="#16a085", linewidth=2.0, linestyle="--", label="Capacity (Mbps)")
        ax_cap.set_ylabel("Shannon Capacity (Mbps)", fontsize=9, fontweight="bold", color="#16a085")
        ax_cap.tick_params(axis="y", labelcolor="#16a085", labelsize=8)
        self.ax_sweep_snr.set_title("SNR & Shannon Capacity vs. Distance", fontsize=10, fontweight="bold")

        self.fig_sweep.tight_layout()
        self.canvas_sweep.draw()

    def _update_all_charts(self):
        self._draw_waterfall_chart()
        self._update_sweep_plot()
        self._update_comparison_ui()

    def _add_current_to_comparison(self):
        """Add current configuration to comparison list."""
        if len(self.comparison_scenarios) >= 5:
            messagebox.showinfo("Comparison Limit", "Maximum 5 scenarios can be compared at once.")
            return

        p = self._read_current_params()
        r = calculate_link_budget(p)
        self.comparison_scenarios.append((p, r))
        self._update_comparison_ui()
        messagebox.showinfo("Added", f"Added '{p.scenario_name}' to comparison list.")

    def _load_all_presets_for_comparison(self):
        """Preload 4 distinct presets into comparison."""
        selected_keys = [
            "Wi-Fi 6 (802.11ax) 2.4 GHz",
            "4G LTE Cellular Base Station (1800 MHz)",
            "5G NR mmWave Urban Small Cell (28 GHz)",
            "LoRaWAN Long-Range IoT (868 MHz)"
        ]
        self.comparison_scenarios = []
        for k in selected_keys:
            p = PRESET_SCENARIOS[k]
            r = calculate_link_budget(p)
            self.comparison_scenarios.append((p, r))
        self._update_comparison_ui()

    def _clear_comparison(self):
        self.comparison_scenarios = []
        self._update_comparison_ui()

    def _update_comparison_ui(self):
        """Refresh comparison treeview table and grouped bar chart."""
        # Clear table
        for item in self.comp_tree.get_children():
            self.comp_tree.delete(item)

        scenarios = self.comparison_scenarios
        if not scenarios:
            self.ax_comp.clear()
            self.ax_comp.text(0.5, 0.5, "No scenarios in comparison list.\nClick 'Load All Standard Presets' or 'Add to Comparison'.",
                              ha="center", va="center", transform=self.ax_comp.transAxes)
            self.canvas_comp.draw()
            return

        # Configure columns
        headers = ["Metric"] + [f"{p.scenario_name[:20]}" for p, _ in scenarios]
        while len(headers) < 5:
            headers.append(f"Scenario {len(headers)}")
        self.comp_tree["columns"] = tuple(headers)
        for h in headers:
            self.comp_tree.heading(h, text=h)

        rows = [
            ("Carrier Frequency", lambda p, r: f"{p.frequency_mhz:.1f} MHz"),
            ("Link Distance", lambda p, r: f"{p.distance_km:.3f} km"),
            ("Propagation Model", lambda p, r: p.path_loss_model.split("(")[0]),
            ("Tx Power", lambda p, r: f"{p.tx_power_dbm:.1f} dBm"),
            ("EIRP", lambda p, r: f"{r.eirp_dbm:.2f} dBm"),
            ("Total Path Loss", lambda p, r: f"{r.total_path_loss_db:.2f} dB"),
            ("Received Power (Prx)", lambda p, r: f"{r.rx_power_dbm:.2f} dBm"),
            ("Rx Sensitivity", lambda p, r: f"{p.rx_sensitivity_dbm:.1f} dBm"),
            ("Link Margin", lambda p, r: f"{r.link_margin_db:+.2f} dB"),
            ("Viability Status", lambda p, r: "✔ PASS" if r.is_link_viable else "✖ FAIL"),
            ("Noise Floor", lambda p, r: f"{r.receiver_noise_floor_dbm:.2f} dBm"),
            ("SNR", lambda p, r: f"{r.snr_db:.2f} dB"),
            ("Max Achievable Dist", lambda p, r: f"{r.max_achievable_distance_km:.2f} km"),
            ("Shannon Capacity", lambda p, r: f"{r.shannon_capacity_mbps:.1f} Mbps"),
        ]

        for label, extractor in rows:
            vals = [label] + [extractor(p, r) for p, r in scenarios]
            self.comp_tree.insert("", tk.END, values=vals)

        # Plot Comparative Bar Chart
        self.ax_comp.clear()
        names = [p.scenario_name[:16] + ".." for p, _ in scenarios]
        margins = [r.link_margin_db for p, r in scenarios]
        prx_vals = [r.rx_power_dbm for p, r in scenarios]

        x = range(len(names))
        width = 0.35

        self.ax_comp.bar([i - width/2 for i in x], margins, width=width, label="Link Margin (dB)", color="#27ae60")
        self.ax_comp.bar([i + width/2 for i in x], prx_vals, width=width, label="Received Power (dBm)", color="#2980b9")

        self.ax_comp.set_xticks(x)
        self.ax_comp.set_xticklabels(names, fontsize=8, rotation=15)
        self.ax_comp.set_ylabel("Power / Margin (dB / dBm)", fontsize=9, fontweight="bold")
        self.ax_comp.set_title("Multi-Scenario Comparison: Link Margin vs. Received Power", fontsize=10, fontweight="bold")
        self.ax_comp.grid(axis="y", linestyle="--", alpha=0.4)
        self.ax_comp.legend(loc="upper right", fontsize=8)
        self.fig_comp.tight_layout()
        self.canvas_comp.draw()

    # --- Export Handlers ---
    def _export_pdf(self):
        """Export high-grade PDF report."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            initialfile=f"LinkBudget_{self.current_params.scenario_name[:12].replace(' ', '_')}.pdf"
        )
        if not filepath:
            return

        temp_chart = os.path.abspath("temp_report_chart.png")
        self.fig_waterfall.savefig(temp_chart, dpi=150)

        try:
            generate_pdf_report(self.current_params, self.current_results, filepath, chart_image_path=temp_chart)
            if os.path.exists(temp_chart):
                os.remove(temp_chart)
            messagebox.showinfo("Export Successful", f"PDF report successfully saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not create PDF report:\n{e}")

    def _export_csv(self):
        """Export calculation results and sweep data to CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv")],
            initialfile=f"LinkBudget_{self.current_params.scenario_name[:12].replace(' ', '_')}.csv"
        )
        if not filepath:
            return

        try:
            dists, rx_powers, snrs, caps = sweep_distance(
                self.current_params,
                float(self.var_sweep_min.get()),
                float(self.var_sweep_max.get()),
                int(self.var_sweep_points.get())
            )
            export_link_budget_csv(
                self.current_params,
                self.current_results,
                filepath,
                sweep_data=(dists, rx_powers, snrs, caps)
            )
            messagebox.showinfo("Export Successful", f"CSV file successfully saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not create CSV file:\n{e}")

    def _export_comparison_csv(self):
        """Export multi-scenario comparison to CSV."""
        if not self.comparison_scenarios:
            messagebox.showinfo("No Data", "No scenarios to export. Load or add scenarios first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv")],
            initialfile="LinkBudget_Comparison.csv"
        )
        if not filepath:
            return

        try:
            export_scenario_comparison_csv(self.comparison_scenarios, filepath)
            messagebox.showinfo("Export Successful", f"Comparison CSV saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export comparison CSV:\n{e}")

    def _export_chart_png(self):
        """Save the active waterfall chart as a high-resolution PNG image."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile="link_budget_waterfall.png"
        )
        if not filepath:
            return

        try:
            self.fig_waterfall.savefig(filepath, dpi=200, bbox_inches="tight")
            messagebox.showinfo("Image Saved", f"Chart image saved successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save chart:\n{e}")


def launch_gui():
    """Application launcher."""
    if HAS_TTKBOOTSTRAP:
        root = tb.Window(title="Wireless Link Budget GUI", themename="darkly")
    else:
        root = tk.Tk()
    
    app = WirelessLinkBudgetApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
