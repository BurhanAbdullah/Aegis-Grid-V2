import pandas as pd

# =====================================================
# LOAD AUTHORITATIVE DATASET
# =====================================================

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

# =====================================================
# NIS VALUES
# =====================================================

nis_df = (
    df.groupby(["case", "attack"])["nis"]
    .mean()
    .reset_index()
)

nis_df.columns = [
    "case",
    "attack",
    "nis_mean"
]

nis_df.to_csv(
    "paper/data/nis_values.csv",
    index=False
)

# =====================================================
# CUSUM VALUES
# =====================================================

cusum_df = (
    df.groupby(["case", "attack"])["cusum_stat"]
    .mean()
    .reset_index()
)

cusum_df.columns = [
    "case",
    "attack",
    "cusum_mean"
]

cusum_df.to_csv(
    "paper/data/cusum_values.csv",
    index=False
)

# =====================================================
# CONSENSUS VOTES
# =====================================================

consensus_df = (
    df.groupby(["case", "attack"])["consensus"]
    .mean()
    .reset_index()
)

consensus_df.columns = [
    "case",
    "attack",
    "consensus_rate"
]

consensus_df.to_csv(
    "paper/data/consensus_votes.csv",
    index=False
)

print("\n===================================")
print("Paper CSVs regenerated successfully")
print("===================================")

print("\nGenerated:")
print("  paper/data/nis_values.csv")
print("  paper/data/cusum_values.csv")
print("  paper/data/consensus_votes.csv")
