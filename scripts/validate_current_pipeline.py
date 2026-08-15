#!/usr/bin/env python3
"""Cross-validate the repaired model, benchmark generator and analytical math."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_pipeline import generate_physical_dataset
from core.grid_topology import build_ybus, compute_h_x, compute_jacobian, get_ieee_case_data

CASES = ("case9", "case14", "case30", "case118")
SCENARIOS = {"baseline", "branch_outage", "fdia", "load_shift", "stealth_drift"}


def finite_difference_check(case_name="case9"):
    case = get_ieee_case_data(case_name)
    _, G, B = build_ybus(case)
    n = case["num_buses"]
    rng = np.random.RandomState(7)
    x = np.concatenate([rng.normal(0, 0.03, n - 1), 1 + rng.normal(0, 0.01, n)])
    H = compute_jacobian(x, G, B)
    h0 = compute_h_x(x, G, B)
    H_fd = np.zeros_like(H)
    eps = 1e-6
    for j in range(len(x)):
        xp = x.copy(); xm = x.copy()
        xp[j] += eps; xm[j] -= eps
        H_fd[:, j] = (compute_h_x(xp, G, B) - compute_h_x(xm, G, B)) / (2 * eps)
    err = float(np.max(np.abs(H - H_fd)))
    if err > 1e-5:
        raise AssertionError(f"{case_name}: analytical Jacobian finite-difference error {err:.3e}")
    if not np.all(np.isfinite(h0)):
        raise AssertionError(f"{case_name}: non-finite measurement function")
    return err


def main():
    jac_err = finite_difference_check()
    print(f"PASS Jacobian finite-difference cross-check: max error={jac_err:.3e}")

    for case in CASES:
        d1 = generate_physical_dataset(case, 20, 10, 4, seed=31415)
        d2 = generate_physical_dataset(case, 20, 10, 4, seed=31415)
        if not np.array_equal(d1["calibration"]["z"], d2["calibration"]["z"]):
            raise AssertionError(f"{case}: seeded calibration is not reproducible")
        if d1["benchmark_provenance"] != "canonical PYPOWER IEEE topology; synthetic seeded measurements/attacks":
            raise AssertionError(f"{case}: provenance marker mismatch")
        scenarios = {m["scenario"] for m in d1["test"]["metadata"]}
        if scenarios != SCENARIOS:
            raise AssertionError(f"{case}: expected scenarios {SCENARIOS}, got {scenarios}")
        for block in ("calibration", "validation", "test"):
            for key, value in d1[block].items():
                if key != "metadata" and not np.all(np.isfinite(value)):
                    raise AssertionError(f"{case}/{block}/{key}: non-finite value")
        print(f"PASS {case}: canonical topology, AC nominal state, seeded synthetic scenarios")

    print("CURRENT PIPELINE VALIDATION: PASS")


if __name__ == "__main__":
    main()
