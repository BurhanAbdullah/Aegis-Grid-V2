#!/usr/bin/env python3
"""Independent physical validation using canonical PYPOWER IEEE cases.

This script intentionally does not trust XMON-Grid's case loader. It loads the
canonical IEEE 9/14/30/118 cases from PYPOWER, runs AC power flow, checks
physical operating ranges and power balance, then independently checks the
analytic h(x) Jacobian implementation by finite differences.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Allow direct execution as `python validation/real_physical_validation.py`
# from a clean checkout, matching the CI invocation.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from pypower.api import runpf
from pypower.ppoption import ppoption
from pypower.idx_bus import VM, VA, PD, QD
from pypower.idx_gen import PG, QG
from pypower.idx_brch import F_BUS, T_BUS, BR_R, BR_X, BR_B, TAP, SHIFT, BR_STATUS

from core.grid_topology import compute_h_x, compute_jacobian_H, get_ieee_case_data

CASES = ["case9", "case14", "case30", "case118"]


def load_pypower_case(name: str):
    mod = importlib.import_module(f"pypower.{name}")
    return getattr(mod, name)()


def canonical_ybus(ppc):
    """Build Ybus directly from canonical branch data, including tap/phase shift."""
    nb = ppc["bus"].shape[0]
    Y = np.zeros((nb, nb), dtype=complex)
    for row in ppc["branch"]:
        if row[BR_STATUS] == 0:
            continue
        f = int(row[F_BUS]) - 1
        t = int(row[T_BUS]) - 1
        z = complex(row[BR_R], row[BR_X])
        ys = 1.0 / z
        bc = 1j * row[BR_B]
        tap = row[TAP] if row[TAP] != 0 else 1.0
        shift = np.deg2rad(row[SHIFT])
        tr = tap * np.exp(1j * shift)
        Y[f, f] += (ys + bc / 2) / (tr * np.conj(tr))
        Y[t, t] += ys + bc / 2
        Y[f, t] -= ys / np.conj(tr)
        Y[t, f] -= ys / tr
    return Y


def max_fd_jacobian_error(x, G, B):
    H = compute_jacobian_H(x, G, B)
    fd = np.zeros_like(H)
    eps = 1e-6
    for k in range(len(x)):
        xp = x.copy(); xm = x.copy()
        xp[k] += eps; xm[k] -= eps
        fd[:, k] = (compute_h_x(xp, G, B) - compute_h_x(xm, G, B)) / (2 * eps)
    return float(np.max(np.abs(H - fd))), float(np.linalg.norm(H - fd) / max(np.linalg.norm(fd), 1e-12))


def run_case(name):
    ppc = load_pypower_case(name)
    opts = ppoption(VERBOSE=0, OUT_ALL=0, PF_ALG=1)
    solved, success = runpf(ppc, opts)
    assert success, f"{name}: canonical AC power flow did not converge"

    bus = solved["bus"]
    vm = bus[:, VM]
    va = bus[:, VA]
    assert np.all(np.isfinite(vm)) and np.all(np.isfinite(va))
    assert float(vm.min()) > 0.80 and float(vm.max()) < 1.20, (name, vm.min(), vm.max())

    # Canonical system power balance: generation - load - branch losses ~= 0.
    total_pg = float(np.sum(solved["gen"][:, PG]))
    total_qg = float(np.sum(solved["gen"][:, QG]))
    total_pd = float(np.sum(bus[:, PD]))
    total_qd = float(np.sum(bus[:, QD]))
    pf = solved["branch"]
    p_loss = float(np.sum(pf[:, 13] + pf[:, 15]))
    q_loss = float(np.sum(pf[:, 14] + pf[:, 16]))
    assert abs(total_pg - total_pd - p_loss) < 1e-6, (name, total_pg, total_pd, p_loss)
    assert abs(total_qg - total_qd - q_loss) < 1e-6, (name, total_qg, total_qd, q_loss)

    Y = canonical_ybus(solved)
    G, B = Y.real, Y.imag
    N = len(bus)
    # Use solved physical state; reference angle is bus 1 in the canonical cases.
    x = np.concatenate([np.deg2rad(va[1:]), vm])
    err_abs, err_rel = max_fd_jacobian_error(x, G, B)
    assert err_abs < 2e-5, (name, err_abs, err_rel)

    # Compare repository loader against canonical case dimensions/topology.
    repo = get_ieee_case_data(name)
    canonical_branch_count = int(np.sum(solved["branch"][:, BR_STATUS] != 0))
    topology_match = repo["num_buses"] == N and repo["num_branches"] == canonical_branch_count

    print(f"{name}: PF=PASS Vm=[{vm.min():.5f},{vm.max():.5f}] "
          f"Pbalance={total_pg-total_pd-p_loss:+.2e} "
          f"Qbalance={total_qg-total_qd-q_loss:+.2e} "
          f"Jacobian maxerr={err_abs:.2e} relerr={err_rel:.2e} "
          f"repo_topology_match={topology_match}")
    return topology_match


def main():
    mismatches = []
    for name in CASES:
        if not run_case(name):
            mismatches.append(name)
    if mismatches:
        print("TOPOLOGY MISMATCHES:", ", ".join(mismatches))
        print("The canonical physical validation passed, but XMON-Grid's internal case loader is not yet canonical.")
        return 2
    print("ALL CANONICAL PHYSICAL AND JACOBIAN CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
