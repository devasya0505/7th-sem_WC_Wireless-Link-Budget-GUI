"""
Unit Test Suite for Wireless Link Budget Engine
===============================================
Verifies accuracy of RF equations, path loss models, presets, and sweeps.
"""

import unittest
import math
from link_budget_engine import (
    LinkBudgetParameters,
    calculate_link_budget,
    calculate_fspl,
    calculate_two_ray_path_loss,
    calculate_log_distance_path_loss,
    calculate_okumura_hata_path_loss,
    calculate_cost231_hata_path_loss,
    solve_max_achievable_distance,
    sweep_distance,
    PRESET_SCENARIOS,
    dbm_to_watts,
    watts_to_dbm,
    calculate_wavelength
)


class TestLinkBudgetEngine(unittest.TestCase):
    def test_power_conversions(self):
        # 30 dBm == 1 Watt
        self.assertAlmostEqual(dbm_to_watts(30.0), 1.0, places=4)
        self.assertAlmostEqual(watts_to_dbm(1.0), 30.0, places=4)

        # 0 dBm == 1 mW = 0.001 W
        self.assertAlmostEqual(dbm_to_watts(0.0), 0.001, places=6)
        self.assertAlmostEqual(watts_to_dbm(0.001), 0.0, places=4)

    def test_wavelength(self):
        # At 300 MHz, lambda = c / 300e6 ~= 0.9993 m (~1m)
        lam = calculate_wavelength(300.0)
        self.assertAlmostEqual(lam, 0.9993, places=2)
        # At 3000 MHz (3 GHz), lambda ~= 0.1 m
        self.assertAlmostEqual(calculate_wavelength(3000.0), 0.0999, places=2)

    def test_fspl_known_values(self):
        # FSPL = 32.44 + 20*log10(d_km) + 20*log10(f_MHz)
        # At d = 1 km, f = 1000 MHz (1 GHz):
        # FSPL = 32.44 + 0 + 20*3 = 92.44 dB
        fspl = calculate_fspl(1000.0, 1.0)
        self.assertAlmostEqual(fspl, 92.44, places=2)

        # At d = 10 km, f = 1000 MHz:
        # FSPL = 92.44 + 20 = 112.44 dB
        self.assertAlmostEqual(calculate_fspl(1000.0, 10.0), 112.44, places=2)

    def test_link_budget_basic(self):
        # Simple textbook link:
        # Ptx = 20 dBm (100 mW)
        # Gtx = 10 dBi, Ltx = 0 dB -> EIRP = 30 dBm
        # f = 1000 MHz, d = 1 km -> FSPL = 92.44 dB
        # Grx = 10 dBi, Lrx = 0 dB
        # Prx = 30 - 92.44 + 10 = -52.44 dBm
        # Sensitivity = -90 dBm -> Margin = -52.44 - (-90) = 37.56 dB (VIABLE)
        params = LinkBudgetParameters(
            tx_power_dbm=20.0,
            tx_antenna_gain_dbi=10.0,
            tx_cable_loss_db=0.0,
            frequency_mhz=1000.0,
            distance_km=1.0,
            path_loss_model="Free Space Path Loss (FSPL)",
            rain_attenuation_db=0.0,
            atmospheric_loss_db=0.0,
            obstacle_loss_db=0.0,
            polarization_loss_db=0.0,
            fade_margin_db=0.0,
            rx_antenna_gain_dbi=10.0,
            rx_cable_loss_db=0.0,
            rx_sensitivity_dbm=-90.0,
            bandwidth_mhz=20.0,
            noise_figure_db=5.0
        )
        res = calculate_link_budget(params)
        self.assertAlmostEqual(res.eirp_dbm, 30.0, places=2)
        self.assertAlmostEqual(res.rx_power_dbm, -52.44, places=1)
        self.assertAlmostEqual(res.link_margin_db, 37.56, places=1)
        self.assertTrue(res.is_link_viable)

    def test_presets_validity(self):
        for name, preset in PRESET_SCENARIOS.items():
            res = calculate_link_budget(preset)
            self.assertGreater(res.eirp_dbm, -100)
            self.assertGreater(res.total_path_loss_db, 0)
            self.assertIsNotNone(res.status_text)
            self.assertGreater(len(res.waterfall_stages), 4)

    def test_distance_sweep(self):
        preset = PRESET_SCENARIOS["Wi-Fi 6 (802.11ax) 2.4 GHz"]
        dists, rx_powers, snrs, caps = sweep_distance(preset, 0.01, 1.0, 50)
        self.assertEqual(len(dists), 50)
        # Power should decrease as distance increases
        self.assertGreater(rx_powers[0], rx_powers[-1])
        # SNR should decrease
        self.assertGreater(snrs[0], snrs[-1])
        # Capacity should decrease
        self.assertGreater(caps[0], caps[-1])

    def test_solver_max_distance(self):
        preset = PRESET_SCENARIOS["Wi-Fi 6 (802.11ax) 2.4 GHz"]
        max_d = solve_max_achievable_distance(preset)
        self.assertGreater(max_d, 0.0)


if __name__ == "__main__":
    unittest.main()
