#!/usr/bin/env python3

from core.consensus import compute_consensus
from core.mitigation import trigger_mitigation

cases = {
    "baseline": (0,0,0),
    "stealth":  (1,0,0),
    "flood":    (1,1,1),
    "timing":   (0,1,1),
}

for name, votes in cases.items():

    v_p, v_m, v_a = votes

    consensus = compute_consensus(v_p, v_m, v_a)

    mitigation = trigger_mitigation(consensus)

    print(
        f"{name} | "
        f"v_p={v_p} "
        f"v_m={v_m} "
        f"v_a={v_a} "
        f"| consensus={consensus} "
        f"| mitigation={mitigation}"
    )
