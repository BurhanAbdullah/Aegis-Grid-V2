import numpy as np
import pandas as pd

df = pd.read_csv(
    "results/stealth/nis_results.csv"
)

baseline_window = 50
kappa = 0.15
threshold = 8.0
decay = 0.92

baseline_mean = (
    df["nis"]
    .iloc[:baseline_window]
    .mean()
)

baseline_std = (
    df["nis"]
    .iloc[:baseline_window]
    .std()
)

print("\nBaseline statistics")
print("-------------------")
print(f"Mean : {baseline_mean:.4f}")
print(f"Std  : {baseline_std:.4f}")

S = 0
scores = []
detections = []

for nis in df["nis"]:

    z = (nis - baseline_mean) / baseline_std

    S = max(
        0,
        decay * S + (z - kappa)
    )

    scores.append(S)

    detections.append(
        int(S > threshold)
    )

df["seq_score"] = scores
df["seq_detect"] = detections

print("\nSequential detector preview")
print("---------------------------")

print(
    df[
        [
            "cycle",
            "nis",
            "seq_score",
            "seq_detect",
            "label"
        ]
    ].head(20)
)

df.to_csv(
    "results/sequential/sequential_scores.csv",
    index=False
)

print("\nSaved:")
print("results/sequential/sequential_scores.csv")
