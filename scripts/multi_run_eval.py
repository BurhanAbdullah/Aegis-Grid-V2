import subprocess
import pandas as pd
import numpy as np

results = []

for i in range(10):
    subprocess.run(["python3", "scripts/generate_realistic_dataset.py"], stdout=subprocess.DEVNULL)

    df = pd.read_csv("data/full_experiment_table.csv")
    y_true = (df['attack'] != 'baseline').astype(int)

    score = (
        0.3333*df['kalman_anomaly'] +
        0.3333*(df['cusum_alarm']==True) +
        0.3333*(df['jitter_detected']==True)
    )

    y_pred = (score >= 0.2).astype(int)

    from sklearn.metrics import precision_score, recall_score, f1_score

    results.append({
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred)
    })

df_out = pd.DataFrame(results)

print("\n=== MULTI-RUN RESULTS ===")
print(df_out.describe())

df_out.to_csv("plotting_data/multi_run_results.csv", index=False)
