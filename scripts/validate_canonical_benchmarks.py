#!/usr/bin/env python3
"""Validate canonical PYPOWER/MATPOWER benchmark definitions and Ybus math."""

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.grid_topology import get_ieee_case_data, build_ybus

EXPECTED = {"case9": (9, 9), "case14": (14, 20), "case30": (30, 41), "case118": (118, 186)}


def main() -> int:
    failures = []
    for case_name, (expected_buses, expected_branches) in EXPECTED.items():
        case = get_ieee_case_data(case_name)
        nbus, nbranch = case["num_buses"], case["num_branches"]
        if (nbus, nbranch) != (expected_buses, expected_branches):
            failures.append(f"{case_name}: expected {expected_buses}/{expected_branches}, got {nbus}/{nbranch}")
        if case["source"] != "PYPOWER/MATPOWER standard case definition":
            failures.append(f"{case_name}: non-canonical source marker")
        if not np.array_equal(np.asarray(case["bus"])[:, 0].astype(int), np.arange(1, nbus + 1)):
            failures.append(f"{case_name}: unexpected external bus numbering")

        try:
            from pypower.makeYbus import makeYbus
            bus_ref = np.asarray(case["bus"], dtype=float).copy()
            branch_ref = np.asarray(case["branch"], dtype=float).copy()
            # PYPOWER 5.1.19's low-level makeYbus expects internal 0..N-1 IDs.
            bus_ref[:, 0] = np.arange(nbus, dtype=float)
            branch_ref[:, 0] = branch_ref[:, 0] - 1.0
            branch_ref[:, 1] = branch_ref[:, 1] - 1.0
            if np.any(branch_ref[:, :2] < 0) or np.any(branch_ref[:, :2] >= nbus):
                raise ValueError("internal branch endpoint outside 0..N-1")
            y_ref, _, _ = makeYbus(float(case["baseMVA"]), bus_ref, branch_ref)
            y_local, _, _ = build_ybus(case)
            err = float(np.max(np.abs(y_local - y_ref.toarray())))
            if err > 1e-12:
                failures.append(f"{case_name}: Ybus mismatch vs PYPOWER makeYbus: {err:.3e}")
        except Exception as exc:
            failures.append(f"{case_name}: PYPOWER Ybus cross-check failed: {exc}")

        print(f"PASS {case_name}: buses={nbus}, branches={nbranch}, baseMVA={case['baseMVA']:.1f}")

    if failures:
        print("\nCANONICAL BENCHMARK VALIDATION: FAIL")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("\nCANONICAL BENCHMARK VALIDATION: PASS")
    print("All four benchmark definitions and local Ybus construction match PYPOWER.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
