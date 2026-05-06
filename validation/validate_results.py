#!/usr/bin/env python3

from core.consensus import compute_consensus
from core.mitigation import trigger_mitigation

tests = [
    (0,0,0),
    (1,0,0),
    (1,1,0),
    (1,1,1),
]

for t in tests:

    consensus = compute_consensus(*t)

    mitigation = trigger_mitigation(consensus)

    assert mitigation == bool(consensus)

print("Consensus/mitigation validation passed.")
