import random
import numpy as np
import pandas as pd

from core.trust_vector import TrustVector
from core.predictive_risk_containment import PredictiveRiskContainment
from core.adaptive_quorum import adaptive_quorum
from core.hysteresis import update_membership

ROWS = []
TRUST_ROWS = []
QUORUM_ROWS = []
PRC_ROWS = []
HYST_ROWS = []

for trust_seed in np.linspace(0.1, 1.0, 20):
    for risk_seed in np.linspace(0.0, 0.9, 20):

        tv = TrustVector()

        tv.competence = trust_seed
        tv.behavior = trust_seed
        tv.loyalty = trust_seed
        tv.stability = trust_seed

        prc = PredictiveRiskContainment()

        active = True
        successful_rounds = 0
        failed_rounds = 0

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

            previous_state = active

            active = update_membership(
                active,
                governance_weight
            )

            TRUST_ROWS.append([
                trust_seed,
                risk_seed,
                rnd,
                trust
            ])

            QUORUM_ROWS.append([
                trust_seed,
                risk_seed,
                rnd,
                quorum
            ])

            PRC_ROWS.append([
                trust_seed,
                risk_seed,
                rnd,
                governance_weight
            ])

            if previous_state != active:
                HYST_ROWS.append([
                    trust_seed,
                    risk_seed,
                    rnd,
                    int(previous_state),
                    int(active)
                ])

            quorum_history.append(quorum)

            if active and governance_weight >= quorum:
                successful_rounds += 1
            else:
                failed_rounds += 1

            tv.competence = max(
                0.0,
                min(
                    1.0,
                    tv.competence - risk * 0.010
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
            "mean_quorum": np.mean(quorum_history)
        })

pd.DataFrame(ROWS).to_csv(
    "paper/data/survivability_landscape.csv",
    index=False
)

pd.DataFrame(ROWS).to_csv(
    "results/governance_sweep.csv",
    index=False
)

pd.DataFrame(
    TRUST_ROWS,
    columns=[
        "initial_trust",
        "initial_risk",
        "round",
        "trust"
    ]
).to_csv(
    "paper/data/trust_trajectories.csv",
    index=False
)

pd.DataFrame(
    QUORUM_ROWS,
    columns=[
        "initial_trust",
        "initial_risk",
        "round",
        "quorum"
    ]
).to_csv(
    "paper/data/quorum_dynamics.csv",
    index=False
)

pd.DataFrame(
    PRC_ROWS,
    columns=[
        "initial_trust",
        "initial_risk",
        "round",
        "governance_weight"
    ]
).to_csv(
    "paper/data/prc_actions.csv",
    index=False
)

pd.DataFrame(
    HYST_ROWS,
    columns=[
        "initial_trust",
        "initial_risk",
        "round",
        "old_state",
        "new_state"
    ]
).to_csv(
    "paper/data/hysteresis_transitions.csv",
    index=False
)

print("governance configs =", len(ROWS))
