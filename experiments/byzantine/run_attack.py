#!/usr/bin/env python3

from core.consensus import compute_consensus

# Honest votes
v_p = 1
v_m = 1

# Corrupted auditor
v_a = 0

consensus = compute_consensus(v_p, v_m, v_a)

print(f"Byzantine test consensus={consensus}")
