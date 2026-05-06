#!/usr/bin/env python3

import pandas as pd

INPUT = "results/final_dataset.csv"

df = pd.read_csv(INPUT)

# =====================================================
# NORMALIZE ATTACK LABELS
# =====================================================

def normalize_attack(x):

    x = str(x).lower()

    if x in [
        "baseline",
        "false",
        "0",
        "none"
    ]:
        return 0

    return 1

df["attack_label"] = df["attack"].apply(normalize_attack)

# =====================================================
# CONSENSUS AS PREDICTION
# =====================================================

df["prediction_label"] = (
    df["consensus"] > 0
).astype(int)

# =====================================================
# SAVE
# =====================================================

OUTPUT = "paper/data/final_dataset_labeled.csv"

df.to_csv(OUTPUT, index=False)

print(df[
    [
        "attack",
        "attack_label",
        "consensus",
        "prediction_label"
    ]
].head())

print(f"\n[OK] Saved -> {OUTPUT}")
