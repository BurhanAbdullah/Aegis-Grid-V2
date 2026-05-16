import os
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    roc_curve,
    auc,
)

# =====================================================
# LOAD AUTHORITATIVE FINAL DATASET
# =====================================================

CSV_PATH = "paper/data/final_dataset_labeled.csv"

df = pd.read_csv(CSV_PATH)

# =====================================================
# GROUND TRUTH + CONTINUOUS SCORE
# =====================================================

y_true = df["y_true"]
y_score = df["threat_score"]

# =====================================================
# ROC COMPUTATION
# =====================================================

fpr, tpr, thresholds = roc_curve(
    y_true,
    y_score
)

roc_auc = auc(fpr, tpr)

print(f"\nROC AUC = {roc_auc:.6f}")

# =====================================================
# SAVE ROC CSV
# =====================================================

roc_df = pd.DataFrame({
    "fpr": fpr,
    "tpr": tpr,
    "threshold": thresholds
})

# Ensure directories exist
os.makedirs("results", exist_ok=True)
os.makedirs("paper/data", exist_ok=True)
os.makedirs("paper/figures", exist_ok=True)

# Save results CSV
roc_df.to_csv(
    "results/roc_metrics.csv",
    index=False
)

# Copy CSV into paper
roc_df.to_csv(
    "paper/data/roc_metrics.csv",
    index=False
)

# =====================================================
# PLOT ROC CURVE
# =====================================================

plt.figure(figsize=(6, 5))

plt.plot(
    fpr,
    tpr,
    linewidth=2,
    label=f"AUC = {roc_auc:.3f}"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend(loc="lower right")

plt.tight_layout()

# Save plots
plt.savefig(
    "results/roc_curve.png",
    dpi=300
)

plt.savefig(
    "paper/figures/roc_curve.png",
    dpi=300
)

print("\nSaved:")
print("  results/roc_metrics.csv")
print("  paper/data/roc_metrics.csv")
print("  results/roc_curve.png")
print("  paper/figures/roc_curve.png")
