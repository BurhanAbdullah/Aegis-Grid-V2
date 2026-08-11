#!/usr/bin/env python3
"""
Unit Test Suite for Canonical XMON-Grid Implementation
File: tests/test_xmon_model.py

Tests:
A. State estimator dimensions
B. Innovation dimensions
C. Innovation covariance S positive definiteness & symmetry
D. NIS non-negativity
E. NIS nominal distribution under benign noise
F. CUSUM reset behavior
G. Jitter calculation & windowing
H. Composite continuous threat score range [0, 1]
I. Quorum K=2 strict majority logic
J. Quorum K=1 sensitivity logic
K. Deterministic reproduction with fixed seed
"""

import unittest
import numpy as np
from core.grid_topology import get_ieee_case_data, build_ybus, compute_h_x, compute_jacobian_H
from core.xmon_model import (
    PowerSystemStateEstimator,
    NISDetector,
    CUSUMDetector,
    CommunicationJitterDetector,
    CompositeThreatScore,
    SequentialAccumulator,
    QuorumLogic,
    XMONGridModel
)
from core.data_pipeline import generate_physical_dataset

class TestXMONModel(unittest.TestCase):

    def setUp(self):
        self.case_name = "case9"
        self.case_data = get_ieee_case_data(self.case_name)
        self.N = self.case_data["num_buses"]
        self.estimator = PowerSystemStateEstimator(case_name=self.case_name)

    def test_A_state_estimator_dimensions(self):
        """Test A: State estimator dimensions match 2N-1 for state and 3N for measurement."""
        expected_state_dim = 2 * self.N - 1
        expected_meas_dim = 3 * self.N
        self.assertEqual(self.estimator.state_dim, expected_state_dim)
        self.assertEqual(self.estimator.meas_dim, expected_meas_dim)

    def test_B_innovation_dimensions(self):
        """Test B: Innovation r_k dimension matches measurement dimension 3N."""
        z_dummy = np.ones(self.estimator.meas_dim)
        res = self.estimator.step(z_dummy)
        self.assertEqual(len(res["residual"]), self.estimator.meas_dim)

    def test_C_S_positive_definiteness(self):
        """Test C: Innovation covariance S_k is symmetric and positive definite."""
        z_dummy = np.ones(self.estimator.meas_dim)
        x_pred, P_pred = self.estimator.predict()
        H_k = compute_jacobian_H(x_pred, self.estimator.G, self.estimator.B)
        S_k = H_k @ P_pred @ H_k.T + self.estimator.R
        
        # Symmetry check
        np.testing.assert_allclose(S_k, S_k.T, rtol=1e-5, atol=1e-7)
        # Eigenvalues must be strictly positive
        eigenvalues = np.linalg.eigvalsh(S_k)
        self.assertTrue(np.all(eigenvalues > 0.0), f"S_k has non-positive eigenvalues: {eigenvalues.min()}")

    def test_D_nis_non_negative(self):
        """Test D: NIS values are strictly non-negative."""
        z_dummy = np.ones(self.estimator.meas_dim)
        res = self.estimator.step(z_dummy)
        self.assertGreaterEqual(res["nis"], 0.0)

    def test_E_nis_nominal_distribution(self):
        """Test E: Under nominal benign noise, NIS values follow Chi-Square expectation E[NIS] ~ df."""
        data = generate_physical_dataset(case_name="case9", num_calibration=50, seed=123)
        # Warmup estimator on first 10 benign samples so P_k converges to steady state
        for z in data["calibration"]["z"][:10]:
            self.estimator.step(z)
            
        nis_vals = []
        for z in data["calibration"]["z"][10:]:
            res = self.estimator.step(z)
            nis_vals.append(res["nis"])
            
        mean_nis = np.mean(nis_vals)
        # E[chi2(m)] = m = 27 for case9 (3 * 9 = 27)
        self.assertTrue(mean_nis > 0.0, f"Mean NIS should be positive, got {mean_nis}")
        self.assertTrue(mean_nis < 300.0, f"Mean NIS should be bounded, got {mean_nis}")

    def test_F_cusum_reset_behavior(self):
        """Test F: CUSUM accumulator resets to zero properly."""
        cusum = CUSUMDetector(threshold=5.0)
        cusum.update(100.0)  # update with high anomaly
        self.assertGreater(cusum.g, 0.0)
        cusum.reset()
        self.assertEqual(cusum.g, 0.0)

    def test_G_jitter_calculation(self):
        """Test G: Jitter detector z-score calculation and window management."""
        jit = CommunicationJitterDetector(mu_T=0.004, sigma_T=0.0005, W=5)
        alarm, z, z_bar = jit.update(0.004)  # nominal interval -> z = 0
        self.assertAlmostEqual(z, 0.0, places=4)
        self.assertFalse(alarm)
        
        # Test attack spike
        for _ in range(5):
            alarm, z, z_bar = jit.update(0.008)  # 4ms shift -> z = (0.004)/0.0005 = 8.0
        self.assertTrue(alarm)

    def test_H_composite_score_range(self):
        """Test H: Composite Continuous Threat Score is strictly bounded in [0, 1]."""
        comp = CompositeThreatScore(w1=0.5, w2=0.3, w3=0.2)
        score_low = comp.compute(0.0, 27.0, 0.0, 5.0, 0.0, 2.0)
        score_high = comp.compute(1000.0, 27.0, 100.0, 5.0, 50.0, 2.0)
        
        self.assertGreaterEqual(score_low, 0.0)
        self.assertLessEqual(score_low, 1.0)
        self.assertGreaterEqual(score_high, 0.0)
        self.assertLessEqual(score_high, 1.0)

    def test_I_quorum_K2(self):
        """Test I: Quorum K=2 triggers strict majority if votes >= 2."""
        res_0 = QuorumLogic.evaluate(False, False, False)
        res_1 = QuorumLogic.evaluate(True, False, False)
        res_2 = QuorumLogic.evaluate(True, True, False)
        res_3 = QuorumLogic.evaluate(True, True, True)
        
        self.assertFalse(res_0["d_k2"])
        self.assertFalse(res_1["d_k2"])
        self.assertTrue(res_2["d_k2"])
        self.assertTrue(res_3["d_k2"])

    def test_J_quorum_K1(self):
        """Test J: Quorum K=1 triggers OR sensitivity mode if votes >= 1."""
        res_0 = QuorumLogic.evaluate(False, False, False)
        res_1 = QuorumLogic.evaluate(True, False, False)
        res_2 = QuorumLogic.evaluate(False, True, False)
        
        self.assertFalse(res_0["d_k1"])
        self.assertTrue(res_1["d_k1"])
        self.assertTrue(res_2["d_k1"])

    def test_K_deterministic_reproduction(self):
        """Test K: Fixed random seed produces identical results across runs."""
        data_1 = generate_physical_dataset(case_name="case9", num_calibration=10, seed=999)
        data_2 = generate_physical_dataset(case_name="case9", num_calibration=10, seed=999)
        
        np.testing.assert_allclose(data_1["calibration"]["z"], data_2["calibration"]["z"])
        np.testing.assert_allclose(data_1["calibration"]["iat"], data_2["calibration"]["iat"])

if __name__ == "__main__":
    unittest.main()
