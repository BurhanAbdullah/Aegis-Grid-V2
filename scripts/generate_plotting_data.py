import pandas as pd

df = pd.read_csv("data/full_experiment_table.csv")

# CUSUM
df[['case','attack','cusum_stat']].to_csv("plotting_data/cusum_values.csv", index=False)

# NIS
df[['case','attack','nis']].to_csv("plotting_data/nis_values.csv", index=False)

# JITTER
df[['case','attack','jitter_z']].to_csv("plotting_data/jitter_values.csv", index=False)

# THREAT SCORE
df[['case','attack','threat_score']].to_csv("plotting_data/threat_scores.csv", index=False)

# CONSENSUS
df[['case','attack','consensus']].to_csv("plotting_data/consensus_votes.csv", index=False)

# ACTIVATION FLAGS
df[['cusum_alarm','jitter_detected','kalman_anomaly']].to_csv(
    "plotting_data/detector_activation.csv", index=False
)

print("Plotting CSVs regenerated from final dataset.")
