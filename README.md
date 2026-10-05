# Wireless Link Budget GUI Application

> **Course:** 3171608 – Wireless Communication (WC)  
> **Degree:** Bachelor of Engineering (B.E.) in Information Technology (7th Semester)  
> **Project Title:** Project 8: Wireless Link Budget GUI  
> **Recommended Tools:** Python 3.10+, Tkinter / ttkbootstrap, Matplotlib, ReportLab, NumPy  

> [!TIP]
> **First-Time User?** Check out the step-by-step walkthrough in [**`USER_GUIDE.md`**](USER_GUIDE.md) for quick setup, tutorials, and beginner tips!

---

## 📋 Table of Contents
1. [Project Overview & Objectives](#-project-overview--objectives)
2. [Key Features & Capabilities](#-key-features--capabilities)
3. [Theoretical Background & Mathematical Formulas](#-theoretical-background--mathematical-formulas)
4. [Software Architecture & Module Design](#-software-architecture--module-design)
5. [Industry Presets & Scenarios](#-industry-presets--scenarios)
6. [Installation & Setup](#-installation--setup)
7. [How to Run the Application](#-how-to-run-the-application)
8. [Module-by-Module Walkthrough](#-module-by-module-walkthrough)
9. [Sample Outputs & Deliverables](#-sample-outputs--deliverables)
10. [Unit Testing & Verification](#-unit-testing--verification)
11. [Viva Voce / Oral Examination Preparation](#-viva-voce--oral-examination-preparation)

---

## 🎯 Project Overview & Objectives

In wireless telecommunications, a **Link Budget** accounts for all the power gains and losses that a radio frequency (RF) signal experiences as it travels from a transmitter through a medium (free space, atmosphere, physical obstacles) to the receiver. Calculating the link budget ensures that the receiver captures a signal with sufficient strength and quality (Signal-to-Noise Ratio, SNR) above its sensitivity threshold and thermal noise floor to achieve reliable demodulation and error-free transmission.

### Primary Objectives:
- **Core RF Concepts Implementation:** Model the physical layers of modern wireless links (Wi-Fi, 4G/5G Cellular, Satellite, LoRaWAN IoT, and Microwave Backhaul).
- **Interactive Graphical Interface:** Provide an intuitive, modern, dark/light-themed GUI for real-time parameter configuration, live calculation, and interactive visual feedback.
- **Propagation Model Versatility:** Support Free Space Path Loss (FSPL), Two-Ray Ground Reflection, Log-Distance Shadowing, Okumura-Hata, and COST-231 Hata models.
- **Parametric Sweeps & Capacity Analysis:** Analyze Received Power, SNR, and Shannon-Hartley channel capacity across varying link distances.
- **Multi-Scenario Comparison:** Compare different frequency bands, propagation environments, and technologies side-by-side.
- **Engineering-Grade Reporting:** Export automated IEEE-style PDF reports, CSV datasets, and high-resolution chart images.

---

## ✨ Key Features & Capabilities

- **Interactive Parameter Input Forms:**
  - **Transmitter (Tx):** Power output (dBm/Watts), antenna gain (dBi), feeder/cable losses (dB), and tower height ($h_b$).
  - **Channel / Propagation:** Carrier frequency (MHz/GHz), distance (m/km), choice of 5 path loss models, path loss exponent ($n$), and receiver height ($h_m$).
  - **Environmental & Extra Losses:** Rain attenuation, atmospheric absorption, building/wall penetration loss, polarization mismatch, and fade margin allocation.
  - **Receiver (Rx):** Antenna gain (dBi), front-end filter/cable loss, sensitivity threshold ($P_{rx,sens}$), noise figure ($NF$), channel bandwidth ($B$), and noise temperature ($T$).
- **Live Performance Badges & KPI Cards:**
  - Real-time display of **Link Margin (dB)**, **Received Power ($P_{rx}$)**, **EIRP**, **Total Path Loss**, **SNR**, **Noise Floor**, **Maximum Achievable Distance ($d_{max}$)**, and **Shannon Capacity (Mbps)**.
  - Visual status banner: `✔ PASS (EXCELLENT)` vs `✖ FAIL (MARGIN DEFICIT)`.
- **Dynamic Visualizations (Embedded Matplotlib):**
  - **Waterfall Power Accounting Chart:** Step-by-step bar chart illustrating cumulative power levels from Tx power $\to$ EIRP $\to$ Path Loss $\to$ Environmental Loss $\to$ Rx antenna $\to$ Demodulator input, alongside Rx Sensitivity and Noise Floor threshold lines.
  - **Received Power vs. Distance Plot:** Logarithmic distance sweep showing power decay with marker for maximum coverage range ($d_{max}$).
  - **SNR & Shannon Capacity Sweep:** Dual-axis curve illustrating how spectral efficiency and achievable throughput diminish with distance.
  - **Scenario Comparison Bar Chart:** Direct comparison of margins and received power across configurations.
- **Reporting & Exporting:**
  - One-click **PDF Report Export** with formatted tables, badges, and high-resolution chart image.
  - One-click **CSV Data Export** for spreadsheets and external simulation tools.
  - High-resolution **PNG Chart Export**.

---

## 📐 Theoretical Background & Mathematical Formulas

### 1. Transmitter EIRP (Effective Isotropic Radiated Power)
EIRP represents the total power that a theoretical isotropic antenna would emit to produce the peak power density observed in the direction of maximum antenna gain:
$$\text{EIRP (dBm)} = P_{tx} \text{ (dBm)} + G_{tx} \text{ (dBi)} - L_{tx} \text{ (dB)}$$
$$\text{EIRP (Watts)} = 10^{\frac{\text{EIRP (dBm)} - 30}{10}}$$

### 2. Propagation Path Loss Models
Let $d$ be distance in kilometers, $f$ be carrier frequency in MHz, and $c = 3 \times 10^8\text{ m/s}$.

#### A. Free Space Path Loss (FSPL) - Friis Transmission Law
Ideal line-of-sight (LOS) propagation through vacuum/air:
$$\text{FSPL (dB)} = 32.44 + 20\log_{10}(d_{\text{km}}) + 20\log_{10}(f_{\text{MHz}})$$

#### B. Two-Ray Ground Reflection Model
Considers direct LOS ray plus ground-reflected ray. Beyond the crossover distance $d_{\text{cross}} = \frac{4\pi h_{tx} h_{rx}}{\lambda}$, power falls off at $40\text{ dB/decade}$:
$$\text{PL}_{\text{2ray}}\text{ (dB)} = 40\log_{10}(d) - 20\log_{10}(h_{tx}) - 20\log_{10}(h_{rx})$$

#### C. Log-Distance Path Loss Model
Accounts for cluttered indoor and outdoor environments where path loss follows a power law:
$$\text{PL}(d)\text{ (dB)} = \text{PL}(d_0) + 10\,n\log_{10}\left(\frac{d}{d_0}\right) + X_\sigma$$
Where $n$ is the path loss exponent ($n \approx 2.0$ for free space, $2.7 - 3.5$ for urban macro, $3.0 - 5.0$ for shadowed indoor buildings) and $X_\sigma$ is log-normal shadowing margin.

#### D. Okumura-Hata Model (150 MHz – 1500 MHz Cellular)
Standard empirical model for cellular base stations ($h_b = 30-200\text{ m}$, $h_m = 1-10\text{ m}$, $d = 1-20\text{ km}$):
$$\text{PL}_{\text{urban}} = 69.55 + 26.16\log_{10}(f) - 13.82\log_{10}(h_b) - a(h_m) + [44.9 - 6.55\log_{10}(h_b)]\log_{10}(d)$$
Mobile antenna correction factor:
$$a(h_m) = (1.1\log_{10}(f) - 0.7)h_m - (1.56\log_{10}(f) - 0.8)$$
Suburban correction:
$$\text{PL}_{\text{suburban}} = \text{PL}_{\text{urban}} - 2\left[\log_{10}\left(\frac{f}{28}\right)\right]^2 - 5.4$$
Open / Rural correction:
$$\text{PL}_{\text{rural}} = \text{PL}_{\text{urban}} - 4.78(\log_{10}(f))^2 + 18.33\log_{10}(f) - 40.94$$

#### E. COST-231 Hata Model (1500 MHz – 2000 MHz PCS)
Extends Hata to 2 GHz personal communications:
$$\text{PL}_{\text{cost}} = 46.3 + 33.9\log_{10}(f) - 13.82\log_{10}(h_b) - a(h_m) + [44.9 - 6.55\log_{10}(h_b)]\log_{10}(d) + C_m$$
Where $C_m = 0\text{ dB}$ for medium city/suburban, and $3\text{ dB}$ for dense metropolitan centers.

### 3. Received Power ($P_{rx}$)
$$P_{rx}\text{ (dBm)} = \text{EIRP} - \text{PL}_{\text{model}} - L_{\text{env}} + G_{rx} - L_{rx}$$
Where:
$$L_{\text{env}} = L_{\text{rain}} + L_{\text{atm}} + L_{\text{obstacle}} + L_{\text{polarization}} + L_{\text{fade}}$$
Linear power in Watts:
$$P_{rx}\text{ (Watts)} = 10^{\frac{P_{rx}\text{ (dBm)} - 30}{10}}$$

### 4. Thermal Noise Floor & Noise Figure
Thermal noise generated in the receiver front-end (Johnson-Nyquist noise):
$$N = k \cdot T \cdot B \quad \text{(Watts)}$$
In dBm:
$$N\text{ (dBm)} = -174\text{ dBm/Hz} + 10\log_{10}(B_{\text{Hz}}) + NF\text{ (dB)}$$
Where $k = 1.380649 \times 10^{-23}\text{ J/K}$, $T = 290\text{ K}$, $B$ is channel bandwidth in Hz, and $NF$ is the receiver noise figure.

### 5. Signal-to-Noise Ratio (SNR) & Link Margin
$$\text{SNR (dB)} = P_{rx}\text{ (dBm)} - N\text{ (dBm)}$$
$$\text{Link Margin (dB)} = P_{rx}\text{ (dBm)} - P_{rx,\text{sens}}\text{ (dBm)}$$
- $\text{Margin} \ge 10\text{ dB}$: **EXCELLENT** link; withstands severe fading and atmospheric fluctuations.
- $0\text{ dB} \le \text{Margin} < 10\text{ dB}$: **MARGINAL / VIABLE** link.
- $\text{Margin} < 0\text{ dB}$: **LINK FAILED**; received power is insufficient for demodulation.

### 6. Shannon-Hartley Channel Capacity
The theoretical maximum error-free information rate through an AWGN channel:
$$C = B \cdot \log_2(1 + \text{SNR}_{\text{linear}}) \quad \text{(bps)}$$
Where $\text{SNR}_{\text{linear}} = 10^{\frac{\text{SNR (dB)}}{10}}$.

### 7. Maximum Achievable Coverage Distance ($d_{max}$)
Computed by numerically inverting the propagation model at the boundary condition where $\text{Link Margin} = 0\text{ dB}$ (i.e., $P_{rx} = P_{rx,\text{sens}}$).

---

## 🏗 Software Architecture & Module Design

```
WC_Micro-Project_Wireless-Link-Budget-GUI/
│
├── main.py                     # Primary launcher: DPI awareness, dependency validation, GUI start
├── gui_app.py                  # Full desktop application GUI (ttkbootstrap, tabs, widgets, plots)
├── link_budget_engine.py       # Core mathematical RF models, unit conversions, solver & presets
├── report_generator.py         # IEEE-style PDF reports (ReportLab) & CSV export modules
├── test_engine.py              # Automated unit test suite verifying RF formulas and edge cases
├── generate_sample_outputs.py  # Headless generator producing sample charts, CSVs, and PDF reports
├── generate_dashboard_preview.py # Generator for composite GUI visual preview dashboard
├── requirements.txt            # Python dependencies specification
│
├── sample_outputs/             # Generated evaluation deliverables
│   ├── gui_dashboard_preview.png        # Complete application dashboard preview
│   ├── sample_power_budget_waterfall.png# Stage-by-stage waterfall chart
│   ├── sample_prx_vs_distance.png       # Received power vs distance curve
│   ├── sample_snr_vs_distance.png       # SNR & Shannon capacity sweep curves
│   ├── sample_wifi_report.pdf           # Generated PDF report for Wi-Fi 6
│   ├── sample_cellular_lte_report.pdf   # Generated PDF report for 4G LTE
│   ├── sample_satellite_report.pdf      # Generated PDF report for GEO Satellite
│   ├── sample_lte_link_budget.csv       # Exported CSV with parameters & distance sweep
│   └── link_budget_comparison.csv       # Multi-scenario comparison matrix
│
└── README.md                   # Comprehensive project documentation
```

---

## 📡 Industry Presets & Scenarios

The system includes preconfigured, realistic link budgets matching industry standards:

| Preset Scenario | Frequency | Distance | Model | Tx Power | Rx Sens | Description |
|---|---|---|---|---|---|---|
| **Wi-Fi 6 (802.11ax) 2.4 GHz** | 2437 MHz | 80 m | Log-Distance ($n=3.0$) | 20 dBm (100 mW) | -82 dBm | Indoor campus/office coverage with partition wall losses |
| **Wi-Fi 6 (802.11ax) 5 GHz** | 5180 MHz | 50 m | Log-Distance ($n=3.2$) | 23 dBm (200 mW) | -75 dBm | 80 MHz high-throughput WLAN link |
| **4G LTE Urban Macro Cell** | 1800 MHz | 2.0 km | COST-231 Hata | 43 dBm (20 W) | -100 dBm | Downlink from 35m tower to handheld smartphone |
| **5G NR mmWave Small Cell** | 28 GHz | 300 m | FSPL | 30 dBm (1 W) | -86 dBm | 400 MHz bandwidth beamforming micro-cell |
| **GEO Satellite Ku-band** | 12 GHz | 36,000 km | FSPL | 50 dBm (100 W) | -115 dBm | Geostationary transponder downlink to 90cm dish |
| **LEO Satellite (Starlink-style)**| 12.5 GHz | 750 km | FSPL | 40 dBm (10 W) | -105 dBm | Low Earth Orbit constellation to phased-array user terminal |
| **LoRaWAN IoT Sensor Link** | 868 MHz | 5.0 km | Okumura-Hata (Rural) | 14 dBm (25 mW) | -137 dBm | Sub-GHz sensor link with Chirp Spread Spectrum SF12 |
| **18 GHz Microwave Backhaul** | 18 GHz | 10.0 km | FSPL | 24 dBm (250 mW) | -78 dBm | Telecom tower backhaul with 1.2m dish antennas |

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on Windows / Linux / macOS.
- PowerShell or Terminal.

### Step 1: Open PowerShell in Project Directory
```powershell
cd "e:\1_B.E. in IT\7th Semester\3171608_Wireless Communication (WC)\WC_Micro-Project_Wireless-Link-Budget-GUI"
```

### Step 2: Install Required Libraries
```powershell
pip install -r requirements.txt
```

---

## 🚀 How to Run the Application

### Launch the Interactive Desktop GUI:
```powershell
python main.py
```
*(Or alternatively: `python gui_app.py`)*

### Run Automated Headless Sample Deliverable Generator:
```powershell
python generate_sample_outputs.py
```

### Run the RF Mathematical Test Suite:
```powershell
python test_engine.py
```

---

## 🖥 Module-by-Module Walkthrough

### 1. Tab 1: Link Budget Calculator
- **Left Input Panel:** Parameter entry grouped into Transmitter, Channel, Environmental Margins, and Receiver.
- **Top Summary Cards:** Live updates of Link Margin, Received Power, EIRP, Total Path Loss, SNR, Coverage Range, and Capacity.
- **Status Banner:** Immediate visual feedback on link viability.
- **Interactive Waterfall Chart:** Visualizes signal strength evolution from transmitter power stage to receiver input.
- **Export Toolbar:** Direct buttons to export a PDF Report, CSV Data, or PNG Chart.

### 2. Tab 2: Parametric Sweeps & Capacity
- Configurable distance sweep (minimum distance, maximum distance, and point density).
- Dual interactive graphs:
  1. **Received Power vs. Distance** with sensitivity and noise floor threshold lines.
  2. **SNR & Shannon Capacity vs. Distance** showing spectral efficiency degradation.
- Navigation toolbar supporting zoom, pan, and home view.

### 3. Tab 3: Multi-Scenario Comparator
- Compare up to 5 wireless links side-by-side in a comparative matrix table.
- "Load All Standard Presets" button for instant benchmarking of Wi-Fi vs. LTE vs. 5G vs. LoRaWAN.
- Grouped bar chart comparing Link Margin and Received Power across all loaded scenarios.
- One-click export to a comparison CSV file.

### 4. Tab 4: WC Theory & Formulas Reference
- Integrated educational reference containing Friis transmission theory, thermal noise calculations, channel capacity theorem, and practical RF engineering guidelines.

---

## 📊 Sample Outputs & Deliverables

All project documentation, reports, and sample outputs are pre-generated and stored in the project root and `sample_outputs/` directory:

1. **`WC_Micro_Project_Wireless_Link_Budget_Report.pdf`** (or `sample_outputs/WC_Micro_Project_Wireless_Link_Budget_Report.pdf`): **Complete 9-page Official GTU Micro-Project Report PDF**, including formal Cover Page, Certificate of Completion, Abstract, Table of Contents, 6 Technical Chapters, Embedded Figures, Multi-Scenario Comparison Table, and Academic Bibliography.
2. **`sample_outputs/gui_dashboard_preview.png`**: Composite GUI dashboard overview.
3. **`sample_outputs/sample_wifi_report.pdf`**: Formatted single-scenario engineering PDF report for Wi-Fi 6 (2.4 GHz).
4. **`sample_outputs/sample_cellular_lte_report.pdf`**: Formatted single-scenario PDF report for 4G LTE Base Station.
5. **`sample_outputs/sample_satellite_report.pdf`**: Formatted single-scenario PDF report for GEO Satellite Ku-band link.
6. **`sample_outputs/sample_power_budget_waterfall.png`**: High-resolution waterfall chart.
7. **`sample_outputs/sample_prx_vs_distance.png`**: Received power vs distance curve.
8. **`sample_outputs/sample_snr_vs_distance.png`**: SNR & Shannon capacity sweep curve.
9. **`sample_outputs/link_budget_comparison.csv`**: Multi-scenario comparison matrix.
10. **`sample_outputs/sample_lte_link_budget.csv`**: Single-link detailed data and distance sweep points.

---

## 🧪 Unit Testing & Verification

Run the test suite:
```powershell
python test_engine.py
```
Output:
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```
Tests verify:
- Unit conversion integrity (Watts $\leftrightarrow$ dBm).
- Carrier wavelength calculation across RF frequencies.
- Free Space Path Loss exact numerical validation against known textbook benchmarks.
- End-to-end link budget calculation accuracy.
- Sanity and boundary conditions of all 8 industry presets.
- Parametric distance sweep monotonicity (power and SNR decline with distance).
- Binary search solver accuracy for maximum coverage range ($d_{max}$).

---

## 🎓 Viva Voce / Oral Examination Preparation

### Q1: What is a Link Budget and why is it essential in wireless design?
**Ans:** A link budget is the comprehensive accounting of all gains (amplifier gain, antenna gain) and losses (cables, connectors, path loss, rain attenuation, fading) in a telecommunications system. It determines whether the received power at the receiver will exceed the sensitivity threshold and noise floor with an adequate safety margin for reliable communication.

### Q2: What is EIRP and how is it calculated?
**Ans:** EIRP (Effective Isotropic Radiated Power) is the apparent power radiated by an antenna relative to an ideal isotropic antenna that radiates equally in all directions.  
$$\text{EIRP (dBm)} = P_{tx} \text{ (dBm)} + G_{tx} \text{ (dBi)} - L_{tx} \text{ (dB)}$$

### Q3: What is Free Space Path Loss (FSPL) and what is the Friis Equation?
**Ans:** FSPL represents signal attenuation due to spherical spreading of the wavefront through free space. Friis' formula states:
$$\frac{P_{rx}}{P_{tx}} = G_{tx} G_{rx} \left(\frac{\lambda}{4\pi d}\right)^2$$
In dB with $d$ in km and $f$ in MHz:
$$\text{FSPL} = 32.44 + 20\log_{10}(d_{\text{km}}) + 20\log_{10}(f_{\text{MHz}})$$
Every doubling of distance reduces power by $6\text{ dB}$ ($20\text{ dB/decade}$).

### Q4: Why does Two-Ray Ground Reflection exhibit $40\text{ dB/decade}$ loss at far distances?
**Ans:** In the far field ($d \ge d_{\text{cross}}$), the phase difference between the direct line-of-sight ray and the ground-reflected ray becomes very small, causing near-destructive interference. As a result, power falls off inversely with the fourth power of distance ($P_{rx} \propto d^{-4}$), yielding $40\text{ dB}$ of attenuation per decade of distance.

### Q5: What is the Thermal Noise Floor and what does $-174\text{ dBm/Hz}$ mean?
**Ans:** Thermal noise is generated by the random thermal agitation of electrons inside conductors (Johnson-Nyquist noise). The noise spectral density at room temperature ($T = 290\text{ K}$) is:
$$N_0 = k \cdot T = (1.38 \times 10^{-23})(290) \approx 4.00 \times 10^{-21}\text{ W/Hz} = -174\text{ dBm/Hz}$$
For a channel with bandwidth $B$ and noise figure $NF$:
$$N\text{ (dBm)} = -174 + 10\log_{10}(B) + NF$$

### Q6: What is Link Margin and what is considered an acceptable value?
**Ans:** Link margin is the excess received power above the minimum sensitivity required for demodulation ($\text{Margin} = P_{rx} - P_{rx,\text{sens}}$). A link margin of $10\text{ to }20\text{ dB}$ is typically recommended in commercial wireless deployments to safeguard against multipath fading, rain attenuation, and shadowing.

### Q7: How does Shannon's Theorem relate to the Link Budget?
**Ans:** Shannon-Hartley theorem defines the upper bound on error-free data rate:
$$C = B \cdot \log_2(1 + \text{SNR})$$
By calculating $P_{rx}$ and the noise floor $N$, the link budget gives the SNR ($P_{rx} - N$), which directly determines the channel's maximum achievable throughput.

---

## 👨‍💻 Author & Project Information
- **Course:** Wireless Communication (3171608)
- **Department:** Information Technology
- **Topic:** Micro-Project 8 – Wireless Link Budget GUI
