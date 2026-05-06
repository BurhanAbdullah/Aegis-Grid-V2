import sys
import os
import csv
import random
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from matpower_voltage_parser import run_with_voltages
from v3_fabric.core.jitter_detector import JitterDetector
from v4_hive.core.hive_consensus import HiveConsensus

# --------------------------------------------------
# Lightweight local detectors
# --------------------------------------------------

class KalmanAnomalyDetector:
    def __init__(self, threshold=0.02):
        self.threshold = threshold

    def update(self, z):
        residual = float(np.mean(np.abs(np.array(z) - 1.0)))
        detected = residual > self.threshold
        return {
            "residual": residual,
            "detected": detected
        }


class CUSUMDetector:
    def __init__(self, threshold=0.05):
        self.threshold = threshold
        self.g = 0.0

    def update(self, x):
        self.g = max(0.0, self.g + x)
        detected = self.g > self.threshold
        return {
            "score": self.g,
            "detected": detected
        }


# --------------------------------------------------
# Experiment setup
# --------------------------------------------------

CASES = ["case9", "case14", "case30", "case118"]

ATTACKS = {
    "baseline": "",

    "branch1_out":
        "mpc.branch(1, BR_STATUS) = 0;",

    "branch2_out":
        "mpc.branch(2, BR_STATUS) = 0;",

    "branch3_out":
        "mpc.branch(3, BR_STATUS) = 0;",

    "impedance_perturb":
        "mpc.branch(1, BR_X) = mpc.branch(1, BR_X) * 1.25;",

    "load_shift":
        "mpc.bus(:, PD) = mpc.bus(:, PD) * 1.15;",

    "voltage_drift":
        "mpc.gen(:, VG) = mpc.gen(:, VG) * 1.03;"
}

os.makedirs("experiments/results", exist_ok=True)

rows = []

print("\n" + "=" * 72)
print("  MACPR Full Experiment Pipeline")
print("=" * 72)

# --------------------------------------------------
# Main loop
# --------------------------------------------------

for case in CASES:

    print(f"\n--- {case} ---")

    rng = random.Random(42)

    base = run_with_voltages(case)

    if not base["success"]:
        print("MATPOWER failed for", case)
        continue

    nominal_v = base["voltages"]

    for attack_name, attack_code in ATTACKS.items():

        print(f"  -> {attack_name}")

        result = run_with_voltages(case, attack_code)

        if not result["success"]:
            print("     power flow failed")
            continue

        voltages = result["voltages"]

        # ------------------------------------------
        # Kalman residual detector
        # ------------------------------------------

        kalman = KalmanAnomalyDetector()

        k_out = kalman.update(voltages)

        # ------------------------------------------
        # CUSUM detector
        # ------------------------------------------

        cusum = CUSUMDetector()

        c_out = cusum.update(k_out["residual"])

        # ------------------------------------------
        # Timing jitter detector
        # ------------------------------------------

        jitter = JitterDetector(
            mu=0.004,
            sigma=0.001,
            eta_sigma=3.5,
            eta_mu=2.0,
            W=50
        )

        delta_t = rng.uniform(0.0035, 0.0045)

        if attack_name != "baseline":
            delta_t += rng.uniform(0.002, 0.006)

        jitter_result = jitter.update(delta_t)

        # ------------------------------------------
        # Hive consensus
        # ------------------------------------------

        hive = HiveConsensus()

        votes = [
            int(k_out["detected"]),
            int(c_out["detected"]),
            int(jitter_result["detected"])
        ]

        consensus = sum(votes) >= 2

        # ------------------------------------------
        # Save row
        # ------------------------------------------

        rows.append({
            "case": case,
            "attack": attack_name,

            "kalman_residual":
                round(k_out["residual"], 6),

            "cusum_score":
                round(c_out["score"], 6),

            "jitter_z":
                round(jitter_result["z_score"], 6),

            "jitter_window":
                round(jitter_result["window_mean_z"], 6),

            "consensus":
                int(consensus),

            "latency":
                result["latency"],

            "delta_v":
                result["delta_v"]
        })

# --------------------------------------------------
# Save CSV
# --------------------------------------------------

csv_path = "experiments/results/macpr_results.csv"

with open(csv_path, "w", newline="") as f:

    writer = csv.DictWriter(f, fieldnames=rows[0].keys())

    writer.writeheader()

    writer.writerows(rows)

print("\nSaved:", csv_path)
print("Rows:", len(rows))
