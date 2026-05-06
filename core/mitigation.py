#!/usr/bin/env python3

def trigger_mitigation(consensus):
    mitigation = bool(consensus)

    assert mitigation == bool(consensus), \
        "Mitigation/consensus mismatch"

    return mitigation
