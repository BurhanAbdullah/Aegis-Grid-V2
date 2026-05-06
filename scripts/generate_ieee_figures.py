import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =============================
# GLOBAL STYLE (IEEE)
# =============================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['legend.fontsize'] = 10

# Load data
roc = pd.read_csv("plotting_data/roc_curve_data.csv")
sens = pd.read_csv("plotting_data/sensitivity_data.csv")
comp = pd.read_csv("plotting_data/comparison_table.csv")
multi = pd.read_csv("plotting_data/multi_run_results.csv")

# =============================
# FIG 1 — ROC CURVE
# =============================
plt.figure(figsize=(5,4))
plt.plot(roc['fpr'], roc['tpr'], linewidth=2, label='Proposed Method')
plt.plot([0,1],[0,1],'k--', linewidth=1, label='Random Guess')

plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("figures/fig_roc.png", dpi=600)
plt.close()

# =============================
# FIG 2 — THRESHOLD SENSITIVITY
# =============================
plt.figure(figsize=(5,4))
plt.plot(sens['threshold'], sens['recall'], linewidth=2)

plt.xlabel('Threshold')
plt.ylabel('Recall')
plt.title('Threshold Sensitivity')
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("figures/fig_sensitivity.png", dpi=600)
plt.close()

# =============================
# FIG 3 — COMPARISON BAR
# =============================
plt.figure(figsize=(6,4))

methods = comp['method']
x = np.arange(len(methods))

plt.bar(x-0.2, comp['precision'], width=0.2, label='Precision')
plt.bar(x, comp['recall'], width=0.2, label='Recall')
plt.bar(x+0.2, comp['f1'], width=0.2, label='F1-score')

plt.xticks(x, methods)
plt.ylabel('Score')
plt.title('Detector Performance Comparison')
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig("figures/fig_comparison.png", dpi=600)
plt.close()

# =============================
# FIG 4 — MULTI-RUN STABILITY
# =============================
plt.figure(figsize=(5,4))

data = [multi['precision'], multi['recall'], multi['f1']]
plt.boxplot(data, labels=['Precision','Recall','F1'])

plt.ylabel('Score')
plt.title('Multi-run Performance Stability')
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("figures/fig_stability.png", dpi=600)
plt.close()

# =============================
# FIG 5 — HEATMAP
# =============================
heat = pd.read_csv("plotting_data/heatmap_data.csv")

plt.figure(figsize=(6,4))
plt.imshow(heat.T, aspect='auto')
plt.colorbar()

plt.yticks(range(4), ['Kalman','CUSUM','Jitter','Consensus'])
plt.xlabel('Sample Index')
plt.title('Detector Agreement Heatmap')

plt.tight_layout()
plt.savefig("figures/fig_heatmap.png", dpi=600)
plt.close()

print("All IEEE-quality figures generated.")

