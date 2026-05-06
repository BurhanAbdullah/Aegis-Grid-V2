import pandas as pd
import numpy as np

df = pd.read_csv(
    "results/sequential/sequential_scores.csv"
)

# =====================================================
# NORMALIZATION
# =====================================================

seq_norm = (
    df["seq_score"]
    - df["seq_score"].mean()
) / df["seq_score"].std()

traffic_norm = (
    df["traffic"]
    - df["traffic"].mean()
) / df["traffic"].std()

jitter_norm = (
    df["jitter"]
    - df["jitter"].mean()
) / df["jitter"].std()

# =====================================================
# FUSION SCORE
# =====================================================

fusion_score = (
    0.60 * seq_norm +
    0.25 * traffic_norm +
    0.15 * jitter_norm
)

df["fusion_score"] = fusion_score

print("\n================================================")
print("FUSION DETECTOR SUMMARY")
print("================================================\n")

print(
    df[
        [
            "cycle",
            "fusion_score",
            "label"
        ]
    ].head(20)
)

attack_mean = (
    df[df["label"] == 1]
    ["fusion_score"]
    .mean()
)

normal_mean = (
    df[df["label"] == 0]
    ["fusion_score"]
    .mean()
)

print("\nFusion Separation:")
print(f"Normal Mean : {normal_mean:.3f}")
print(f"Attack Mean : {attack_mean:.3f}")

df.to_csv(
    "results/sequential/fusion_scores.csv",
    index=False
)

print("\nSaved:")
print("results/sequential/fusion_scores.csv")
