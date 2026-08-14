#!/usr/bin/env python3
"""
Grid topology and AC measurement equation engine for XMON-Grid.

The benchmark cases are loaded directly from the standard PYPOWER/MATPOWER
case definitions rather than synthetic approximations.  This keeps the
benchmark topology, bus loads, generator buses, line charging, transformer
taps, and phase shifts tied to a versioned external case definition.
"""

from importlib import import_module
from typing import Dict, Tuple, Any

import numpy as np

_CASE_MODULES = {
    "case9": "pypower.case9",
    "case14": "pypower.case14",
    "case30": "pypower.case30",
    "case118": "pypower.case118",
}


def get_ieee_case_data(case_name: str) -> Dict[str, Any]:
    """Return canonical IEEE benchmark data from PYPOWER case definitions.

    The returned dictionary retains the full MATPOWER bus/branch arrays so
    transformer ratios, phase shifts, shunts, and branch status are not lost.
    ``buses`` and ``branches`` are also provided as Python lists for backward
    compatibility with existing metadata/reporting code.
    """
    case_name = case_name.lower().strip()
    if case_name not in _CASE_MODULES:
        raise ValueError(f"Unknown test case: {case_name}. Supported: {sorted(_CASE_MODULES)}")

    module = import_module(_CASE_MODULES[case_name])
    loader = getattr(module, case_name)
    mpc = loader()

    bus = np.asarray(mpc["bus"], dtype=float)
    branch = np.asarray(mpc["branch"], dtype=float)
    base_mva = float(mpc["baseMVA"])

    if bus.ndim != 2 or bus.shape[1] < 13:
        raise ValueError(f"Invalid {case_name} bus matrix shape: {bus.shape}")
    if branch.ndim != 2 or branch.shape[1] < 13:
        raise ValueError(f"Invalid {case_name} branch matrix shape: {branch.shape}")

    return {
        "case_name": case_name,
        "source": "PYPOWER/MATPOWER standard case definition",
        "baseMVA": base_mva,
        "bus": bus,
        "branch": branch,
        "gen": np.asarray(mpc.get("gen", []), dtype=float),
        "gencost": np.asarray(mpc.get("gencost", []), dtype=float),
        "buses": bus.tolist(),
        "branches": branch.tolist(),
        "num_buses": int(bus.shape[0]),
        "num_branches": int(branch.shape[0]),
    }


def build_ybus(case_data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct the MATPOWER-compatible bus admittance matrix.

    Includes series admittance, line charging, transformer off-nominal tap,
    phase shift, branch status, and bus shunts.  All quantities are in p.u.
    on ``baseMVA``.
    """
    bus = np.asarray(case_data["bus"], dtype=float)
    branch = np.asarray(case_data["branch"], dtype=float)
    base_mva = float(case_data["baseMVA"])
    n = int(case_data["num_buses"])

    # MATPOWER column indices (zero-based).
    BUS_I, GS, BS = 0, 4, 5
    F_BUS, T_BUS, BR_R, BR_X, BR_B = 0, 1, 2, 3, 4
    TAP, SHIFT, BR_STATUS = 8, 9, 10

    ybus = np.zeros((n, n), dtype=complex)

    # Bus shunts are specified in MW/MVAr at V = 1 p.u.; convert to p.u.
    for row in bus:
        i = int(round(row[BUS_I])) - 1
        if not 0 <= i < n:
            raise ValueError(f"Invalid bus number {row[BUS_I]} in {case_data['case_name']}")
        ybus[i, i] += complex(row[GS], row[BS]) / base_mva

    for row in branch:
        if row[BR_STATUS] == 0:
            continue

        f = int(round(row[F_BUS])) - 1
        t = int(round(row[T_BUS])) - 1
        if not (0 <= f < n and 0 <= t < n):
            raise ValueError(f"Invalid branch endpoints {row[F_BUS]} -> {row[T_BUS]}")

        z = complex(row[BR_R], row[BR_X])
        if abs(z) <= 1e-15:
            raise ValueError(f"Zero branch impedance on {row[F_BUS]} -> {row[T_BUS]}")
        y = 1.0 / z
        b_shunt = complex(0.0, row[BR_B])

        ratio = float(row[TAP])
        if abs(ratio) <= 1e-15:
            ratio = 1.0
        shift = np.deg2rad(float(row[SHIFT]))
        tap = ratio * np.exp(1j * shift)

        yff = (y + b_shunt / 2.0) / (tap * np.conj(tap))
        yft = -y / np.conj(tap)
        ytf = -y / tap
        ytt = y + b_shunt / 2.0

        ybus[f, f] += yff
        ybus[f, t] += yft
        ybus[t, f] += ytf
        ybus[t, t] += ytt

    return ybus, ybus.real, ybus.imag


def compute_h_x(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Evaluate full AC measurement vector h(x) = [V, P, Q].

    State: x = [theta_2, ..., theta_N, V_1, ..., V_N].
    Reference-bus angle theta_1 is fixed to zero.
    """
    n = G.shape[0]
    x = np.asarray(x, dtype=float)
    if x.size != 2 * n - 1:
        raise ValueError(f"State dimension mismatch: expected {2*n-1}, got {x.size}")

    theta = np.zeros(n)
    theta[1:] = x[: n - 1]
    v = x[n - 1 :]

    d_ij = theta[:, None] - theta[None, :]
    cos_d = np.cos(d_ij)
    sin_d = np.sin(d_ij)

    p = v * np.sum(v[None, :] * (G * cos_d + B * sin_d), axis=1)
    q = v * np.sum(v[None, :] * (G * sin_d - B * cos_d), axis=1)
    return np.concatenate([v, p, q])


def compute_jacobian_H(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Evaluate the exact analytical Jacobian H = dh/dx."""
    n = G.shape[0]
    x = np.asarray(x, dtype=float)
    if x.size != 2 * n - 1:
        raise ValueError(f"State dimension mismatch: expected {2*n-1}, got {x.size}")

    theta = np.zeros(n)
    theta[1:] = x[: n - 1]
    v = x[n - 1 :]

    d_ij = theta[:, None] - theta[None, :]
    cos_d = np.cos(d_ij)
    sin_d = np.sin(d_ij)
    v_outer = v[:, None] * v[None, :]

    h_v_theta = np.zeros((n, n - 1))
    h_v_v = np.eye(n)

    m_p_theta = v_outer * (G * sin_d - B * cos_d)
    np.fill_diagonal(m_p_theta, 0.0)
    np.fill_diagonal(m_p_theta, -np.sum(m_p_theta, axis=1))
    h_p_theta = m_p_theta[:, 1:]

    m_q_theta = -v_outer * (G * cos_d + B * sin_d)
    np.fill_diagonal(m_q_theta, 0.0)
    np.fill_diagonal(m_q_theta, -np.sum(m_q_theta, axis=1))
    h_q_theta = m_q_theta[:, 1:]

    h_p_v = v[:, None] * (G * cos_d + B * sin_d)
    np.fill_diagonal(h_p_v, 0.0)
    np.fill_diagonal(h_p_v, 2.0 * v * np.diag(G) + np.sum(h_p_v, axis=1))

    h_q_v = v[:, None] * (G * sin_d - B * cos_d)
    np.fill_diagonal(h_q_v, 0.0)
    np.fill_diagonal(h_q_v, -2.0 * v * np.diag(B) + np.sum(h_q_v, axis=1))

    h_v = np.hstack([h_v_theta, h_v_v])
    h_p = np.hstack([h_p_theta, h_p_v])
    h_q = np.hstack([h_q_theta, h_q_v])
    return np.vstack([h_v, h_p, h_q])
