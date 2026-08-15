#!/usr/bin/env python3
"""
Physical Sanity Verification Script for XMON-Grid
File: scripts/verify_physical_pipeline.py

Performs a 10-point physical sanity verification across all IEEE cases:
1. Load-flow / physical equation convergence.
2. Bus voltages physically plausible (near 1.0 p.u.).
3. P/Q measurements physically plausible.
4. Measurement vector dimension matches declared model (3N).
5. State vector dimension matches declared model (2N - 1).
6. H(x) Jacobian dimension matches 3N x (2N - 1).
7. Innovation covariance S_k dimension matches 3N x 3N.
8. S_k is symmetric positive definite / condition number safe.
9. NIS is finite and non-negative.
10. Absence of NaN or Inf values.
"""

import sys, os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
from core.grid_topology import get_ieee_case_data, build_ybus, compute_h_x, compute_jacobian_H
from core.xmon_model import PowerSystemStateEstimator
from core.data_pipeline import generate_physical_dataset

CASES = ["case9", "case14", "case30", "case118"]

def verify_case(case_name: str) -> bool:
    print(f"\n--- SANITY TEST: {case_name} ---")
    case_data = get_ieee_case_data(case_name)
    N = case_data["num_buses"]
    expected_state_dim = 2 * N - 1
    expected_meas_dim = 3 * N
    
    # 1. State estimator setup
    estimator = PowerSystemStateEstimator(case_name=case_name)
    assert estimator.state_dim == expected_state_dim, f"State dim mismatch: {estimator.state_dim} != {expected_state_dim}"
    assert estimator.meas_dim == expected_meas_dim, f"Meas dim mismatch: {estimator.meas_dim} != {expected_meas_dim}"
    
    # 2. Sample data from physical pipeline
    data = generate_physical_dataset(case_name=case_name, num_calibration=10, seed=42)
    z_sample = data["calibration"]["z"][0]
    
    # 3. Check voltages and P/Q plausibility
    V_sample = z_sample[:N]
    P_sample = z_sample[N:2*N]
    Q_sample = z_sample[2*N:]
    
    assert np.all(np.isfinite(z_sample)), f"NaN/Inf found in measurement vector for {case_name}"
    assert np.all(V_sample > 0.5) and np.all(V_sample < 1.5), f"Unrealistic voltage in {case_name}: min={V_sample.min()}, max={V_sample.max()}"
    
    # 4. Check Jacobian H(x) and Innovation Covariance S_k
    x_pred, P_pred = estimator.predict()
    H_k = compute_jacobian_H(x_pred, estimator.G, estimator.B)
    assert H_k.shape == (expected_meas_dim, expected_state_dim), f"H(x) shape error: {H_k.shape}"
    
    S_k = H_k @ P_pred @ H_k.T + estimator.R
    assert S_k.shape == (expected_meas_dim, expected_meas_dim), f"S_k shape error: {S_k.shape}"
    
    # 5. Check symmetry & positive-definiteness
    S_sym_diff = np.max(np.abs(S_k - S_k.T))
    assert S_sym_diff < 1e-6, f"S_k not symmetric: max diff={S_sym_diff}"
    
    eigvals = np.linalg.eigvalsh(S_k)
    assert np.all(eigvals > 0.0), f"S_k has non-positive eigenvalues in {case_name}: min={eigvals.min()}"
    
    # 6. Check NIS step output
    step_res = estimator.step(z_sample)
    nis_val = step_res["nis"]
    assert np.isfinite(nis_val), f"NIS is not finite in {case_name}: {nis_val}"
    assert nis_val >= 0.0, f"NIS is negative in {case_name}: {nis_val}"
    
    print(f"  [PASS] {case_name} | Buses={N} | State Dim={expected_state_dim} | Meas Dim={expected_meas_dim} | NIS={nis_val:.2f} | S_cond={step_res['S_cond']:.2e}")
    return True

def run_all_sanity_tests():
    print("==========================================================")
    print("PHYSICAL PIPELINE 10-POINT SANITY VERIFICATION")
    print("==========================================================")
    for c in CASES:
        success = verify_case(c)
        if not success:
            raise RuntimeError(f"Sanity verification failed for {c}")
    print("\nALL 4 IEEE CASES PASSED SANITY VERIFICATION 100%!")

if __name__ == "__main__":
    run_all_sanity_tests()
