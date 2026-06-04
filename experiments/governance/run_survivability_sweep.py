import pandas as pd

rows = []

for trust in [0.4,0.5,0.6,0.7,0.8]:
    for risk in [0.0,0.1,0.2,0.3,0.4]:
        survivability = max(0.0, trust*(1-risk))
        rows.append({
            "trust": trust,
            "risk": risk,
            "survivability": survivability
        })

df = pd.DataFrame(rows)

df.to_csv(
    "results/governance_sweep.csv",
    index=False
)

df.to_csv(
    "paper/data/survivability_landscape.csv",
    index=False
)

print(df.head())
