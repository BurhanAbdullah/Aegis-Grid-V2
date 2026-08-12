#!/usr/bin/env python3
"""
Authoritative Canonical Model for XMON-Grid
File: core/xmon_model.py

Implements mathematically rigorous state estimation, NIS calculation,
CUSUM, communication jitter detection, composite continuous threat score,
sequential accumulator, and K=2 / K=1 quorum voting logic.
"""

import numpy as np
from typing import Dict, Any, Tuple
from core.grid_topology import get_ieee_case_data, build_ybus, compute_h_x, compute_jacobian_H

# =====================================================================
# 1. State Estimation & NIS Calculation
# =====================================================================

class PowerSystemStateEstimator:
    """
    Extended Kalman Filter / WLS State Estimator for AC Power Grids.
    State vector x = [theta_2..theta_N, V_1..V_N]^T (Dim: 2N - 1)
    Measurement z = [V_1..V_N, P_1..P_N, Q_1..Q_N]^T (Dim: 3N)
    """
    def __init__(self, case_name: str = "case9", process_noise_std: float = 0.001, measurement_noise_std: float = 0.002):
        self.case_data = get_ieee_case_data(case_name)
        self.Ybus, self.G, self.B = build_ybus(self.case_data)
        
        self.N = self.case_data["num_buses"]
        self.state_dim = 2 * self.N - 1
        self.meas_dim = 3 * self.N
        
        # Initial state: theta = 0, V = 1.0 p.u.
        self.x_hat = np.zeros(self.state_dim)
        self.x_hat[self.N - 1 :] = 1.0  # V_1..V_N = 1.0
        
        # Initial error covariance P
        self.P = np.eye(self.state_dim) * 1e-3
        
        # Process noise covariance Q for [theta_2..theta_N, V_1..V_N]
        q_theta = np.full(self.N - 1, (0.001) ** 2)
        q_v = np.full(self.N, (0.002) ** 2)
        self.Q = np.diag(np.concatenate([q_theta, q_v]))
        
        # Diagonal R for [V_1..V_N, P_1..P_N, Q_1..Q_N]
        v_var = (0.002) ** 2
        pq_var = (0.005) ** 2
        r_diag = np.concatenate([
            np.full(self.N, v_var),
            np.full(self.N, pq_var),
            np.full(self.N, pq_var)
        ])
        self.R = np.diag(r_diag)

    def reset(self):
        """Resets estimator state vector x_hat to nominal and error covariance P to initial state."""
        self.x_hat = np.zeros(self.state_dim)
        self.x_hat[self.N - 1 :] = 1.0  # V_1..V_N = 1.0
        self.P = np.eye(self.state_dim) * 1e-3

    def predict(self) -> Tuple[np.ndarray, np.ndarray]:
        """State prediction step: x_{k|k-1} = x_{k-1|k-1}, P_{k|k-1} = P_{k-1|k-1} + Q"""
        x_pred = self.x_hat.copy()
        P_pred = self.P + self.Q
        return x_pred, P_pred

    def step(self, z_meas: np.ndarray) -> Dict[str, Any]:
        """
        Executes prediction, measurement residual, innovation covariance,
        NIS computation, and Joseph-form state update.
        """
        z_meas = np.asarray(z_meas, dtype=float).flatten()
        if len(z_meas) != self.meas_dim:
            raise ValueError(f"Measurement dimension mismatch: expected {self.meas_dim}, got {len(z_meas)}")
            
        # 1. Prediction
        x_pred, P_pred = self.predict()
        
        # 2. Predicted measurement and Jacobian
        h_pred = compute_h_x(x_pred, self.G, self.B)
        H_k = compute_jacobian_H(x_pred, self.G, self.B)
        
        # 3. Measurement residual / Innovation r_k
        r_k = z_meas - h_pred
        
        # 4. Innovation covariance S_k = H P_pred H^T + R
        S_k = H_k @ P_pred @ H_k.T + self.R
        
        # 5. Numerical stability & checks
        # Enforce symmetry
        S_k = 0.5 * (S_k + S_k.T)
        
        # Check condition number and apply ridge regularization if ill-conditioned
        cond_num = float(np.linalg.cond(S_k))
        if cond_num > 1e12 or np.isnan(cond_num):
            S_k += np.eye(self.meas_dim) * 1e-6
            
        # 6. NIS calculation using np.linalg.solve (no explicit inverse!)
        try:
            S_inv_r = np.linalg.solve(S_k, r_k)
            nis_val = float(r_k.T @ S_inv_r)
        except np.linalg.LinAlgError:
            nis_val = float(np.linalg.norm(r_k) ** 2)
            S_inv_r = np.zeros_like(r_k)
            
        nis_val = max(0.0, nis_val)
        
        # 7. Kalman Gain K_k = P_pred H^T S_k^{-1}
        try:
            K_k = np.linalg.solve(S_k.T, H_k @ P_pred).T
        except np.linalg.LinAlgError:
            K_k = np.zeros((self.state_dim, self.meas_dim))
            
        # 8. State update x_{k|k}
        self.x_hat = x_pred + K_k @ r_k
        
        # 9. Joseph-form covariance update: P_{k|k} = (I - K H) P_pred (I - K H)^T + K R K^T
        I_KH = np.eye(self.state_dim) - K_k @ H_k
        self.P = I_KH @ P_pred @ I_KH.T + K_k @ self.R @ K_k.T
        self.P = 0.5 * (self.P + self.P.T)  # enforce symmetry
        
        return {
            "x_hat": self.x_hat.copy(),
            "residual": r_k,
            "residual_norm": float(np.linalg.norm(r_k)),
            "nis": nis_val,
            "meas_dim": self.meas_dim,
            "state_dim": self.state_dim,
            "S_cond": cond_num
        }

# =====================================================================
# 2. NIS Detector
# =====================================================================

class NISDetector:
    """
    NIS Anomaly Detector using exact Chi-Square distribution chi2(df=m).
    """
    def __init__(self, meas_dim: int, alpha: float = 0.01):
        self.meas_dim = meas_dim
        self.alpha = alpha
        # Deterministic threshold calculation (Chi-Square percent point function)
        # Using analytical approximation if scipy is unavailable, or scipy.stats
        try:
            from scipy.stats import chi2
            self.threshold = float(chi2.ppf(1.0 - alpha, df=meas_dim))
        except ImportError:
            # Wilson-Hilferty transformation approximation for chi2 ppf
            z = 2.326348  # z for 99% confidence (alpha = 0.01)
            self.threshold = float(meas_dim * (1.0 - 2.0 / (9.0 * meas_dim) + z * np.sqrt(2.0 / (9.0 * meas_dim))) ** 3)

    def update(self, nis_val: float) -> Tuple[bool, float]:
        alarm = bool(nis_val > self.threshold)
        return alarm, self.threshold

# =====================================================================
# 3. One-Sided CUSUM Detector
# =====================================================================

class CUSUMDetector:
    """
    Standard one-sided CUSUM detector.
    Accumulates standardized NIS innovations: g_k = max(0, g_{k-1} + y_k - mu_0 - kappa)
    """
    def __init__(self, mu_0: float = 0.0, kappa: float = 0.5, threshold: float = 5.0):
        self.mu_0 = mu_0
        self.kappa = kappa
        self.threshold = threshold
        self.g = 0.0
        
        # Calibration baseline stats
        self.baseline_mean = 0.0
        self.baseline_std = 1.0

    def calibrate(self, benign_nis_samples: np.ndarray):
        arr = np.asarray(benign_nis_samples, dtype=float)
        self.baseline_mean = float(np.mean(arr))
        self.baseline_std = float(np.std(arr)) + 1e-9

    def update(self, nis_val: float) -> Tuple[bool, float]:
        # Standardize NIS relative to benign baseline
        y_k = (nis_val - self.baseline_mean) / self.baseline_std
        
        # Accumulate
        self.g = max(0.0, self.g + y_k - self.mu_0 - self.kappa)
        alarm = bool(self.g > self.threshold)
        return alarm, float(self.g)

    def reset(self):
        self.g = 0.0

# =====================================================================
# 4. Communication Jitter Detector
# =====================================================================

class CommunicationJitterDetector:
    """
    Dual-threshold Communication Jitter Detector.
    Instantaneous z-score J_k = |delta_t - mu_T| / sigma_T
    Window average Jbar_W = mean(J_{k-W+1}..J_k)
    """
    def __init__(self, mu_T: float = 0.004, sigma_T: float = 0.0005, eta_sigma: float = 3.5, eta_mu: float = 2.0, W: int = 20):
        self.mu_T = mu_T
        self.sigma_T = sigma_T
        self.eta_sigma = eta_sigma
        self.eta_mu = eta_mu
        self.W = W
        self.window = []

    def calibrate(self, benign_iat_samples: np.ndarray):
        arr = np.asarray(benign_iat_samples, dtype=float)
        self.mu_T = float(np.mean(arr))
        self.sigma_T = float(np.std(arr)) + 1e-9

    def update(self, delta_t: float) -> Tuple[bool, float, float]:
        j_k = abs(delta_t - self.mu_T) / self.sigma_T
        self.window.append(j_k)
        if len(self.window) > self.W:
            self.window.pop(0)
            
        j_bar = float(np.mean(self.window))
        alarm = bool(j_k > self.eta_sigma and j_bar > self.eta_mu)
        return alarm, j_k, j_bar

    def reset(self):
        self.window.clear()

# =====================================================================
# 5. Continuous Composite Threat Score
# =====================================================================

class CompositeThreatScore:
    """
    Normalized continuous composite threat score S_comp in [0, 1].
    Excludes discrete consensus votes.
    S_comp = w1 * S_NIS + w2 * S_CUSUM + w3 * S_JITTER
    """
    def __init__(self, w1: float = 0.50, w2: float = 0.30, w3: float = 0.20):
        assert abs((w1 + w2 + w3) - 1.0) < 1e-5, "Weights must sum to 1.0"
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3

    def compute(self, nis_val: float, nis_threshold: float, cusum_g: float, cusum_threshold: float, jitter_bar: float, jitter_threshold: float) -> float:
        # Component normalization into [0, 1]
        s_nis = min(1.0, max(0.0, nis_val) / (2.0 * nis_threshold))
        s_cusum = min(1.0, max(0.0, cusum_g) / (2.0 * cusum_threshold))
        s_jitter = min(1.0, max(0.0, jitter_bar) / (2.0 * jitter_threshold))
        
        s_comp = self.w1 * s_nis + self.w2 * s_cusum + self.w3 * s_jitter
        return float(np.clip(s_comp, 0.0, 1.0))

# =====================================================================
# 6. Sequential Accumulator
# =====================================================================

class SequentialAccumulator:
    """
    Sequential accumulator: Theta_k = alpha * Theta_{k-1} + S_comp(k)
    Threshold calibrated strictly on benign data: tau = mean_benign + 3 * std_benign
    """
    def __init__(self, alpha: float = 0.90):
        self.alpha = alpha
        self.theta = 0.0
        self.threshold = 3.0  # default, updated by calibration

    def calibrate(self, benign_theta_samples: np.ndarray):
        arr = np.asarray(benign_theta_samples, dtype=float)
        mu = float(np.mean(arr))
        sigma = float(np.std(arr))
        self.threshold = mu + 3.0 * sigma

    def update(self, s_comp: float) -> Tuple[bool, float]:
        self.theta = self.alpha * self.theta + s_comp
        alarm = bool(self.theta > self.threshold)
        return alarm, float(self.theta)

    def reset(self):
        self.theta = 0.0

# =====================================================================
# 7. Quorum Logic
# =====================================================================

class QuorumLogic:
    """
    Evaluates Strict Majority (K=2) and OR Sensitivity (K=1) quorums.
    """
    @staticmethod
    def evaluate(a_nis: bool, a_cusum: bool, a_jitter: bool) -> Dict[str, Any]:
        votes = int(a_nis) + int(a_cusum) + int(a_jitter)
        d_k2 = bool(votes >= 2)
        d_k1 = bool(votes >= 1)
        return {
            "votes": votes,
            "d_k2": d_k2,
            "d_k1": d_k1,
            "a_nis": int(a_nis),
            "a_cusum": int(a_cusum),
            "a_jitter": int(a_jitter),
        }

# =====================================================================
# 8. Unified Authoritative XMON-Grid Pipeline
# =====================================================================

class XMONGridModel:
    """
    Authoritative XMON-Grid model wrapper uniting state estimation,
    detectors, fusion, and quorum logic.
    """
    def __init__(self, case_name: str = "case9"):
        self.case_name = case_name
        self.estimator = PowerSystemStateEstimator(case_name=case_name)
        self.nis_detector = NISDetector(meas_dim=self.estimator.meas_dim)
        self.cusum_detector = CUSUMDetector()
        self.jitter_detector = CommunicationJitterDetector()
        self.composite_threat = CompositeThreatScore()
        self.sequential_accumulator = SequentialAccumulator()
        self.tau_comp = 0.30  # default, updated by benign calibration

    def calibrate_benign(self, benign_measurements: np.ndarray, benign_iats: np.ndarray):
        """
        Calibrates detector baselines strictly on benign calibration data.
        """
        nis_list = []
        for z in benign_measurements:
            est_res = self.estimator.step(z)
            nis_list.append(est_res["nis"])
            
        self.cusum_detector.calibrate(np.array(nis_list))
        self.jitter_detector.calibrate(benign_iats)
        
        # Calibrate sequential accumulator and continuous threat score threshold on benign scores
        self.cusum_detector.reset()
        self.jitter_detector.reset()
        self.sequential_accumulator.reset()
        
        theta_list = []
        s_comp_list = []
        for nis_v, delta_t in zip(nis_list, benign_iats):
            a_n, th_n = self.nis_detector.update(nis_v)
            a_c, g_c = self.cusum_detector.update(nis_v)
            a_j, j_k, j_bar = self.jitter_detector.update(delta_t)
            s_comp = self.composite_threat.compute(nis_v, th_n, g_c, self.cusum_detector.threshold, j_bar, self.jitter_detector.eta_mu)
            s_comp_list.append(s_comp)
            a_seq, theta = self.sequential_accumulator.update(s_comp)
            theta_list.append(theta)
            
        self.sequential_accumulator.calibrate(np.array(theta_list))
        self.tau_comp = float(np.percentile(s_comp_list, 99.0))
        
        # Reset state after calibration
        self.reset()

    def reset(self):
        """
        Resets state estimator and all stateful detectors to clean initial state.
        Ensures zero information leakage across independent test scenarios.
        """
        self.estimator.reset()
        self.cusum_detector.reset()
        self.jitter_detector.reset()
        self.sequential_accumulator.reset()

    def step(self, z_meas: np.ndarray, delta_t: float) -> Dict[str, Any]:
        """
        Single-step pipeline execution for online detection.
        """
        # 1. State estimation & NIS
        est_res = self.estimator.step(z_meas)
        nis_val = est_res["nis"]
        
        # 2. Individual detector evaluations
        a_nis, nis_thresh = self.nis_detector.update(nis_val)
        a_cusum, cusum_g = self.cusum_detector.update(nis_val)
        a_jitter, j_k, j_bar = self.jitter_detector.update(delta_t)
        
        # Memoryless (instantaneous) CUSUM evaluation for Ablation E
        y_k = (nis_val - self.cusum_detector.baseline_mean) / (self.cusum_detector.baseline_std + 1e-9)
        g_inst = max(0.0, y_k - self.cusum_detector.mu_0 - self.cusum_detector.kappa)
        a_cusum_inst = int(g_inst > self.cusum_detector.threshold)
        
        # 3. Continuous Composite Threat Score
        s_comp = self.composite_threat.compute(
            nis_val=nis_val,
            nis_threshold=nis_thresh,
            cusum_g=cusum_g,
            cusum_threshold=self.cusum_detector.threshold,
            jitter_bar=j_bar,
            jitter_threshold=self.jitter_detector.eta_mu
        )
        
        # 4. Sequential Accumulator
        a_seq, theta = self.sequential_accumulator.update(s_comp)
        
        # 5. Quorum Voting
        quorum_res = QuorumLogic.evaluate(a_nis, a_cusum, a_jitter)
        
        # Return complete step trace
        return {
            "case": self.case_name,
            "nis": nis_val,
            "nis_threshold": nis_thresh,
            "cusum_g": cusum_g,
            "cusum_threshold": self.cusum_detector.threshold,
            "jitter_z": j_k,
            "jitter_bar": j_bar,
            "s_comp": s_comp,
            "tau_comp": round(self.tau_comp, 6),
            "theta_seq": theta,
            "theta_threshold": self.sequential_accumulator.threshold,
            "a_nis": quorum_res["a_nis"],
            "a_cusum": quorum_res["a_cusum"],
            "a_cusum_inst": a_cusum_inst,
            "a_jitter": quorum_res["a_jitter"],
            "a_seq": int(a_seq),
            "votes": quorum_res["votes"],
            "d_k2": int(quorum_res["d_k2"]),
            "d_k1": int(quorum_res["d_k1"]),
            "S_cond": est_res["S_cond"],
        }
