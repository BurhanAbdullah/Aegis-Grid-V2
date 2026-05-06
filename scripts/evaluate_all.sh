#!/bin/bash

echo "======================================"
echo "AEGIS-GRID EVALUATION (FINAL)"
echo "======================================"

python3 << 'PYCODE'
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

df = pd.read_csv("data/full_experiment_table.csv")

y_true = (df['attack'] != 'baseline').astype(int)

wk = 0.3333
wc = 0.3333
wj = 0.3333
th = 0.2

kalman = df['kalman_anomaly'].astype(int)
cusum  = (df['cusum_alarm'] == True).astype(int)
jitter = (df['jitter_detected'] == True).astype(int)

score = wk*kalman + wc*cusum + wj*jitter
y_pred = (score >= th).astype(int)

precision = precision_score(y_true, y_pred)
recall    = recall_score(y_true, y_pred)
f1        = f1_score(y_true, y_pred)
auc       = roc_auc_score(y_true, df['threat_score'])

print("\n=== MAIN METHOD ===")
print(f"Precision : {precision:.3f}")
print(f"Recall    : {recall:.3f}")
print(f"F1 Score  : {f1:.3f}")
print(f"AUC       : {auc:.3f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))

print("\n=== BASELINES ===")

def eval_model(name, pred):
    p = precision_score(y_true, pred)
    r = recall_score(y_true, pred)
    f = f1_score(y_true, pred)
    print(f"{name:10s} | P={p:.3f} R={r:.3f} F1={f:.3f}")

eval_model("CUSUM",  (df['cusum_alarm']==True).astype(int))
eval_model("JITTER", (df['jitter_detected']==True).astype(int))
eval_model("KALMAN", (df['kalman_anomaly']==True).astype(int))

print("\nEvaluation complete.")
PYCODE
