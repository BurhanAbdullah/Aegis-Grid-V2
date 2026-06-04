import numpy as np
import random
import pandas as pd

from core.trust_vector import TrustVector
from core.predictive_risk_containment import PredictiveRiskContainment
from core.adaptive_quorum import adaptive_quorum
from core.hysteresis import update_membership

ROWS = []

for trust_seed in np.linspace(0.1,1.0,20):
    for risk_seed in np.linspace(0.0,0.9,20):

        tv = TrustVector()

        tv.competence = trust_seed
        tv.behavior = trust_seed
        tv.loyalty = trust_seed
        tv.stability = trust_seed

        prc = PredictiveRiskContainment()

        active = True
        successful_rounds = 0
        failed_rounds = 0

        trust_history = []
        quorum_history = []

        for rnd in range(100):

            risk = min(
                1.0,
                max(
                    0.0,
                    risk_seed + random.uniform(-0.05, 0.05)
                )
            )

            trust = tv.aggregate()

            governance_weight = prc.governance_weight(
                trust,
                risk
            )

            quorum = adaptive_quorum(
                active_nodes=10,
                avg_trust=trust
            )

            active = update_membership(
                active,
                governance_weight
            )

            trust_history.append(trust)
            quorum_history.append(quorum)

            if active and governance_weight >= quorum:
                successful_rounds += 1
            else:
                failed_rounds += 1

            tv.competence = max(
                0.0,
                min(
                    1.0,
                    tv.competence - risk * 0.01
                )
            )

            tv.behavior = max(
                0.0,
                min(
                    1.0,
                    tv.behavior - risk * 0.008
                )
            )

            tv.loyalty = max(
                0.0,
                min(
                    1.0,
                    tv.loyalty - risk * 0.006
                )
            )

            tv.stability = max(
                0.0,
                min(
                    1.0,
                    tv.stability - risk * 0.004
                )
            )

        survivability = (
            successful_rounds /
            (successful_rounds + failed_rounds)
        )

        ROWS.append({
            "initial_trust": trust_seed,
            "initial_risk": risk_seed,
            "survivability": survivability,
            "final_trust": tv.aggregate(),
            "mean_quorum": sum(quorum_history)/len(quorum_history)
        })

df = pd.DataFrame(ROWS)

df.to_csv(
    "results/governance_sweep.csv",
    index=False
)

df.to_csv(
    "paper/data/survivability_landscape.csv",
    index=False
)

print(df.head())
print()
print("rows =", len(df))
