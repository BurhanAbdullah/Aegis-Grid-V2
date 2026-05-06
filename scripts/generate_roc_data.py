import pandas as pd
import numpy as np
from sklearn.metrics import roc_curve, auc

df = pd.read_csv("data/full_experiment_table.csv")

y_true = (df['attack'] != 'baseline').astype(int)

# continuous score
scores = df['threat_score']

fpr, tpr, thresholds = roc_curve(y_true, scores)
roc_auc = auc(fpr, tpr)

roc_df = pd.DataFrame({
    "fpr": fpr,
    "tpr": tpr,
    "threshold": thresholds
})

roc_df.to_csv("plotting_data/roc_curve_data.csv", index=False)

print(f"AUC = {roc_auc:.4f}")
