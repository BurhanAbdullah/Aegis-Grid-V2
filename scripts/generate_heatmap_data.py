import pandas as pd

df = pd.read_csv("data/full_experiment_table.csv")

heatmap = df[[
    'kalman_anomaly',
    'cusum_alarm',
    'jitter_detected',
    'consensus'
]].astype(int)

heatmap.to_csv("plotting_data/heatmap_data.csv", index=False)

print("Heatmap data saved")
