import pandas as pd
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

df = pd.read_csv(
    "experiments/results/macpr_results.csv"
)

# ----------------------------------------
# Labels
# ----------------------------------------

df["label"] = (
    df["attack"] != "baseline"
).astype(int)

# ----------------------------------------
# Composite detection score
# ----------------------------------------

score = (
    df["kalman_residual"] * 10
    + abs(df["jitter_z"])
    + df["consensus"] * 2
)

# ----------------------------------------
# ROC
# ----------------------------------------

fpr, tpr, thresholds = roc_curve(
    df["label"],
    score
)

roc_auc = auc(fpr, tpr)

print("\nROC AUC =", roc_auc)

# ----------------------------------------
# Save metrics
# ----------------------------------------

roc_df = pd.DataFrame({
    "fpr": fpr,
    "tpr": tpr,
    "threshold": thresholds
})

roc_df.to_csv(
    "results/roc_metrics.csv",
    index=False
)

# ----------------------------------------
# Plot
# ----------------------------------------

plt.figure(figsize=(6,5))

plt.plot(fpr, tpr, linewidth=2)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title(
    f"ROC Curve (AUC={roc_auc:.4f})"
)

plt.grid(True)

plt.savefig(
    "results/roc_curve.png",
    dpi=300,
    bbox_inches="tight"
)

print("Saved:")
print("  results/roc_metrics.csv")
print("  results/roc_curve.png")
