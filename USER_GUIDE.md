# First-Time User Guide: Wireless Link Budget GUI

> **Course:** 3171608 – Wireless Communication (WC)  
> **Topic:** Micro-Project 8 – Wireless Link Budget GUI  
> **Target Audience:** Students, lab evaluators, and first-time users  

Welcome! This step-by-step guide will walk you through setting up, launching, and using the **Wireless Link Budget GUI** application from scratch. No prior RF simulation experience is required.

---

## 📑 Table of Contents
1. [Prerequisites & System Requirements](#1-prerequisites--system-requirements)
2. [Step-by-Step Installation](#2-step-by-step-installation)
3. [How to Launch the Application](#3-how-to-launch-the-application)
4. [First-Time Walkthrough: Step-by-Step Tutorial](#4-first-time-walkthrough-step-by-step-tutorial)
   - [Tutorial 1: Loading a Preset Link Budget](#tutorial-1-loading-a-preset-link-budget)
   - [Tutorial 2: Customizing Parameters & Re-calculating](#tutorial-2-customizing-parameters--re-calculating)
   - [Tutorial 3: Understanding the Results & Waterfall Chart](#tutorial-3-understanding-the-results--the-waterfall-chart)
   - [Tutorial 4: Exporting a Professional PDF Report](#tutorial-4-exporting-a-professional-pdf-report)
   - [Tutorial 5: Performing Distance & Capacity Sweeps](#tutorial-5-performing-distance--capacity-sweeps)
   - [Tutorial 6: Comparing Multiple Technologies Side-by-Side](#tutorial-6-comparing-multiple-technologies-side-by-side)
   - [Tutorial 7: Changing Themes (Dark Mode & Light Mode)](#tutorial-7-changing-themes-dark-mode--light-mode)
5. [Understanding Key RF Terminology (Quick Cheat-Sheet)](#5-understanding-key-rf-terminology-quick-cheat-sheet)
6. [Troubleshooting & Frequently Asked Questions (FAQ)](#6-troubleshooting--frequently-asked-questions-faq)

---

## 1. Prerequisites & System Requirements

Before running the application, make sure your computer has:
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** Version **3.10** or newer (Python 3.10, 3.11, 3.12, 3.13, or 3.14).
- **Terminal:** Windows PowerShell, Command Prompt (CMD), or Terminal.

### Verify Python Installation
Open PowerShell or Terminal and run:
```powershell
python --version
```
*Expected Output:* `Python 3.10.x` (or newer).  
*(If `python` is not recognized, see the [Troubleshooting](#6-troubleshooting--frequently-asked-questions-faq) section).*

---

## 2. Step-by-Step Installation

### Step 2.1: Open PowerShell in the Project Directory
Navigate to the project folder where the application files are located:
```powershell
cd "e:\1_B.E. in IT\7th Semester\3171608_Wireless Communication (WC)\WC_Micro-Project_Wireless-Link-Budget-GUI"
```

### Step 2.2: (Optional but Recommended) Create a Virtual Environment
A virtual environment ensures that the project packages don't interfere with other software:
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1

# (If using Command Prompt CMD):
# .\venv\Scripts\activate.bat
```

### Step 2.3: Install Required Libraries
Install all required RF calculation, GUI, and reporting packages with a single command:
```powershell
pip install -r requirements.txt
```
This automatically installs:
- `ttkbootstrap` (Modern UI styling and themes)
- `matplotlib` (Embedded RF charts and curves)
- `reportlab` (Automated PDF report generator)
- `numpy` & `pandas` (Numerical modeling and data export)
- `pillow` (Image handling)

---

## 3. How to Launch the Application

Once dependencies are installed, launch the application using:

```powershell
python main.py
```

*(You can also run `python gui_app.py` directly).*

The application window will open automatically in a sleek, modern **Dark Mode** (`darkly` theme) with the **Wi-Fi 6 (2.4 GHz)** link budget pre-loaded and ready for exploration.

---

## 4. First-Time Walkthrough: Step-by-Step Tutorial

### Tutorial 1: Loading a Preset Link Budget
The application comes pre-loaded with **8 realistic industry-standard scenarios**.

1. Look at the top right of the application header for the **"Scenario Preset:"** dropdown.
2. Click the dropdown to view available links:
   - `Wi-Fi 6 (802.11ax) 2.4 GHz` (Indoor campus coverage)
   - `Wi-Fi 6 (802.11ax) 5 GHz` (High-speed 80 MHz channel)
   - `4G LTE Cellular Base Station (1800 MHz)` (Urban macro tower to mobile)
   - `5G NR mmWave Urban Small Cell (28 GHz)` (Phased array micro-cell)
   - `Satellite Ku-band Downlink (GEO 36,000 km)` (TV/Data satellite dish)
   - `Satellite LEO Starlink-style Downlink (550 km)` (Low Earth Orbit link)
   - `LoRaWAN Long-Range IoT (868 MHz)` (Sub-GHz long range sensor)
   - `Microwave Point-to-Point Backhaul (18 GHz)` (Tower-to-tower link)
3. Select any scenario (e.g., **"4G LTE Cellular Base Station (1800 MHz)"**).
4. Notice how **all input parameters instantly update**, the calculations refresh, the KPI cards update, and the **Waterfall Chart** re-draws in real-time!

---

### Tutorial 2: Customizing Parameters & Re-calculating
Want to see what happens when you move further away, increase transmit power, or switch propagation models?

1. On the left side of the window, you will find 4 organized parameter sections:
   - **Transmitter (Tx):** Change **Tx Power (dBm)**, **Tx Antenna Gain (dBi)**, or **Antenna Height (m)**.
   - **Channel & Propagation:** Change **Carrier Frequency (MHz)** or **Link Distance (km)**.
   - **Propagation Model Dropdown:** Try switching between:
     - `Free Space Path Loss (FSPL)`
     - `Two-Ray Ground Reflection Model`
     - `Log-Distance Model`
     - `Okumura-Hata Model`
     - `COST-231 Hata Model`
   - **Environmental Losses:** Add **Rain Attenuation (dB)** or **Obstacle Loss (dB)** (e.g., enter `15 dB` for concrete building penetration).
   - **Receiver (Rx):** Adjust **Rx Sensitivity (dBm)**, **Noise Figure (dB)**, or **Bandwidth (MHz)**.
2. Click the blue **"⚡ Recalculate"** button (or press the top **"⚡ Compute Link Budget"** button).
3. Observe how the **Link Margin**, **Received Power**, and **Status Badge** update immediately.

---

### Tutorial 3: Understanding the Results & the Waterfall Chart

#### A. Reading the Status Banner
- **`✔ PASS — EXCELLENT LINK (Margin >= 10 dB)`**: Signal is strong and has enough safety buffer to survive rain, fading, and moving obstacles.
- **`✔ PASS — VIABLE / MARGINAL (0 <= Margin < 10 dB)`**: Signal arrives above sensitivity, but is vulnerable to atmospheric variations.
- **`✖ FAIL — LINK DOWN / FAILED (Margin Deficit: X dB)`**: Insufficient received power; the receiver cannot decode the signal.

#### B. Reading the KPI Metric Cards
- **LINK MARGIN:** Received Power minus Sensitivity threshold. Positive is good, negative means no signal.
- **RECEIVED POWER ($P_{rx}$):** Signal power entering the receiver front-end (displayed in both `dBm` and picowatts `pW`).
- **EIRP:** Total radiated power from the antenna ($P_{tx} + G_{tx} - L_{tx}$).
- **TOTAL PATH LOSS:** Signal attenuation caused by distance, obstacles, and atmosphere.
- **SNR (SIGNAL-TO-NOISE RATIO):** Received Power minus the Thermal Noise Floor.
- **MAX COVERAGE RANGE ($d_{max}$):** The maximum physical distance before the signal drops below sensitivity.
- **SHANNON CAPACITY:** Theoretical maximum data rate in Mbps ($C = B\log_2(1+\text{SNR})$).

#### C. Reading the Waterfall Bar Chart
The bar chart on the right visually tracks power level evolution stage-by-stage:
1. **Tx Power (dBm)** $\to$
2. **After Cable Loss** (drops slightly) $\to$
3. **EIRP** (jumps up by antenna gain) $\to$
4. **After Path Loss** (drops significantly across distance) $\to$
5. **After Environmental Losses** (drops due to rain/walls) $\to$
6. **Rx Antenna Gain** (boosted by receiver dish/antenna) $\to$
7. **Rx Power (Input)** (final level at the demodulator).
- **Red Dashed Line:** Receiver Sensitivity threshold. The final bar **must be above this line** for the link to pass!
- **Dotted Line:** Thermal Noise Floor.

---

### Tutorial 4: Exporting a Professional PDF Report
The application can generate comprehensive engineering-grade PDF documentation formatted for academic submissions:

1. In **Tab 1**, locate the export toolbar below the Waterfall chart.
2. Click **"📄 Export PDF Report"**.
3. Choose where to save the file (e.g., your Desktop or project folder) and click **Save**.
4. Open the generated PDF to see:
   - Formal header with Course Code (3171608) and project title.
   - Colored Executive Pass/Fail status banner.
   - Formatted performance summary grid.
   - Comprehensive input parameter breakdown table.
   - Numerical stage-by-stage power accounting table.
   - Embedded high-resolution waterfall chart image.
   - Mathematical equations reference block.

*Note: You can also click **"📊 Export CSV Data"** to save spreadsheet data, or **"🖼 Save Plot (PNG)"** to save the chart image.*

---

### Tutorial 5: Performing Distance & Capacity Sweeps

Want to see how signal power and data throughput drop as you walk further away from a transmitter?

1. Click on **Tab 2: "📈 Parametric Sweeps & Capacity"** at the top.
2. In the top bar, set:
   - **Min (km):** `0.1` (100 meters)
   - **Max (km):** `10.0` (10 km)
   - **Points:** `100`
3. Click **"🔄 Run Distance Sweep"**.
4. Examine the two side-by-side graphs:
   - **Left Graph (Received Power vs Distance):** Shows the logarithmic decline of $P_{rx}$. Notice the red dashed sensitivity line and green vertical dash-dot line marking the **Maximum Coverage Distance ($d_{max}$)**!
   - **Right Graph (SNR & Shannon Capacity vs Distance):** Shows both SNR in dB (purple curve) and maximum data rate in Mbps (green dashed curve).
5. Use the Matplotlib toolbar at the bottom to zoom into any section or pan along the curves.

---

### Tutorial 6: Comparing Multiple Technologies Side-by-Side

Compare Wi-Fi, 4G LTE, 5G mmWave, and LoRaWAN IoT on a single screen:

1. Click on **Tab 3: "⚖ Scenario Comparator"** at the top.
2. Click the **"Load All Standard Presets"** button.
3. Observe:
   - **Top Comparison Matrix Table:** A side-by-side table displaying Carrier Frequency, Link Distance, Propagation Model, EIRP, Total Path Loss, Received Power, Margin, and Status for all loaded links.
   - **Bottom Grouped Bar Chart:** Visually compares **Link Margin (dB)** (green bars) and **Received Power (dBm)** (blue bars) across technologies.
4. Click **"Export Comparison CSV"** to save the comparison table into an Excel-ready `.csv` file.

---

### Tutorial 7: Changing Themes (Dark Mode & Light Mode)

Prefer a light theme for reading or printing?
1. In the top-right header, find the **"Theme:"** dropdown.
2. Select any theme:
   - **Dark Themes:** `darkly` (default), `superhero`, `cyborg`
   - **Light Themes:** `flatly`, `cosmo`, `litera`
3. The application window, buttons, fonts, and charts will dynamically adapt to your selected theme!

---

## 5. Understanding Key RF Terminology (Quick Cheat-Sheet)

| Term | Unit | Plain English Meaning |
|---|---|---|
| **$P_{tx}$ (Tx Power)** | dBm / Watts | The raw power produced by the transmitter amplifier. $0\text{ dBm} = 1\text{ mW}$, $30\text{ dBm} = 1\text{ Watt}$. |
| **$G_{tx}$ / $G_{rx}$ (Gain)** | dBi | Antenna amplification achieved by focusing energy in a specific direction compared to an omnidirectional sphere. |
| **EIRP** | dBm | Total radiated power: $P_{tx} + G_{tx} - L_{tx}$. |
| **$f$ (Frequency)** | MHz / GHz | Carrier wave frequency. Higher frequencies (e.g. 5G 28 GHz) suffer more atmospheric and obstacle attenuation than lower frequencies (e.g. 868 MHz). |
| **$d$ (Distance)** | km / meters | Physical separation between transmitting and receiving antennas. |
| **FSPL** | dB | Free Space Path Loss: Attenuation due to spherical wavefront spreading through space. |
| **$P_{rx}$ (Received Power)**| dBm | Net power arriving at the receiver antenna terminals after all losses and gains. |
| **Sensitivity ($P_{rx,sens}$)**| dBm | Minimum power level required by the receiver hardware to detect and decode bits without errors (e.g. $-90\text{ dBm}$). |
| **Link Margin** | dB | Safety buffer ($P_{rx} - P_{rx,sens}$). Must be $> 0\text{ dB}$ for the link to function. |
| **Noise Floor ($N$)** | dBm | Background thermal noise created by atomic vibrations in electronic components: $N = -174 + 10\log_{10}(B) + NF$. |
| **SNR** | dB | Signal-to-Noise Ratio ($P_{rx} - N$). Higher SNR enables higher-order modulation (e.g. 64-QAM, 256-QAM). |
| **Shannon Capacity ($C$)** | Mbps | Theoretical maximum error-free throughput achievable across channel bandwidth $B$. |

---

## 6. Troubleshooting & Frequently Asked Questions (FAQ)

### Q1: `python` is not recognized as an internal or external command.
**Solution:** Python is not added to your Windows PATH environment variable.
1. Download Python from [python.org](https://www.python.org/downloads/).
2. During installation, make sure to check the box: **"Add Python to PATH"**.
3. Alternatively, in PowerShell try typing `py main.py`.

### Q2: I get `ModuleNotFoundError: No module named 'ttkbootstrap'`.
**Solution:** The required libraries have not been installed yet. Run:
```powershell
pip install -r requirements.txt
```

### Q3: How do I generate the official Micro-Project Report PDF?
**Solution:** Run the dedicated report generator:
```powershell
python generate_project_report_pdf.py
```
This generates the complete 9-page academic project report: [**`WC_Micro_Project_Wireless_Link_Budget_Report.pdf`**](WC_Micro_Project_Wireless_Link_Budget_Report.pdf) with cover page, certificate, theory, embedded figures, comparison tables, and bibliography.

### Q4: How do I test the application without opening the GUI?
**Solution:** Run the automated headless test suite:
```powershell
python test_engine.py
```
To generate sample scenario PDF reports and charts headlessly:
```powershell
python generate_sample_outputs.py
```

### Q5: Where are exported PDF reports and CSV files saved?
**Solution:** When you click "Export PDF Report" or "Export CSV Data", a Windows file dialog will ask you where you wish to save the file. Pre-generated reports and sample outputs are located in the project root and [`sample_outputs/`](sample_outputs/) folder.

### Q6: Can I add my own custom scenario?
**Solution:** Yes! Simply modify the values in Tab 1 to match your system, click **"➕ Add to Comparison"**, and it will be stored in Tab 3 alongside the standard presets for comparative analysis.

---

## 👨‍💻 Need Help or Preparing for Viva?
Check **Tab 4: "📖 WC Theory & Formulas Reference"** inside the application or read the full [**`README.md`**](README.md) for theory derivations and standard Viva Voce questions & answers!
