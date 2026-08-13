#!/usr/bin/env python3
"""Physical AC-grid topology and measurement/Jacobian engine.

The benchmark cases are loaded from canonical MATPOWER/PYPOWER data rather
than synthetic rings or fabricated bus loads. The internal representation is
kept deliberately small: buses carry the operating-point fields required by
XMON and branches retain resistance, reactance, charging, tap and phase shift.
"""

import importlib
import numpy as np
from typing import Dict, Tuple, Any


def _load_canonical_case(case_name: str) -> Dict[str, Any]:
    """Load a canonical MATPOWER case through the open-source PYPOWER package."""
    try:
        mod = importlib.import_module(f"pypower.{case_name}")
    except ImportError as exc:
        raise ImportError(
            "Canonical XMON cases require the open-source 'pypower' package. "
            "Install it with `pip install pypower`."
        ) from exc

    ppc = getattr(mod, case_name)()
    bus = ppc["bus"]
    branch = ppc["branch"]

    # MATPOWER/PYPOWER bus columns:
    # BUS_I, BUS_TYPE, PD, QD, GS, BS, AREA, VM, VA, BASE_KV, ZONE, VMAX, VMIN
    buses = [
        [
            int(row[0]), int(row[1]), float(row[7]), float(row[8]),
            float(row[2]) / float(ppc["baseMVA"]),
            float(row[3]) / float(ppc["baseMVA"]),
        ]
        for row in bus
    ]

    # Preserve transformer tap/phase shift. A branch is
    # [from, to, r, x, b, tap, shift_deg].
    branches = []
    for row in branch:
        if int(row[10]) == 0:  # BR_STATUS
            continue
        tap = float(row[8]) if abs(float(row[8])) > 1e-12 else 1.0
        branches.append([
            int(row[0]), int(row[1]), float(row[2]), float(row[3]),
            float(row[4]), tap, float(row[9])
        ])

    return {
        "case_name": case_name,
        "baseMVA": float(ppc["baseMVA"]),
        "buses": buses,
        "branches": branches,
        "num_buses": len(buses),
        "num_branches": len(branches),
    }


def get_ieee_case_data(case_name: str) -> Dict[str, Any]:
    """Return canonical IEEE/MATPOWER benchmark data for an XMON case."""
    case_name = case_name.lower().strip()
    if case_name not in {"case9", "case14", "case30", "case118"}:
        raise ValueError(f"Unknown test case: {case_name}")
    return _load_canonical_case(case_name)


def build_ybus(case_data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct Ybus including line charging and transformer tap/phase shift."""
    n = case_data["num_buses"]
    Ybus = np.zeros((n, n), dtype=complex)

    for branch in case_data["branches"]:
        f = int(branch[0]) - 1
        t = int(branch[1]) - 1
        r, x, b = map(float, branch[2:5])
        tap = float(branch[5]) if len(branch) > 5 else 1.0
        shift_deg = float(branch[6]) if len(branch) > 6 else 0.0
        if abs(tap) < 1e-12:
            tap = 1.0

        z = complex(r, x)
        ys = 1.0 / z if abs(z) > 1e-12 else 0.0
        ysh = 1j * b / 2.0
        tr = tap * np.exp(1j * np.deg2rad(shift_deg))

        Ybus[f, f] += (ys + ysh) / (tr * np.conj(tr))
        Ybus[t, t] += ys + ysh
        Ybus[f, t] -= ys / np.conj(tr)
        Ybus[t, f] -= ys / tr

    return Ybus, Ybus.real, Ybus.imag


def compute_h_x(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Evaluate h(x)=[V,P,Q] for x=[theta_2..theta_N,V_1..V_N]."""
    n = G.shape[0]
    theta = np.zeros(n)
    theta[1:] = x[: n - 1]
    V = x[n - 1 :]

    P = np.zeros(n)
    Q = np.zeros(n)
    for i in range(n):
        for j in range(n):
            d = theta[i] - theta[j]
            P[i] += V[i] * V[j] * (G[i, j] * np.cos(d) + B[i, j] * np.sin(d))
            Q[i] += V[i] * V[j] * (G[i, j] * np.sin(d) - B[i, j] * np.cos(d))
    return np.concatenate([V, P, Q])


def compute_jacobian_H(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Analytical Jacobian dh/dx for the full V/P/Q measurement vector."""
    n = G.shape[0]
    theta = np.zeros(n)
    theta[1:] = x[: n - 1]
    V = x[n - 1 :]

    HV_theta = np.zeros((n, n - 1))
    HV_V = np.eye(n)
    HP_theta = np.zeros((n, n - 1))
    HP_V = np.zeros((n, n))
    HQ_theta = np.zeros((n, n - 1))
    HQ_V = np.zeros((n, n))

    for i in range(n):
        for k in range(1, n):
            col = k - 1
            if k != i:
                d = theta[i] - theta[k]
                HP_theta[i, col] = V[i] * V[k] * (G[i, k] * np.sin(d) - B[i, k] * np.cos(d))
                HQ_theta[i, col] = -V[i] * V[k] * (G[i, k] * np.cos(d) + B[i, k] * np.sin(d))
            else:
                dp = dq = 0.0
                for j in range(n):
                    if j == i:
                        continue
                    d = theta[i] - theta[j]
                    dp += V[i] * V[j] * (-G[i, j] * np.sin(d) + B[i, j] * np.cos(d))
                    dq += V[i] * V[j] * (G[i, j] * np.cos(d) + B[i, j] * np.sin(d))
                HP_theta[i, col] = dp
                HQ_theta[i, col] = dq

        for k in range(n):
            if k != i:
                d = theta[i] - theta[k]
                HP_V[i, k] = V[i] * (G[i, k] * np.cos(d) + B[i, k] * np.sin(d))
                HQ_V[i, k] = V[i] * (G[i, k] * np.sin(d) - B[i, k] * np.cos(d))
            else:
                dp = 2.0 * V[i] * G[i, i]
                dq = -2.0 * V[i] * B[i, i]
                for j in range(n):
                    if j == i:
                        continue
                    d = theta[i] - theta[j]
                    dp += V[j] * (G[i, j] * np.cos(d) + B[i, j] * np.sin(d))
                    dq += V[j] * (G[i, j] * np.sin(d) - B[i, j] * np.cos(d))
                HP_V[i, i] = dp
                HQ_V[i, i] = dq

    return np.vstack([
        np.hstack([HV_theta, HV_V]),
        np.hstack([HP_theta, HP_V]),
        np.hstack([HQ_theta, HQ_V]),
    ])
