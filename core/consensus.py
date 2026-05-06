#!/usr/bin/env python3

def compute_consensus(v_p, v_m, v_a, threshold=2):
    votes = int(v_p) + int(v_m) + int(v_a)
    consensus = int(votes >= threshold)
    return consensus
