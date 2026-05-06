import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    roc_curve,
    auc,
    precision_score,
    recall_score,
    f1_score
)

df = pd.read_csv(
    "results/sequential/sequential_scores.csv"
)

y_true = df["label"]

# =====================================================
# DETECTOR SCORES
# =====================================================

chi_scores = df["nis"]

kf_scores = (
    (df["nis"] - df["nis"].mean())
    / df["nis"].std()
)

aegis_scores = df["seq_score"]

# =====================================================
# ROC
# =====================================================

fpr_a, tpr_a, _ = roc_curve(y_true, aegis_scores)
fpr_k, tpr_k, _ = roc_curve(y_true, kf_scores)
fpr_c, tpr_c, _ = roc_curve(y_true, chi_scores)

auc_a = auc(fpr_a, tpr_a)
auc_k = auc(fpr_k, tpr_k)
auc_c = auc(fpr_c, tpr_c)

# =====================================================
# THRESHOLD METRICS
# =====================================================

threshold = 8.0

pred_a = (aegis_scores > threshold).astype(int)

precision = precision_score(
    y_true,
    pred_a
)

recall = recall_score(
    y_true,
    pred_a
)

f1 = f1_score(
    y_true,
    pred_a
)

# =====================================================
# PRINT RESULTS
# =====================================================

print("\n================================================")
print("REAL DETECTOR BENCHMARKING")
print("================================================\n")

print("AUC RESULTS")
print("--------------------------------")

print(f"AEGIS Sequential : {auc_a:.4f}")
print(f"Plain KF         : {auc_k:.4f}")
print(f"Chi-Square       : {auc_c:.4f}")

print("\nAEGIS THRESHOLD METRICS")
print("--------------------------------")

print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")

# =====================================================
# ROC FIGURE
# =====================================================

plt.figure(figsize=(8,6))

plt.plot(
    fpr_a,
    tpr_a,
    linewidth=2,
    label=f'AEGIS (AUC={auc_a:.3f})'
)

plt.plot(
    fpr_k,
    tpr_k,
    linewidth=2,
    label=f'KF (AUC={auc_k:.3f})'
)

plt.plot(
    fpr_c,
    tpr_c,
    linewidth=2,
    label=f'Chi² (AUC={auc_c:.3f})'
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Real Detector ROC Comparison")
plt.legend()

plt.savefig(
    "figures/roc/real_roc_comparison.png",
    dpi=300
)

print("\nROC figure updated:")
print("figures/roc/real_roc_comparison.png")
