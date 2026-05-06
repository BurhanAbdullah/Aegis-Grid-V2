import sys
import os
import csv
import random
import numpy as np

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from matpower_voltage_parser import run_with_voltages
from v3_fabric.core.jitter_detector import JitterDetector
from v4_hive.core.hive_consensus import HiveConsensus


# ==========================================================
# Lightweight Detectors
# ==========================================================

class KalmanAnomalyDetector:

    def __init__(self, threshold=0.025):

        self.threshold = threshold

    def update(self, z):

        residual = float(
            np.mean(
                np.abs(np.array(z) - 1.0)
            )
        )

        detected = residual > self.threshold

        return {
            "residual": residual,
            "detected": detected
        }


class CUSUMDetector:

    def __init__(self, threshold=0.08):

        self.threshold = threshold

        self.g = 0.0

    def update(self, x):

        self.g = max(
            0.0,
            self.g + x - 0.01
        )

        detected = self.g > self.threshold

        return {
            "score": self.g,
            "detected": detected
        }


# ==========================================================
# Experiment Configuration
# ==========================================================

CASES = [
    "case9",
    "case14",
    "case30",
    "case118"
]

ATTACKS = {

    # --------------------------------------------------
    # Baseline
    # --------------------------------------------------

    "baseline": "",

    # --------------------------------------------------
    # Small reactance perturbation
    # --------------------------------------------------

    "impedance_perturb":
        "mpc.branch(:,4)=mpc.branch(:,4)*1.02;",

    # --------------------------------------------------
    # Small distributed load drift
    # --------------------------------------------------

    "load_shift":
        "mpc.bus(:,3)=mpc.bus(:,3)*1.01;"
        "mpc.bus(:,4)=mpc.bus(:,4)*1.01;",

    # --------------------------------------------------
    # Generator voltage drift
    # --------------------------------------------------

    "voltage_drift":
        "mpc.gen(:,6)=mpc.gen(:,6)*1.005;",

    # --------------------------------------------------
    # Resistance perturbation
    # --------------------------------------------------

    "resistance_shift":
        "mpc.branch(:,3)=mpc.branch(:,3)*1.03;",

    # --------------------------------------------------
    # Localized demand perturbation
    # --------------------------------------------------

    "localized_load_attack":
        "mpc.bus(5,3)=mpc.bus(5,3)*1.05;"
        "mpc.bus(5,4)=mpc.bus(5,4)*1.05;",
}

os.makedirs(
    "experiments/results",
    exist_ok=True
)

rows = []

print("\n" + "=" * 72)
print("  MACPR Full Experiment Pipeline")
print("=" * 72)


# ==========================================================
# Main Experiment Loop
# ==========================================================

for case in CASES:

    print(f"\n--- {case} ---")

    rng = random.Random(42)

    # --------------------------------------------------
    # Baseline PF
    # --------------------------------------------------

    base = run_with_voltages(case)

    if not base["success"]:

        print("MATPOWER failed for", case)

        continue

    nominal_v = base["voltages"]

    # --------------------------------------------------
    # Scenario Loop
    # --------------------------------------------------

    for attack_name, attack_code in ATTACKS.items():

        print(f"  -> {attack_name}")

        result = run_with_voltages(
            case,
            attack_code
        )

        if not result["success"]:

            print("     power flow failed")

            continue

        # --------------------------------------------------
        # Add realistic sensor noise
        # --------------------------------------------------

        voltages = [
            v + rng.gauss(0, 0.002)
            for v in result["voltages"]
        ]

        # --------------------------------------------------
        # Kalman residual detector
        # --------------------------------------------------

        kalman = KalmanAnomalyDetector()

        k_out = kalman.update(voltages)

        # --------------------------------------------------
        # Sequential CUSUM detector
        # --------------------------------------------------

        cusum = CUSUMDetector()

        c_out = cusum.update(
            k_out["residual"]
        )

        # --------------------------------------------------
        # Timing jitter detector
        # --------------------------------------------------

        jitter = JitterDetector(
            mu=0.004,
            sigma=0.001,
            eta_sigma=3.5,
            eta_mu=2.0,
            W=50
        )

        delta_t = rng.gauss(
            0.004,
            0.001
        )

        if attack_name != "baseline":

            delta_t += abs(
                rng.gauss(
                    0.0015,
                    0.002
                )
            )

        jitter_result = jitter.update(delta_t)

        # --------------------------------------------------
        # Consensus fusion
        # --------------------------------------------------

        hive = HiveConsensus()

        votes = [

            int(k_out["detected"]),

            int(c_out["detected"]),

            int(jitter_result["detected"])
        ]

        consensus = sum(votes) >= 2

        # --------------------------------------------------
        # Save results
        # --------------------------------------------------

        rows.append({

            "case":
                case,

            "attack":
                attack_name,

            "kalman_residual":
                round(
                    k_out["residual"],
                    6
                ),

            "cusum_score":
                round(
                    c_out["score"],
                    6
                ),

            "jitter_z":
                round(
                    jitter_result["z_score"],
                    6
                ),

            "jitter_window":
                round(
                    jitter_result["window_mean_z"],
                    6
                ),

            "consensus":
                int(consensus),

            "latency":
                result["latency"],

            "delta_v":
                result["delta_v"]
        })

# ==========================================================
# Save CSV
# ==========================================================

csv_path = (
    "experiments/results/macpr_results.csv"
)

with open(
    csv_path,
    "w",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=rows[0].keys()
    )

    writer.writeheader()

    writer.writerows(rows)

print("\nSaved:", csv_path)

print("Rows:", len(rows))
