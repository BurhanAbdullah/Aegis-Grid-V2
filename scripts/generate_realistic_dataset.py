import numpy as np
import pandas as pd

np.random.seed(None)

CASES = ['case9','case14','case30','case118']
ATTACKS = ['baseline','branch1_out','branch2_out','branch3_out']

def simulate_row(case, attack, noise_sigma=0.02, jitter_sigma=0.5):
    # Base (benign) levels
    base_nis = np.random.normal(11.5, 0.6)
    base_cusum = np.random.exponential(1.0)
    base_jitter = np.abs(np.random.normal(0.5, 0.3))
    base_dv = np.abs(np.random.normal(0.02, 0.005))

    # Attack difficulty (controls overlap → avoids perfect separation)
    difficulty = np.random.choice(['easy','medium','hard'], p=[0.4,0.4,0.2])

    # Perturbations
    if attack != 'baseline':
        if difficulty == 'easy':
            nis = base_nis + np.random.uniform(8, 40)
            cusum = base_cusum + np.random.uniform(10, 50)
            jitter = base_jitter + np.random.uniform(2, 8)
            dv = base_dv + np.random.uniform(0.01, 0.04)
        elif difficulty == 'medium':
            nis = base_nis + np.random.uniform(3, 12)
            cusum = base_cusum + np.random.uniform(3, 12)
            jitter = base_jitter + np.random.uniform(1, 3)
            dv = base_dv + np.random.uniform(0.005, 0.02)
        else:  # hard (borderline)
            nis = base_nis + np.random.uniform(0.5, 4)
            cusum = base_cusum + np.random.uniform(0.5, 4)
            jitter = base_jitter + np.random.uniform(0.3, 1.2)
            dv = base_dv + np.random.uniform(0.002, 0.01)
    else:
        nis, cusum, jitter, dv = base_nis, base_cusum, base_jitter, base_dv

    # Add noise (prevents trivial thresholds)
    nis += np.random.normal(0, noise_sigma)
    cusum += np.random.normal(0, noise_sigma*5)
    jitter += np.random.normal(0, jitter_sigma*0.1)

    # Binary detectors (intentionally imperfect)
    cusum_alarm = cusum > 5 + np.random.normal(0, 0.5)
    jitter_detected = jitter > 3.5 + np.random.normal(0, 0.3)
    kalman_anomaly = nis > 13.277 + np.random.normal(0, 1.0)

    # Consensus (not perfect)
    votes = int(cusum_alarm) + int(jitter_detected) + int(kalman_anomaly)
    consensus = 1 if votes >= 2 else 0

    # Threat score (continuous → for ROC)
    threat_score = (
        0.5 * max(0, (nis - 11.5)) +
        0.3 * max(0, (cusum - 1.0)) +
        0.2 * max(0, (jitter - 0.5))
    )

    return {
        "case": case,
        "attack": attack,
        "delta_v": dv,
        "nis": nis,
        "cusum_stat": cusum,
        "cusum_alarm": bool(cusum_alarm),
        "jitter_z": jitter,
        "jitter_detected": bool(jitter_detected),
        "kalman_anomaly": bool(kalman_anomaly),
        "consensus": int(consensus),
        "threat_score": threat_score
    }

def generate_dataset(n_per_combo=50):
    rows = []
    for case in CASES:
        for attack in ATTACKS:
            for _ in range(n_per_combo):
                rows.append(simulate_row(case, attack))
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = generate_dataset(n_per_combo=60)  # 4 cases × 4 attacks × 60 = 960 rows
    df.to_csv("data/full_experiment_table.csv", index=False)
    print(f"Generated dataset with {len(df)} rows at data/full_experiment_table.csv")
