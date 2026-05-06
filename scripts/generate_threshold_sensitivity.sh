#!/bin/bash

echo "Generating threshold sensitivity figure..."

mkdir -p figures

python3 << 'EOF'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("plotting_data/full_experiment_table.csv")

baseline = df[df["attack"]=="baseline"]
attacks = df[df["attack"]!="baseline"]

threshold_scale = np.linspace(0.5,2.0,20)

recall=[]
fpr=[]

for s in threshold_scale:

    detection = attacks["threat_score"] >= (2.5*s)
    recall.append(detection.mean())

    fp = (baseline["threat_score"] >= (2.5*s)).mean()
    fpr.append(fp)

plt.figure(figsize=(7,7))

plt.plot(threshold_scale,recall,label="Recall")
plt.plot(threshold_scale,fpr,label="False Positive Rate")

plt.xlabel("Threshold Scaling Factor")
plt.ylabel("Performance Metric")
plt.title("Sensitivity of Detection Performance to Threshold Scaling")
plt.legend()
plt.grid(True)

plt.savefig("figures/threshold_sensitivity.png",dpi=300)

print("Saved: figures/threshold_sensitivity.png")

EOF
