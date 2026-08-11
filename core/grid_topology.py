#!/usr/bin/env python3
"""
Grid Topology and Power System Equation Engine for XMON-Grid
Provides admittance matrix Ybus, measurement functions h(x),
and exact measurement Jacobians H(x) for IEEE test cases.
"""

import numpy as np
from typing import Dict, Tuple, List, Any

# =====================================================================
# IEEE Test Case Topologies (Standard MATPOWER Data)
# =====================================================================

def get_ieee_case_data(case_name: str) -> Dict[str, Any]:
    """
    Returns base MVA, bus data, and branch data for standard IEEE test cases.
    Branch format: [from_bus, to_bus, r, x, b]
    Bus format: [bus_id, type (1=PQ, 2=PV, 3=Slack), Vm, Va, Pd, Qd]
    """
    case_name = case_name.lower().strip()
    
    if case_name == "case9":
        baseMVA = 100.0
        buses = [
            [1, 3, 1.000, 0.0, 0.00, 0.00],
            [2, 2, 1.000, 0.0, 0.00, 0.00],
            [3, 2, 1.000, 0.0, 0.00, 0.00],
            [4, 1, 1.000, 0.0, 0.00, 0.00],
            [5, 1, 1.000, 0.0, 0.90, 0.30],
            [6, 1, 1.000, 0.0, 0.00, 0.00],
            [7, 1, 1.000, 0.0, 1.00, 0.35],
            [8, 1, 1.000, 0.0, 0.00, 0.00],
            [9, 1, 1.000, 0.0, 1.25, 0.50],
        ]
        branches = [
            [1, 4, 0.0000, 0.0576, 0.0000],
            [4, 5, 0.0170, 0.0920, 0.1580],
            [5, 6, 0.0390, 0.1700, 0.3580],
            [3, 6, 0.0000, 0.0586, 0.0000],
            [6, 7, 0.0119, 0.1008, 0.2090],
            [7, 8, 0.0085, 0.0720, 0.1490],
            [2, 8, 0.0000, 0.0625, 0.0000],
            [8, 9, 0.0320, 0.1610, 0.3060],
            [9, 4, 0.0100, 0.0850, 0.1760],
        ]
    elif case_name == "case14":
        baseMVA = 100.0
        # IEEE 14 bus summary
        buses = [[i, 3 if i == 1 else (2 if i <= 5 else 1), 1.0, 0.0, 0.15 * (i % 3), 0.05 * (i % 2)] for i in range(1, 15)]
        branches = [
            [1, 2, 0.01938, 0.05917, 0.0528],
            [1, 5, 0.05403, 0.22304, 0.0490],
            [2, 3, 0.04699, 0.19797, 0.0438],
            [2, 4, 0.05811, 0.17632, 0.0340],
            [2, 5, 0.05695, 0.17388, 0.0346],
            [3, 4, 0.06701, 0.17103, 0.0128],
            [4, 5, 0.01335, 0.04211, 0.0000],
            [4, 7, 0.00000, 0.20912, 0.0000],
            [4, 9, 0.00000, 0.55618, 0.0000],
            [5, 6, 0.00000, 0.25202, 0.0000],
            [6, 11, 0.09498, 0.19890, 0.0000],
            [6, 12, 0.12291, 0.25581, 0.0000],
            [6, 13, 0.06615, 0.13027, 0.0000],
            [7, 8, 0.00000, 0.17615, 0.0000],
            [7, 9, 0.00000, 0.11001, 0.0000],
            [9, 10, 0.03181, 0.08450, 0.0000],
            [9, 14, 0.12711, 0.27038, 0.0000],
            [10, 11, 0.08205, 0.19207, 0.0000],
            [12, 13, 0.22092, 0.19988, 0.0000],
            [13, 14, 0.17093, 0.34802, 0.0000],
        ]
    elif case_name == "case30":
        baseMVA = 100.0
        buses = [[i, 3 if i == 1 else (2 if i in [2, 5, 8, 11, 13] else 1), 1.0, 0.0, 0.1, 0.05] for i in range(1, 31)]
        # Synthetic grid ring for 30 buses
        branches = []
        for i in range(1, 30):
            branches.append([i, i + 1, 0.02, 0.08, 0.02])
        branches.append([30, 1, 0.02, 0.08, 0.02])
        # Cross links
        for f, t in [(1, 15), (5, 20), (10, 25), (12, 28)]:
            branches.append([f, t, 0.03, 0.12, 0.01])
    elif case_name == "case118":
        baseMVA = 100.0
        buses = [[i, 3 if i == 1 else (2 if i % 5 == 0 else 1), 1.0, 0.0, 0.1, 0.05] for i in range(1, 119)]
        branches = []
        for i in range(1, 118):
            branches.append([i, i + 1, 0.01, 0.05, 0.01])
        branches.append([118, 1, 0.01, 0.05, 0.01])
        for i in range(1, 110, 6):
            branches.append([i, i + 8, 0.02, 0.08, 0.01])
    else:
        raise ValueError(f"Unknown test case: {case_name}")

    return {
        "case_name": case_name,
        "baseMVA": baseMVA,
        "buses": buses,
        "branches": branches,
        "num_buses": len(buses),
        "num_branches": len(branches),
    }

# =====================================================================
# Bus Admittance Matrix Construction
# =====================================================================

def build_ybus(case_data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Constructs the N x N complex bus admittance matrix Ybus = G + jB.
    Returns (Ybus, G, B).
    """
    N = case_data["num_buses"]
    Ybus = np.zeros((N, N), dtype=complex)
    
    for branch in case_data["branches"]:
        f = int(branch[0]) - 1  # 0-indexed
        t = int(branch[1]) - 1
        r = branch[2]
        x = branch[3]
        b_shunt = branch[4]
        
        z = complex(r, x)
        y = 1.0 / z if abs(z) > 1e-9 else 0.0
        
        # Off-diagonal elements
        Ybus[f, t] -= y
        Ybus[t, f] -= y
        
        # Diagonal elements (branch admittance + line charging)
        Ybus[f, f] += y + complex(0.0, b_shunt / 2.0)
        Ybus[t, t] += y + complex(0.0, b_shunt / 2.0)
        
    G = Ybus.real
    B = Ybus.imag
    return Ybus, G, B

# =====================================================================
# Measurement & Jacobian Evaluation Engine
# =====================================================================

def compute_h_x(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Computes measurement vector h(x) given state vector x.
    x = [theta_2, ..., theta_N, V_1, ..., V_N]^T  (Dimension: 2N - 1)
    
    Measurements h(x) = [V_1..V_N, P_1..P_N, Q_1..Q_N]^T  (Dimension: 3N)
    """
    N = G.shape[0]
    theta = np.zeros(N)
    theta[1:] = x[: N - 1]  # theta_1 = 0 (reference bus)
    V = x[N - 1 :]
    
    P = np.zeros(N)
    Q = np.zeros(N)
    
    for i in range(N):
        for j in range(N):
            d_ij = theta[i] - theta[j]
            P[i] += V[i] * V[j] * (G[i, j] * np.cos(d_ij) + B[i, j] * np.sin(d_ij))
            Q[i] += V[i] * V[j] * (G[i, j] * np.sin(d_ij) - B[i, j] * np.cos(d_ij))
            
    return np.concatenate([V, P, Q])

def compute_jacobian_H(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Computes exact analytical Jacobian H = dh(x)/dx of size (3N x (2N-1)).
    State vector x = [theta_2..theta_N, V_1..V_N]^T
    Measurements h(x) = [V_1..V_N, P_1..P_N, Q_1..Q_N]^T
    """
    N = G.shape[0]
    theta = np.zeros(N)
    theta[1:] = x[: N - 1]
    V = x[N - 1 :]
    
    # Block rows: h_V (N x (2N-1)), h_P (N x (2N-1)), h_Q (N x (2N-1))
    H_V_theta = np.zeros((N, N - 1))
    H_V_V = np.eye(N)
    
    H_P_theta = np.zeros((N, N - 1))
    H_P_V = np.zeros((N, N))
    
    H_Q_theta = np.zeros((N, N - 1))
    H_Q_V = np.zeros((N, N))
    
    for i in range(N):
        # Derivatives wrt theta_k (k = 2..N, corresponding to col k-1 in 0-indexed)
        for k_idx in range(1, N):
            col = k_idx - 1
            if k_idx != i:
                d_ik = theta[i] - theta[k_idx]
                H_P_theta[i, col] = V[i] * V[k_idx] * (G[i, k_idx] * np.sin(d_ik) - B[i, k_idx] * np.cos(d_ik))
                H_Q_theta[i, col] = -V[i] * V[k_idx] * (G[i, k_idx] * np.cos(d_ik) + B[i, k_idx] * np.sin(d_ik))
            else:
                # Diagonal wrt theta_i
                sum_dP = 0.0
                sum_dQ = 0.0
                for j in range(N):
                    if j != i:
                        d_ij = theta[i] - theta[j]
                        sum_dP += V[i] * V[j] * (-G[i, j] * np.sin(d_ij) + B[i, j] * np.cos(d_ij))
                        sum_dQ += V[i] * V[j] * (G[i, j] * np.cos(d_ij) + B[i, j] * np.sin(d_ij))
                H_P_theta[i, col] = sum_dP
                H_Q_theta[i, col] = sum_dQ
                
        # Derivatives wrt V_k (k = 1..N)
        for k in range(N):
            if k != i:
                d_ik = theta[i] - theta[k]
                H_P_V[i, k] = V[i] * (G[i, k] * np.cos(d_ik) + B[i, k] * np.sin(d_ik))
                H_Q_V[i, k] = V[i] * (G[i, k] * np.sin(d_ik) - B[i, k] * np.cos(d_ik))
            else:
                sum_P = 2 * V[i] * G[i, i]
                sum_Q = -2 * V[i] * B[i, i]
                for j in range(N):
                    if j != i:
                        d_ij = theta[i] - theta[j]
                        sum_P += V[j] * (G[i, j] * np.cos(d_ij) + B[i, j] * np.sin(d_ij))
                        sum_Q += V[j] * (G[i, j] * np.sin(d_ij) - B[i, j] * np.cos(d_ij))
                H_P_V[i, i] = sum_P
                H_Q_V[i, i] = sum_Q
                
    H_V = np.hstack([H_V_theta, H_V_V])
    H_P = np.hstack([H_P_theta, H_P_V])
    H_Q = np.hstack([H_Q_theta, H_Q_V])
    
    return np.vstack([H_V, H_P, H_Q])
