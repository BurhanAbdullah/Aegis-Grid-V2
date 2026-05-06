import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

df = pd.read_csv("data/full_experiment_table.csv")
y_true = (df['attack'] != 'baseline').astype(int).values

kalman = df['kalman_anomaly'].astype(int).values
cusum  = (df['cusum_alarm'] == True).astype(int).values
jitter = (df['jitter_detected'] == True).astype(int).values

best = {"f1": -1}

for wk in np.linspace(0.2,0.8,7):
    for wc in np.linspace(0.2,0.8,7):
        for wj in np.linspace(0.2,0.8,7):
            s = wk+wc+wj
            wk2, wc2, wj2 = wk/s, wc/s, wj/s

            score = wk2*kalman + wc2*cusum + wj2*jitter

            for th in np.linspace(0.2,1.8,17):
                y_pred = (score >= th).astype(int)

                p = precision_score(y_true, y_pred, zero_division=0)
                r = recall_score(y_true, y_pred, zero_division=0)
                f = f1_score(y_true, y_pred, zero_division=0)

                if f > best.get("f1",-1) and p >= 0.95:
                    best = {"f1":f,"p":p,"r":r,"wk":wk2,"wc":wc2,"wj":wj2,"th":th}

print(best)
