#!/usr/bin/env python3
"""Canonical IEEE benchmark data generation for XMON-Grid.

The network topology and electrical parameters come from the standard PYPOWER
IEEE cases.  The measurements and attack realizations are synthetic, seeded,
and generated from the canonical AC measurement equation.  This distinction
is intentional: the repository does not claim to contain field SCADA data.
"""

from collections import deque
from typing import Any, Dict, Tuple
from importlib import import_module

import numpy as np

from core.grid_topology import get_ieee_case_data, build_ybus, compute_h_x

SEVERITY_TIERS = [
    "Tier 1 (Subtle)",
    "Tier 2 (Moderate)",
    "Tier 3 (Strong)",
    "Tier 4 (Severe)",
]
CASE_MODULES = {name: f"pypower.{name}" for name in ("case9", "case14", "case30", "case118")}


def _nominal_state(case_name: str) -> np.ndarray:
    """Solve the canonical AC power flow and return x=[theta_2..theta_N,V_1..V_N]."""
    if case_name not in CASE_MODULES:
        raise ValueError(f"Unsupported IEEE case: {case_name}")
    from pypower.api import ppoption, runpf

    module = import_module(CASE_MODULES[case_name])
    mpc = getattr(module, case_name)()
    ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
    solved, success = runpf(mpc, ppopt)
    if not success:
        raise RuntimeError(f"PYPOWER AC power flow failed for {case_name}")

    bus = np.asarray(solved["bus"], dtype=float)
    va = np.deg2rad(bus[:, 8])
    vm = bus[:, 7]
    return np.concatenate([va[1:], vm])


def _connected_after_removal(branch: np.ndarray, nbus: int, remove_idx: int) -> bool:
    """Return True when removing one active branch leaves the bus graph connected."""
    adjacency = [[] for _ in range(nbus)]
    for idx, row in enumerate(branch):
        if idx == remove_idx or row[10] == 0:
            continue
        f, t = int(row[0]) - 1, int(row[1]) - 1
        adjacency[f].append(t)
        adjacency[t].append(f)

    seen = {0}
    queue = deque([0])
    while queue:
        node = queue.popleft()
        for nxt in adjacency[node]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return len(seen) == nbus


def _select_outage_branch(case_data: Dict[str, Any]) -> Tuple[int, int, int]:
    """Choose the first active non-islanding branch deterministically."""
    branch = np.asarray(case_data["branch"], dtype=float)
    nbus = int(case_data["num_buses"])
    for idx, row in enumerate(branch):
        if row[10] != 0 and _connected_after_removal(branch, nbus, idx):
            return idx, int(row[0]), int(row[1])
    raise RuntimeError(f"No non-islanding branch outage available for {case_data['case_name']}")


def generate_physical_dataset(
    case_name: str = "case9",
    num_calibration: int = 200,
    num_validation: int = 100,
    num_test_per_scenario: int = 60,
    seed: int = 42,
) -> Dict[str, Any]:
    """Generate deterministic synthetic measurements on canonical IEEE cases.

    The benchmark topology/electrical parameters are canonical PYPOWER cases;
    noise and attack realizations are synthetic.  Calibration is benign-only.
    """
    rng = np.random.RandomState(seed)
    case_data = get_ieee_case_data(case_name)
    _, G, B = build_ybus(case_data)
    n = int(case_data["num_buses"])
    meas_dim = 3 * n
    x_nominal = _nominal_state(case_name)

    outage_idx, outage_from, outage_to = _select_outage_branch(case_data)
    outage_case = {
        **case_data,
        "branch": np.asarray(case_data["branch"], dtype=float).copy(),
    }
    outage_case["branch"][outage_idx, 10] = 0.0
    _, G_out, B_out = build_ybus(outage_case)

    def noise_vector() -> np.ndarray:
        return np.concatenate([
            rng.normal(0.0, 0.002, size=n),
            rng.normal(0.0, 0.005, size=2 * n),
        ])

    def sample_measurement(attack_type: str = "baseline", tier: str = "Tier 0 (Benign)"):
        x_state = x_nominal.copy()
        delta_t = max(0.0001, float(rng.normal(0.004, 0.0005)))
        magnitude = 0.0
        snr_est = 0.0
        model_note = "canonical IEEE topology + synthetic noise"
        G_use, B_use = G, B

        if attack_type == "baseline":
            x_state[: n - 1] += rng.normal(0, 0.001, size=n - 1)
            x_state[n - 1 :] += rng.normal(0, 0.002, size=n)
            tier_name = "Tier 0 (Benign)"

        elif attack_type == "branch_outage":
            # True topology change: disable an actual canonical branch rather
            # than zeroing arbitrary off-diagonal Ybus entries.
            G_use, B_use = G_out, B_out
            tier_scale = {
                "Tier 1 (Subtle)": (0.0015, 0.0025, 0.0025, 1.25),
                "Tier 2 (Moderate)": (0.0030, 0.0050, 0.0050, 2.50),
                "Tier 3 (Strong)": (0.0050, 0.0080, 0.0080, 4.00),
                "Tier 4 (Severe)": (0.0080, 0.0120, 0.0120, 6.00),
            }[tier]
            sa, sv, magnitude, snr_est = tier_scale
            x_state[: n - 1] += rng.normal(0, sa, size=n - 1)
            x_state[n - 1 :] += rng.normal(0, sv, size=n)
            tier_name = tier
            model_note = f"canonical branch outage {outage_from}-{outage_to}"

        elif attack_type == "fdia":
            ranges = {
                "Tier 1 (Subtle)": ((0.002, 0.004), (0.005, 0.010)),
                "Tier 2 (Moderate)": ((0.006, 0.010), (0.015, 0.025)),
                "Tier 3 (Strong)": ((0.012, 0.018), (0.030, 0.045)),
                "Tier 4 (Severe)": ((0.030, 0.030), (0.050, 0.050)),
            }[tier]
            v_off = float(rng.uniform(*ranges[0]))
            pq_off = float(rng.uniform(*ranges[1]))
            magnitude, snr_est = v_off, v_off / 0.002
            h_clean = compute_h_x(x_state, G_use, B_use)
            attack = np.zeros(meas_dim)
            attack[:n] = v_off
            attack[n:2 * n] = pq_off
            return h_clean + attack + noise_vector(), delta_t, {
                "attack_type": attack_type, "severity_tier": tier,
                "attack_magnitude": round(magnitude, 6), "snr_estimate": round(snr_est, 2),
                "model_note": "synthetic additive FDIA; not a field trace",
            }

        elif attack_type == "load_shift":
            drops = {
                "Tier 1 (Subtle)": (0.005, 0.010),
                "Tier 2 (Moderate)": (0.015, 0.025),
                "Tier 3 (Strong)": (0.030, 0.040),
                "Tier 4 (Severe)": (0.050, 0.050),
            }[tier]
            drop = float(rng.uniform(*drops))
            magnitude, snr_est = drop, drop / 0.004
            x_state[n - 1 :] *= 1.0 - drop
            tier_name = tier
            model_note = "synthetic load-equivalent voltage perturbation"

        elif attack_type == "stealth_drift":
            drifts = {
                "Tier 1 (Subtle)": (0.002, 0.005),
                "Tier 2 (Moderate)": (0.008, 0.014),
                "Tier 3 (Strong)": (0.016, 0.024),
                "Tier 4 (Severe)": (0.025, 0.035),
            }[tier]
            drift = float(rng.uniform(*drifts))
            magnitude, snr_est = drift, drift / 0.002
            x_state[n - 1 :] += drift
            tier_name = tier
            model_note = "synthetic slow state drift"
            if rng.rand() < 0.2:
                delta_t = max(0.0001, float(rng.normal(0.006, 0.0015)))

        else:
            raise ValueError(f"Unknown attack type: {attack_type}")

        h_clean = compute_h_x(x_state, G_use, B_use)
        return h_clean + noise_vector(), delta_t, {
            "attack_type": attack_type,
            "severity_tier": tier_name,
            "attack_magnitude": round(magnitude, 6),
            "snr_estimate": round(snr_est, 2),
            "model_note": model_note,
        }

    calib_z, calib_iat = [], []
    for _ in range(num_calibration):
        z, dt, _ = sample_measurement("baseline")
        calib_z.append(z); calib_iat.append(dt)

    val_z, val_iat, val_labels = [], [], []
    for _ in range(num_validation // 2):
        z, dt, _ = sample_measurement("baseline")
        val_z.append(z); val_iat.append(dt); val_labels.append(0)
    attack_order = ["fdia", "load_shift", "stealth_drift", "branch_outage"]
    for idx in range(num_validation // 2):
        tier = SEVERITY_TIERS[idx % 4]
        z, dt, _ = sample_measurement(attack_order[idx % 4], tier)
        val_z.append(z); val_iat.append(dt); val_labels.append(1)

    test_z, test_iat, test_labels, test_metadata = [], [], [], []
    scenarios = ["baseline", "branch_outage", "fdia", "load_shift", "stealth_drift"]
    for scenario in scenarios:
        label = 0 if scenario == "baseline" else 1
        for i in range(num_test_per_scenario):
            tier = "Tier 0 (Benign)" if scenario == "baseline" else SEVERITY_TIERS[i % 4]
            z, dt, meta = sample_measurement(scenario, tier)
            test_z.append(z); test_iat.append(dt); test_labels.append(label)
            test_metadata.append({
                "case": case_name, "scenario": scenario,
                "severity_tier": meta["severity_tier"],
                "attack_magnitude": meta["attack_magnitude"],
                "snr_estimate": meta["snr_estimate"],
                "model_note": meta["model_note"],
                "sample_idx": i,
                "outage_from": outage_from if scenario == "branch_outage" else None,
                "outage_to": outage_to if scenario == "branch_outage" else None,
            })

    return {
        "case_name": case_name,
        "benchmark_provenance": "canonical PYPOWER IEEE topology; synthetic seeded measurements/attacks",
        "calibration": {"z": np.asarray(calib_z), "iat": np.asarray(calib_iat)},
        "validation": {"z": np.asarray(val_z), "iat": np.asarray(val_iat), "labels": np.asarray(val_labels)},
        "test": {"z": np.asarray(test_z), "iat": np.asarray(test_iat), "labels": np.asarray(test_labels), "metadata": test_metadata},
    }
