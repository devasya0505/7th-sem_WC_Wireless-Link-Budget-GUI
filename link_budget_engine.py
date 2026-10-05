"""
Wireless Link Budget Engine
===========================
Core analytical models and algorithms for RF Link Budget calculations.
Part of the Wireless Communication (WC) Micro-Project.

Implements:
  - Transmitter EIRP calculation
  - Path Loss Models:
      * Free Space Path Loss (FSPL)
      * Two-Ray Ground Reflection Model
      * Log-Distance Path Loss Model (with customizable path exponent)
      * Okumura-Hata Model (Urban, Suburban, Open / Rural)
      * COST-231 Hata Model (1.5 - 2.0 GHz)
  - Atmospheric, Rain, Obstacle & Fade Margins
  - Thermal Noise Floor & Noise Figure calculation
  - Received Power (dBm, Watts), SNR (dB), and Link Margin (dB)
  - Shannon Channel Capacity & Max Allowable Path Loss (MAPL)
  - Distance & Frequency parameter sweeps
  - Standard Industry Presets (Wi-Fi, 4G LTE, 5G mmWave, Satellite Ku-band, LoRaWAN, Microwave)
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional


# Physical Constants
BOLTZMANN_K = 1.380649e-23  # J/K
SPEED_OF_LIGHT = 299792458.0  # m/s
STANDARD_TEMP_K = 290.0  # Standard reference temperature in Kelvin


@dataclass
class LinkBudgetParameters:
    """Input parameters defining a wireless communication link."""
    # Scenario Info
    scenario_name: str = "Standard Link"
    description: str = ""

    # Transmitter
    tx_power_dbm: float = 20.0        # Tx Output Power in dBm
    tx_antenna_gain_dbi: float = 2.15 # Tx Antenna Gain in dBi
    tx_cable_loss_db: float = 1.0     # Tx Cable & Connector Losses in dB

    # Channel & Geometry
    frequency_mhz: float = 2400.0     # Carrier Frequency in MHz
    distance_km: float = 0.5          # Link Distance in km
    path_loss_model: str = "Free Space Path Loss (FSPL)"
    
    # Model Specific Parameters
    path_loss_exponent: float = 3.0   # For Log-Distance model (2.0 = free space, 3.5 = urban)
    reference_distance_m: float = 1.0 # Reference distance for log-distance (m)
    tx_antenna_height_m: float = 30.0 # Base Station / Tx height in meters (Hata / Two-Ray)
    rx_antenna_height_m: float = 1.5  # Mobile / Rx height in meters (Hata / Two-Ray)
    environment_type: str = "Urban Small/Medium City" # For Okumura-Hata / COST-231

    # Environmental & Extra Losses
    rain_attenuation_db: float = 0.0  # Rain attenuation in dB
    atmospheric_loss_db: float = 0.0  # Atmospheric gas absorption in dB
    obstacle_loss_db: float = 0.0     # Building / wall / vegetation penetration loss in dB
    polarization_loss_db: float = 0.0 # Antenna polarization mismatch loss in dB
    fade_margin_db: float = 10.0      # Required fade / log-normal shadowing margin in dB

    # Receiver
    rx_antenna_gain_dbi: float = 2.15 # Rx Antenna Gain in dBi
    rx_cable_loss_db: float = 1.0     # Rx Cable & Filter Losses in dB
    rx_sensitivity_dbm: float = -90.0 # Minimum required received power in dBm
    noise_figure_db: float = 5.0      # Receiver front-end noise figure in dB
    bandwidth_mhz: float = 20.0       # Channel Bandwidth in MHz
    temperature_k: float = 290.0      # System noise temperature in Kelvin


@dataclass
class LinkBudgetResults:
    """Detailed calculation outputs for a wireless link budget."""
    # Transmitter Outputs
    tx_power_w: float = 0.0
    eirp_dbm: float = 0.0
    eirp_w: float = 0.0

    # Path Loss & Losses Breakdown
    free_space_path_loss_db: float = 0.0
    model_path_loss_db: float = 0.0
    total_environmental_losses_db: float = 0.0
    total_path_loss_db: float = 0.0
    total_attenuation_db: float = 0.0

    # Receiver Outputs
    rx_power_dbm: float = 0.0
    rx_power_w: float = 0.0
    rx_power_pw: float = 0.0          # Picowatts

    # Noise & SNR
    thermal_noise_density_dbm_hz: float = -174.0
    noise_bandwidth_db_hz: float = 0.0
    receiver_noise_floor_dbm: float = 0.0
    snr_db: float = 0.0

    # Margins & Performance
    link_margin_db: float = 0.0       # Rx Power - Sensitivity
    is_link_viable: bool = False
    status_text: str = ""
    max_allowable_path_loss_db: float = 0.0
    max_achievable_distance_km: float = 0.0
    shannon_capacity_mbps: float = 0.0
    wavelength_m: float = 0.0

    # Waterfall breakdown stages (Stage Name, Value in dBm, Delta in dB)
    waterfall_stages: List[Tuple[str, float, float]] = field(default_factory=list)


def dbm_to_watts(dbm: float) -> float:
    """Convert power from dBm to Watts."""
    return 10.0 ** ((dbm - 30.0) / 10.0)


def watts_to_dbm(watts: float) -> float:
    """Convert power from Watts to dBm."""
    if watts <= 0:
        return -999.0
    return 10.0 * math.log10(watts) + 30.0


def calculate_wavelength(frequency_mhz: float) -> float:
    """Calculate electromagnetic wavelength in meters."""
    freq_hz = frequency_mhz * 1e6
    if freq_hz <= 0:
        return 0.0
    return SPEED_OF_LIGHT / freq_hz


def calculate_fspl(frequency_mhz: float, distance_km: float) -> float:
    """
    Calculate Free Space Path Loss (FSPL) in dB.
    Formula: FSPL = 32.44 + 20*log10(d_km) + 20*log10(f_MHz)
    """
    if distance_km <= 0 or frequency_mhz <= 0:
        return 0.0
    return 32.44 + 20.0 * math.log10(distance_km) + 20.0 * math.log10(frequency_mhz)


def calculate_two_ray_path_loss(
    frequency_mhz: float,
    distance_km: float,
    htx_m: float,
    hrx_m: float
) -> float:
    """
    Two-Ray Ground Reflection Model.
    For distance >= crossover distance:
      PL = 40*log10(d) - 20*log10(htx) - 20*log10(hrx)
    For distance < crossover distance:
      Transitions smoothly to Free Space Path Loss.
    """
    if distance_km <= 0 or frequency_mhz <= 0:
        return 0.0
    d_m = distance_km * 1000.0
    wavelength = calculate_wavelength(frequency_mhz)
    
    # Crossover distance
    d_cross_m = (4.0 * math.pi * max(htx_m, 1.0) * max(hrx_m, 0.5)) / max(wavelength, 1e-6)
    
    if d_m <= d_cross_m:
        # Near region behaves as FSPL
        return calculate_fspl(frequency_mhz, distance_km)
    else:
        # Far-field asymptotic 40 dB/decade roll-off
        pl_two_ray = 40.0 * math.log10(d_m) - 20.0 * math.log10(max(htx_m, 0.1)) - 20.0 * math.log10(max(hrx_m, 0.1))
        # Ensure continuity with FSPL at crossover
        fspl_cross = calculate_fspl(frequency_mhz, d_cross_m / 1000.0)
        pl_two_ray_cross = 40.0 * math.log10(d_cross_m) - 20.0 * math.log10(max(htx_m, 0.1)) - 20.0 * math.log10(max(hrx_m, 0.1))
        offset = fspl_cross - pl_two_ray_cross
        return pl_two_ray + offset


def calculate_log_distance_path_loss(
    frequency_mhz: float,
    distance_km: float,
    path_loss_exponent: float,
    reference_distance_m: float = 1.0
) -> float:
    """
    Log-Distance Path Loss Model:
      PL(d) = PL(d0) + 10 * n * log10(d / d0)
    where PL(d0) is calculated using FSPL at reference distance d0.
    """
    if distance_km <= 0 or frequency_mhz <= 0:
        return 0.0
    d_m = distance_km * 1000.0
    ref_d_km = reference_distance_m / 1000.0
    pl_d0 = calculate_fspl(frequency_mhz, ref_d_km)
    
    if d_m <= reference_distance_m:
        return pl_d0
    
    pl = pl_d0 + 10.0 * path_loss_exponent * math.log10(d_m / reference_distance_m)
    return pl


def calculate_okumura_hata_path_loss(
    frequency_mhz: float,
    distance_km: float,
    hb_m: float,
    hm_m: float,
    env_type: str = "Urban Small/Medium City"
) -> float:
    """
    Okumura-Hata Propagation Model (150 MHz - 1500 MHz, d = 1 - 20 km, hb = 30 - 200 m, hm = 1 - 10 m).
    Extrapolated gracefully outside strict bounds for practical GUI exploration.
    """
    f = max(frequency_mhz, 150.0)
    d = max(distance_km, 0.01)
    hb = max(hb_m, 5.0)
    hm = max(hm_m, 0.5)

    # Antenna height correction factor a(hm)
    if "Large City" in env_type:
        if f >= 300.0:
            a_hm = 3.2 * (math.log10(11.75 * hm) ** 2) - 4.97
        else:
            a_hm = 8.29 * (math.log10(1.54 * hm) ** 2) - 1.1
    else:
        # Small / Medium city standard
        a_hm = (1.1 * math.log10(f) - 0.7) * hm - (1.56 * math.log10(f) - 0.8)

    # Urban Basic Path Loss
    pl_urban = (
        69.55
        + 26.16 * math.log10(f)
        - 13.82 * math.log10(hb)
        - a_hm
        + (44.9 - 6.55 * math.log10(hb)) * math.log10(d)
    )

    if "Suburban" in env_type:
        pl = pl_urban - 2.0 * ((math.log10(f / 28.0)) ** 2) - 5.4
        return pl
    elif "Open" in env_type or "Rural" in env_type:
        pl = pl_urban - 4.78 * ((math.log10(f)) ** 2) + 18.33 * math.log10(f) - 40.94
        return pl
    else:
        return pl_urban


def calculate_cost231_hata_path_loss(
    frequency_mhz: float,
    distance_km: float,
    hb_m: float,
    hm_m: float,
    env_type: str = "Urban Small/Medium City"
) -> float:
    """
    COST-231 Hata Model extension for PCS / Cellular (1500 MHz - 2000 MHz).
    """
    f = max(frequency_mhz, 1500.0)
    d = max(distance_km, 0.01)
    hb = max(hb_m, 5.0)
    hm = max(hm_m, 0.5)

    # Mobile antenna height correction factor
    a_hm = (1.1 * math.log10(f) - 0.7) * hm - (1.56 * math.log10(f) - 0.8)
    
    # Environment correction Cm: 0 dB for medium/suburban, 3 dB for metropolitan dense
    cm = 3.0 if "Large" in env_type or "Dense" in env_type else 0.0

    pl = (
        46.3
        + 33.9 * math.log10(f)
        - 13.82 * math.log10(hb)
        - a_hm
        + (44.9 - 6.55 * math.log10(hb)) * math.log10(d)
        + cm
    )
    return pl


def evaluate_path_loss(params: LinkBudgetParameters, dist_km: Optional[float] = None) -> float:
    """Calculate path loss based on the configured model."""
    d = dist_km if dist_km is not None else params.distance_km
    model = params.path_loss_model
    f = params.frequency_mhz

    if "Free Space" in model:
        return calculate_fspl(f, d)
    elif "Two-Ray" in model:
        return calculate_two_ray_path_loss(
            f, d, params.tx_antenna_height_m, params.rx_antenna_height_m
        )
    elif "Log-Distance" in model:
        return calculate_log_distance_path_loss(
            f, d, params.path_loss_exponent, params.reference_distance_m
        )
    elif "Okumura-Hata" in model:
        return calculate_okumura_hata_path_loss(
            f, d, params.tx_antenna_height_m, params.rx_antenna_height_m, params.environment_type
        )
    elif "COST-231" in model:
        return calculate_cost231_hata_path_loss(
            f, d, params.tx_antenna_height_m, params.rx_antenna_height_m, params.environment_type
        )
    else:
        return calculate_fspl(f, d)


def solve_max_achievable_distance(params: LinkBudgetParameters) -> float:
    """
    Numerically solve for maximum achievable distance where Link Margin = 0
    (i.e., Received Power Prx = Rx Sensitivity).
    Uses binary search over distance range [0.001 km to 50,000 km].
    """
    # Max allowable path loss at threshold
    # Prx = EIRP - (PL + L_env) + Grx - Lrx = Prx_sens
    # => PL = EIRP + Grx - Lrx - Prx_sens - L_env
    eirp = params.tx_power_dbm + params.tx_antenna_gain_dbi - params.tx_cable_loss_db
    env_losses = (
        params.rain_attenuation_db
        + params.atmospheric_loss_db
        + params.obstacle_loss_db
        + params.polarization_loss_db
        + params.fade_margin_db
    )
    target_pl = eirp + params.rx_antenna_gain_dbi - params.rx_cable_loss_db - params.rx_sensitivity_dbm - env_losses

    if target_pl <= 0:
        return 0.0

    # Binary search for distance yielding target_pl
    low_d = 0.0001 # 10 cm
    high_d = 50000.0 # 50,000 km (covers GEO satellite)
    
    # Check if even at 10cm it's unachievable
    if evaluate_path_loss(params, low_d) > target_pl:
        return 0.0

    for _ in range(60):
        mid_d = (low_d + high_d) / 2.0
        pl_mid = evaluate_path_loss(params, mid_d)
        if pl_mid < target_pl:
            low_d = mid_d
        else:
            high_d = mid_d

    return round((low_d + high_d) / 2.0, 4)


def calculate_link_budget(params: LinkBudgetParameters) -> LinkBudgetResults:
    """Perform full link budget calculations based on input parameters."""
    res = LinkBudgetResults()

    # Transmitter Calculations
    res.tx_power_w = dbm_to_watts(params.tx_power_dbm)
    res.eirp_dbm = params.tx_power_dbm + params.tx_antenna_gain_dbi - params.tx_cable_loss_db
    res.eirp_w = dbm_to_watts(res.eirp_dbm)

    # Path Loss & Losses Breakdown
    res.free_space_path_loss_db = calculate_fspl(params.frequency_mhz, params.distance_km)
    res.model_path_loss_db = evaluate_path_loss(params)
    
    res.total_environmental_losses_db = (
        params.rain_attenuation_db
        + params.atmospheric_loss_db
        + params.obstacle_loss_db
        + params.polarization_loss_db
        + params.fade_margin_db
    )

    res.total_path_loss_db = res.model_path_loss_db + res.total_environmental_losses_db
    res.total_attenuation_db = (
        params.tx_cable_loss_db
        + res.total_path_loss_db
        + params.rx_cable_loss_db
    )

    # Receiver Power
    # Prx = EIRP - Total Path Loss + Grx - Lrx
    res.rx_power_dbm = (
        res.eirp_dbm
        - res.total_path_loss_db
        + params.rx_antenna_gain_dbi
        - params.rx_cable_loss_db
    )
    res.rx_power_w = dbm_to_watts(res.rx_power_dbm)
    res.rx_power_pw = res.rx_power_w * 1e12

    # Noise Calculations
    # Thermal Noise Floor = k * T * B
    # In dBm: -174 dBm/Hz + 10*log10(B_Hz) + NF
    bw_hz = max(params.bandwidth_mhz * 1e6, 1.0)
    # k*T in dBm/Hz: 10*log10(k*T*1000)
    thermal_noise_density = 10.0 * math.log10(BOLTZMANN_K * max(params.temperature_k, 1.0) * 1000.0)
    res.thermal_noise_density_dbm_hz = thermal_noise_density
    res.noise_bandwidth_db_hz = 10.0 * math.log10(bw_hz)
    
    res.receiver_noise_floor_dbm = thermal_noise_density + res.noise_bandwidth_db_hz + params.noise_figure_db

    # SNR and Link Margin
    res.snr_db = res.rx_power_dbm - res.receiver_noise_floor_dbm
    res.link_margin_db = res.rx_power_dbm - params.rx_sensitivity_dbm

    # Link Viability Assessment
    res.is_link_viable = res.link_margin_db >= 0.0
    if res.link_margin_db >= 10.0:
        res.status_text = "EXCELLENT LINK (Margin >= 10 dB)"
    elif res.link_margin_db >= 0.0:
        res.status_text = "VIABLE / MARGINAL (0 <= Margin < 10 dB)"
    else:
        res.status_text = f"LINK DOWN / FAILED (Margin Deficit: {abs(res.link_margin_db):.2f} dB)"

    # MAPL (Maximum Allowable Path Loss)
    res.max_allowable_path_loss_db = (
        res.eirp_dbm
        + params.rx_antenna_gain_dbi
        - params.rx_cable_loss_db
        - params.rx_sensitivity_dbm
        - res.total_environmental_losses_db
    )

    # Maximum Achievable Distance
    res.max_achievable_distance_km = solve_max_achievable_distance(params)

    # Shannon Channel Capacity: C = B * log2(1 + SNR_linear)
    snr_linear = 10.0 ** (res.snr_db / 10.0)
    res.shannon_capacity_mbps = (bw_hz * math.log2(1.0 + max(snr_linear, 0.0))) / 1e6

    # Wavelength
    res.wavelength_m = calculate_wavelength(params.frequency_mhz)

    # Build Stage-by-Stage Waterfall Budget
    # Cumulative power levels at each interface
    stages = []
    current_level = params.tx_power_dbm
    stages.append(("Tx Power", current_level, params.tx_power_dbm))

    current_level -= params.tx_cable_loss_db
    stages.append(("After Tx Loss", current_level, -params.tx_cable_loss_db))

    current_level += params.tx_antenna_gain_dbi
    stages.append(("EIRP (Tx Antenna)", current_level, params.tx_antenna_gain_dbi))

    current_level -= res.model_path_loss_db
    stages.append(("After Path Loss", current_level, -res.model_path_loss_db))

    if res.total_environmental_losses_db > 0:
        current_level -= res.total_environmental_losses_db
        stages.append(("After Env Losses", current_level, -res.total_environmental_losses_db))

    current_level += params.rx_antenna_gain_dbi
    stages.append(("Rx Antenna Gain", current_level, params.rx_antenna_gain_dbi))

    current_level -= params.rx_cable_loss_db
    stages.append(("Rx Power (Input)", current_level, -params.rx_cable_loss_db))

    res.waterfall_stages = stages

    return res


def sweep_distance(
    params: LinkBudgetParameters,
    min_dist_km: float = 0.05,
    max_dist_km: float = 10.0,
    points: int = 100
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Generate parametric sweep across distance.
    Returns: (distances, rx_powers, snr_values, capacities)
    """
    if min_dist_km <= 0:
        min_dist_km = 0.01
    
    # Logarithmic or linear spacing
    log_min = math.log10(min_dist_km)
    log_max = math.log10(max_dist_km)
    step = (log_max - log_min) / (points - 1)
    
    dists = [10.0 ** (log_min + i * step) for i in range(points)]
    rx_powers = []
    snrs = []
    capacities = []

    # Precalculate invariant terms
    eirp = params.tx_power_dbm + params.tx_antenna_gain_dbi - params.tx_cable_loss_db
    env_losses = (
        params.rain_attenuation_db
        + params.atmospheric_loss_db
        + params.obstacle_loss_db
        + params.polarization_loss_db
        + params.fade_margin_db
    )
    rx_gain_net = params.rx_antenna_gain_dbi - params.rx_cable_loss_db
    bw_hz = max(params.bandwidth_mhz * 1e6, 1.0)
    noise_floor = (
        10.0 * math.log10(BOLTZMANN_K * max(params.temperature_k, 1.0) * 1000.0)
        + 10.0 * math.log10(bw_hz)
        + params.noise_figure_db
    )

    for d in dists:
        pl = evaluate_path_loss(params, dist_km=d)
        prx = eirp - pl - env_losses + rx_gain_net
        snr = prx - noise_floor
        snr_lin = 10.0 ** (snr / 10.0)
        cap = (bw_hz * math.log2(1.0 + max(snr_lin, 0.0))) / 1e6
        
        rx_powers.append(prx)
        snrs.append(snr)
        capacities.append(cap)

    return dists, rx_powers, snrs, capacities


# Predefined Industry Standard Scenarios
PRESET_SCENARIOS: Dict[str, LinkBudgetParameters] = {
    "Wi-Fi 6 (802.11ax) 2.4 GHz": LinkBudgetParameters(
        scenario_name="Wi-Fi 6 (802.11ax) 2.4 GHz Indoor/Campus",
        description="Standard wireless LAN link for office / campus coverage at 2.4 GHz with log-distance indoor shadowing.",
        tx_power_dbm=20.0,
        tx_antenna_gain_dbi=3.0,
        tx_cable_loss_db=0.5,
        frequency_mhz=2437.0,
        distance_km=0.08,  # 80 meters
        path_loss_model="Log-Distance Model",
        path_loss_exponent=3.0,
        reference_distance_m=1.0,
        rain_attenuation_db=0.0,
        atmospheric_loss_db=0.0,
        obstacle_loss_db=6.0,  # 2 drywall partitions
        polarization_loss_db=0.0,
        fade_margin_db=10.0,
        rx_antenna_gain_dbi=2.0,
        rx_cable_loss_db=0.5,
        rx_sensitivity_dbm=-82.0,
        noise_figure_db=6.0,
        bandwidth_mhz=20.0,
        temperature_k=290.0
    ),
    "Wi-Fi 6 (802.11ax) 5 GHz": LinkBudgetParameters(
        scenario_name="Wi-Fi 6 (802.11ax) 5 GHz High-Throughput",
        description="High-speed 80 MHz channel in 5 GHz band with higher wall attenuation and path loss.",
        tx_power_dbm=23.0,
        tx_antenna_gain_dbi=5.0,
        tx_cable_loss_db=0.8,
        frequency_mhz=5180.0,
        distance_km=0.05,  # 50 meters
        path_loss_model="Log-Distance Model",
        path_loss_exponent=3.2,
        reference_distance_m=1.0,
        rain_attenuation_db=0.0,
        atmospheric_loss_db=0.0,
        obstacle_loss_db=10.0,  # Brick wall / floor penetration
        polarization_loss_db=0.0,
        fade_margin_db=12.0,
        rx_antenna_gain_dbi=3.0,
        rx_cable_loss_db=0.5,
        rx_sensitivity_dbm=-75.0,
        noise_figure_db=7.0,
        bandwidth_mhz=80.0,
        temperature_k=290.0
    ),
    "4G LTE Cellular Base Station (1800 MHz)": LinkBudgetParameters(
        scenario_name="4G LTE Urban Macro Cell (1800 MHz Band 3)",
        description="Downlink from eNodeB tower to mobile user equipment in an urban propagation environment.",
        tx_power_dbm=43.0,  # 20 Watts
        tx_antenna_gain_dbi=16.0,
        tx_cable_loss_db=2.0,
        frequency_mhz=1800.0,
        distance_km=2.0,
        path_loss_model="COST-231 Hata Model",
        tx_antenna_height_m=35.0,
        rx_antenna_height_m=1.5,
        environment_type="Urban Small/Medium City",
        rain_attenuation_db=0.0,
        atmospheric_loss_db=0.0,
        obstacle_loss_db=12.0, # Building penetration margin
        polarization_loss_db=0.0,
        fade_margin_db=10.0,
        rx_antenna_gain_dbi=0.0, # Smartphone omni
        rx_cable_loss_db=0.0,
        rx_sensitivity_dbm=-100.0,
        noise_figure_db=7.0,
        bandwidth_mhz=20.0,
        temperature_k=290.0
    ),
    "5G NR mmWave Urban Small Cell (28 GHz)": LinkBudgetParameters(
        scenario_name="5G NR FR2 mmWave Link (28 GHz)",
        description="Ultra-high bandwidth millimeter-wave microcell with directional beamforming array.",
        tx_power_dbm=30.0,  # 1 Watt
        tx_antenna_gain_dbi=22.0, # Phased array beamforming gain
        tx_cable_loss_db=1.5,
        frequency_mhz=28000.0,
        distance_km=0.3, # 300 meters line-of-sight
        path_loss_model="Free Space Path Loss (FSPL)",
        rain_attenuation_db=2.5, # Heavy rain attenuation at mmWave
        atmospheric_loss_db=0.5, # Oxygen & water vapor absorption
        obstacle_loss_db=0.0,
        polarization_loss_db=0.5,
        fade_margin_db=15.0,
        rx_antenna_gain_dbi=12.0, # Mobile UE beamforming gain
        rx_cable_loss_db=1.0,
        rx_sensitivity_dbm=-86.0,
        noise_figure_db=9.0,
        bandwidth_mhz=400.0,
        temperature_k=290.0
    ),
    "Satellite Ku-band Downlink (GEO 36,000 km)": LinkBudgetParameters(
        scenario_name="GEO Satellite Ku-band TV / Data Downlink",
        description="Geostationary satellite downlink to 90 cm parabolic dish Earth station.",
        tx_power_dbm=50.0,  # 100 Watts transponder
        tx_antenna_gain_dbi=38.0, # Satellite spot beam
        tx_cable_loss_db=1.5,
        frequency_mhz=12000.0, # 12 GHz Ku-band
        distance_km=36000.0, # Geostationary orbit
        path_loss_model="Free Space Path Loss (FSPL)",
        rain_attenuation_db=3.0,
        atmospheric_loss_db=0.6,
        obstacle_loss_db=0.0,
        polarization_loss_db=0.3,
        fade_margin_db=6.0,
        rx_antenna_gain_dbi=39.5, # 90 cm parabolic dish
        rx_cable_loss_db=1.0,
        rx_sensitivity_dbm=-115.0,
        noise_figure_db=1.5, # Low-Noise Block downconverter (LNB)
        bandwidth_mhz=36.0,
        temperature_k=150.0 # Clear sky antenna noise temperature
    ),
    "Satellite LEO Starlink-style Downlink (550 km)": LinkBudgetParameters(
        scenario_name="LEO Satellite Broadband Downlink (550 km Ku/Ka)",
        description="Low Earth Orbit constellation satellite communicating with phased-array user terminal.",
        tx_power_dbm=40.0,  # 10 Watts
        tx_antenna_gain_dbi=32.0,
        tx_cable_loss_db=1.0,
        frequency_mhz=12500.0,
        distance_km=750.0, # Slant range at 45 deg elevation
        path_loss_model="Free Space Path Loss (FSPL)",
        rain_attenuation_db=2.0,
        atmospheric_loss_db=0.5,
        obstacle_loss_db=0.0,
        polarization_loss_db=0.2,
        fade_margin_db=8.0,
        rx_antenna_gain_dbi=34.0, # Phased array user dish
        rx_cable_loss_db=0.5,
        rx_sensitivity_dbm=-105.0,
        noise_figure_db=2.0,
        bandwidth_mhz=250.0,
        temperature_k=180.0
    ),
    "LoRaWAN Long-Range IoT (868 MHz)": LinkBudgetParameters(
        scenario_name="LoRaWAN Long-Range Sub-GHz IoT (EU 868 MHz)",
        description="Low-power wide-area sensor link with high sensitivity Chirp Spread Spectrum modulation.",
        tx_power_dbm=14.0,  # 25 mW max ERP
        tx_antenna_gain_dbi=2.15,
        tx_cable_loss_db=0.2,
        frequency_mhz=868.0,
        distance_km=5.0,
        path_loss_model="Okumura-Hata Model",
        tx_antenna_height_m=20.0,
        rx_antenna_height_m=1.0,
        environment_type="Open / Rural Area",
        rain_attenuation_db=0.0,
        atmospheric_loss_db=0.0,
        obstacle_loss_db=3.0,
        polarization_loss_db=0.0,
        fade_margin_db=10.0,
        rx_antenna_gain_dbi=5.0, # Gateway antenna
        rx_cable_loss_db=1.0,
        rx_sensitivity_dbm=-137.0, # Extreme sensitivity at SF12
        noise_figure_db=5.0,
        bandwidth_mhz=0.125, # 125 kHz
        temperature_k=290.0
    ),
    "Microwave Point-to-Point Backhaul (18 GHz)": LinkBudgetParameters(
        scenario_name="Telecom Microwave Backhaul Link (18 GHz, 10 km)",
        description="High-capacity fixed wireless link connecting cellular towers using dual dish antennas.",
        tx_power_dbm=24.0,  # 250 mW
        tx_antenna_gain_dbi=42.0, # 1.2m parabolic dish
        tx_cable_loss_db=2.0,
        frequency_mhz=18000.0,
        distance_km=10.0,
        path_loss_model="Free Space Path Loss (FSPL)",
        rain_attenuation_db=15.0, # Heavy rain event (ITU-R 99.99% availability)
        atmospheric_loss_db=1.2,
        obstacle_loss_db=0.0, # Clear line-of-sight
        polarization_loss_db=0.0,
        fade_margin_db=25.0,
        rx_antenna_gain_dbi=42.0,
        rx_cable_loss_db=2.0,
        rx_sensitivity_dbm=-78.0,
        noise_figure_db=4.5,
        bandwidth_mhz=56.0,
        temperature_k=290.0
    )
}
