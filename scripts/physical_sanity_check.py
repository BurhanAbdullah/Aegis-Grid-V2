#!/usr/bin/env python3
"""Independent physical consistency audit of the canonical AC network model."""
from pathlib import Path
import sys
import csv
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.grid_topology import get_ieee_case_data, build_ybus, compute_h_x


def solve_state(case_name):
    from pypower.api import ppoption, runpf
    module = __import__(f"pypower.{case_name}", fromlist=[case_name])
    mpc = getattr(module, case_name)()
    solved, success = runpf(mpc, ppoption(VERBOSE=0, OUT_ALL=0))
    if not success:
        raise RuntimeError(f"AC power flow failed for {case_name}")
    bus = np.asarray(solved["bus"], dtype=float)
    va = np.deg2rad(bus[:, 8])
    vm = bus[:, 7]
    return np.concatenate([va[1:], vm]), vm * np.exp(1j * va)


def audit_case(case_name):
    case = get_ieee_case_data(case_name)
    Ybus, G, B = build_ybus(case)
    x, V = solve_state(case_name)

    # Cross-check the repository measurement equation against the independently
    # assembled complex-power injection equation S = V * conj(YV).
    S_bus = V * np.conj(Ybus @ V)
    h = compute_h_x(x, G, B)
    n = case["num_buses"]
    h_p_err = float(np.max(np.abs(h[n:2 * n] - S_bus.real)))
    h_q_err = float(np.max(np.abs(h[2 * n:] - S_bus.imag)))

    # Independent branch-end power calculation.  Include both series current
    # and half-line charging susceptance, and retain transformer tap/phase shift.
    bus = np.asarray(case["bus"], dtype=float)
    p_shunt = float(np.sum(bus[:, 4] / case["baseMVA"] * np.abs(V) ** 2))
    p_branch_loss = 0.0
    active_branches = 0
    for row in np.asarray(case["branch"], dtype=float):
        if row[10] == 0:
            continue
        active_branches += 1
        f = int(round(row[0])) - 1
        t = int(round(row[1])) - 1
        z = complex(row[2], row[3])
        y = 1.0 / z
        b_shunt = complex(0.0, row[4])
        ratio = float(row[8]) or 1.0
        tap = ratio * np.exp(1j * np.deg2rad(float(row[9])))

        Vf_tapped = V[f] / tap
        Ift = (Vf_tapped - V[t]) * y + (b_shunt / 2.0) * Vf_tapped
        Itf = (V[t] - Vf_tapped) * y + (b_shunt / 2.0) * V[t]
        Sft = Vf_tapped * np.conj(Ift)
        Stf = V[t] * np.conj(Itf)
        p_branch_loss += float(np.real(Sft + Stf))

    residual = float(np.sum(S_bus.real) - p_branch_loss - p_shunt)
    return {
        "case": case_name,
        "buses": n,
        "branches": active_branches,
        "h_p_max_abs_error": h_p_err,
        "h_q_max_abs_error": h_q_err,
        "power_balance_residual": residual,
        "converged": True,
    }


def main():
    rows = [audit_case(c) for c in ("case9", "case14", "case30", "case118")]
    for r in rows:
        msg = (
            f"{r['case']}: hP={r['h_p_max_abs_error']:.3e}, "
            f"hQ={r['h_q_max_abs_error']:.3e}, "
            f"balance={r['power_balance_residual']:.3e}"
        )
        print(msg)
        if (
            r["h_p_max_abs_error"] > 1e-10
            or r["h_q_max_abs_error"] > 1e-10
            or abs(r["power_balance_residual"]) > 1e-9
        ):
            raise SystemExit(f"PHYSICAL SANITY CHECK FAILED: {r['case']}")

    out = ROOT / "results" / "current_physical_sanity.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("PHYSICAL MODEL SANITY CHECK: PASS")


if __name__ == "__main__":
    main()
