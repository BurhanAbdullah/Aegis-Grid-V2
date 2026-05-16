import random
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
)

# =====================================================
# LOAD AUTHORITATIVE DATASET
# =====================================================

df = pd.read_csv(
    "data/full_experiment_table.csv"
)

# =====================================================
# GROUND TRUTH
# =====================================================

df["y_true"] = (
    df["attack"] != "baseline"
).astype(int)

# =====================================================
# ORIGINAL DETECTORS
# =====================================================

kalman = (
    df["kalman_anomaly"]
    .astype(int)
)

cusum = (
    df["cusum_alarm"] == True
).astype(int)

jitter = (
    df["jitter_detected"] == True
).astype(int)

# =====================================================
# BYZANTINE SIMULATION
# =====================================================

results = []

fault_probs = [
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
]

for p in fault_probs:

    y_pred = []

    for k, c, j in zip(
        kalman,
        cusum,
        jitter
    ):

        votes = [k, c, j]

        # -----------------------------------------
        # Random malicious agent corruption
        # -----------------------------------------

        if random.random() < p:

            idx = random.randint(0, 2)

            votes[idx] = 1 - votes[idx]

        consensus = int(sum(votes) >= 2)

        y_pred.append(consensus)

    precision = precision_score(
        df["y_true"],
        y_pred
    )

    recall = recall_score(
        df["y_true"],
        y_pred
    )

    f1 = f1_score(
        df["y_true"],
        y_pred
    )

    results.append({
        "fault_probability": p,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
    })

# =====================================================
# EXPORT RESULTS
# =====================================================

out_df = pd.DataFrame(results)

out_df.to_csv(
    "paper/generated/byzantine_results.csv",
    index=False
)

print("\n===================================")
print("BYZANTINE-INSPIRED TEST COMPLETE")
print("===================================")

print(out_df)
