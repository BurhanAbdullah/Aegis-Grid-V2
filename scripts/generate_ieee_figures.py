import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Base directory for staging/isolated outputs if provided via sys.argv[1]
base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
plot_dir = os.path.join(base_dir, "plotting_data")
fig_dir = os.path.join(base_dir, "figures")
os.makedirs(fig_dir, exist_ok=True)

# =============================
# GLOBAL STYLE (IEEE)
# =============================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['legend.fontsize'] = 10

# Load data
roc = pd.read_csv(os.path.join(plot_dir, "roc_curve_data.csv"))
sens = pd.read_csv(os.path.join(plot_dir, "sensitivity_data.csv"))
comp = pd.read_csv(os.path.join(plot_dir, "comparison_table.csv"))

# =============================
# FIG 1 — ROC CURVE
# =============================
plt.figure(figsize=(5,4))
plt.plot(roc['fpr'], roc['tpr'], linewidth=2, label='Threat Score (AUC=0.9982)')
plt.plot([0,1],[0,1],'k--', linewidth=1, label='Random Guess')

plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Continuous Threat Score ROC')
plt.legend(loc='lower right')
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig_roc.png"), dpi=600)
plt.close()

# =============================
# FIG 2 — THRESHOLD SENSITIVITY (PRECISION & RECALL)
# =============================
plt.figure(figsize=(5.5,4))
plt.plot(sens['threshold'], sens['precision'], linewidth=2, label='Precision', color='#1f77b4')
plt.plot(sens['threshold'], sens['recall'], linewidth=2, linestyle='--', label='Recall', color='#ff7f0e')

plt.xlabel('Threat Score Threshold')
plt.ylabel('Score')
plt.title('Threshold Sensitivity (Precision vs. Recall)')
plt.legend(loc='center right')
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig_sensitivity.png"), dpi=600)
plt.close()

# =============================
# FIG 3 — COMPARISON BAR
# =============================
plt.figure(figsize=(7,4.5))

methods = comp['method']
x = np.arange(len(methods))

plt.bar(x-0.2, comp['precision'], width=0.2, label='Precision')
plt.bar(x, comp['recall'], width=0.2, label='Recall')
plt.bar(x+0.2, comp['f1'], width=0.2, label='F1-score')

plt.xticks(x, methods, rotation=12, ha='right')
plt.ylabel('Score')
plt.title('Detector Performance Comparison')
plt.legend(loc='lower right')
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig_comparison.png"), dpi=600)
plt.close()

# =============================
# FIG 4 — HEATMAP (DETECTOR AGREEMENT)
# =============================
heat = pd.read_csv(os.path.join(plot_dir, "heatmap_data.csv"))

plt.figure(figsize=(6,4))
plt.imshow(heat.T, aspect='auto')
plt.colorbar(label='Activation (0=Normal, 1=Alarm)')

plt.yticks(range(4), ['Kalman','CUSUM','Jitter','Consensus (K=2)'])
plt.xlabel('Sample Index')
plt.title('Detector Agreement Heatmap')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig_heatmap.png"), dpi=600)
plt.close()

print("Candidate publication figures generated successfully.")



