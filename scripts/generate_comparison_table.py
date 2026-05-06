import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

df = pd.read_csv("data/full_experiment_table.csv")

y_true = (df['attack'] != 'baseline').astype(int)

def eval_model(name, pred):
    return {
        "method": name,
        "precision": precision_score(y_true, pred),
        "recall": recall_score(y_true, pred),
        "f1": f1_score(y_true, pred)
    }

rows = []

# Proposed method
score = (
    0.3333*df['kalman_anomaly'] +
    0.3333*(df['cusum_alarm']==True) +
    0.3333*(df['jitter_detected']==True)
)

rows.append(eval_model("Proposed", (score >= 0.2).astype(int)))

# Baselines
rows.append(eval_model("CUSUM",  (df['cusum_alarm']==True).astype(int)))
rows.append(eval_model("JITTER", (df['jitter_detected']==True).astype(int)))
rows.append(eval_model("KALMAN", (df['kalman_anomaly']==True).astype(int)))

pd.DataFrame(rows).to_csv("plotting_data/comparison_table.csv", index=False)

print("comparison_table.csv generated")
