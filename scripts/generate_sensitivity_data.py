import pandas as pd
import numpy as np
from sklearn.metrics import recall_score

df = pd.read_csv("data/full_experiment_table.csv")

y_true = (df['attack'] != 'baseline').astype(int)
scores = df['threat_score']

thresholds = np.linspace(scores.min(), scores.max(), 50)

recalls = []

for th in thresholds:
    y_pred = (scores >= th).astype(int)
    r = recall_score(y_true, y_pred)
    recalls.append(r)

out = pd.DataFrame({
    "threshold": thresholds,
    "recall": recalls
})

out.to_csv("plotting_data/sensitivity_data.csv", index=False)

print("Sensitivity data generated")
