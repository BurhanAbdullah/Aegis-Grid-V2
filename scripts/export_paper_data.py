import os
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# =====================================================
# LOAD AUTHORITATIVE EXPERIMENT DATA
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
# AUTHORITATIVE DETECTOR LOGIC
# =====================================================

wk = 0.3333
wc = 0.3333
wj = 0.3333

th = 0.2

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
# THREAT SCORE
# =====================================================

score = (
    wk * kalman +
    wc * cusum +
    wj * jitter
)

df["threat_score"] = score

# =====================================================
# REGENERATE PREDICTIONS
# =====================================================

df["y_pred"] = (
    score >= th
).astype(int)

# =====================================================
# OUTPUT DIRECTORIES
# =====================================================

os.makedirs("paper/data", exist_ok=True)
os.makedirs("paper/tables", exist_ok=True)
os.makedirs("paper/generated", exist_ok=True)

# =====================================================
# EXPORT AUTHORITATIVE DATASET
# =====================================================

df.to_csv(
    "paper/data/final_dataset_labeled.csv",
    index=False
)

# =====================================================
# METRICS
# =====================================================

y_true = df["y_true"]
y_pred = df["y_pred"]

precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

metrics_df = pd.DataFrame({
    "Metric": [
        "Precision",
        "Recall",
        "F1-Score"
    ],
    "Value": [
        round(precision, 3),
        round(recall, 3),
        round(f1, 3),
    ]
})

metrics_df.to_csv(
    "paper/tables/main_results.csv",
    index=False
)

# =====================================================
# CONFUSION MATRIX
# =====================================================

cm = confusion_matrix(y_true, y_pred)

cm_df = pd.DataFrame(
    cm,
    columns=[
        "Predicted_Normal",
        "Predicted_Attack"
    ],
    index=[
        "Actual_Normal",
        "Actual_Attack"
    ]
)

cm_df.to_csv(
    "paper/tables/confusion_matrix.csv"
)

# =====================================================
# NIS EXPORT
# =====================================================

nis_df = (
    df.groupby(
        ["case", "attack"]
    )["nis"]
    .mean()
    .reset_index()
)

nis_df.to_csv(
    "paper/generated/nis_values.csv",
    index=False
)

# =====================================================
# CUSUM EXPORT
# =====================================================

cusum_df = (
    df.groupby(
        ["case", "attack"]
    )["cusum_stat"]
    .mean()
    .reset_index()
)

cusum_df.to_csv(
    "paper/generated/cusum_values.csv",
    index=False
)

# =====================================================
# CONSENSUS EXPORT
# =====================================================

consensus_df = (
    df.groupby(
        ["case", "attack"]
    )["consensus"]
    .mean()
    .reset_index()
)

consensus_df.to_csv(
    "paper/generated/consensus_votes.csv",
    index=False
)

print("\n===================================")
print("PAPER EXPORT COMPLETE")
print("===================================")

print(f"Precision : {precision:.3f}")
print(f"Recall    : {recall:.3f}")
print(f"F1 Score  : {f1:.3f}")

print("\nGenerated:")
print("  paper/data/final_dataset_labeled.csv")
print("  paper/tables/main_results.csv")
print("  paper/tables/confusion_matrix.csv")
print("  paper/generated/nis_values.csv")
print("  paper/generated/cusum_values.csv")
print("  paper/generated/consensus_votes.csv")
