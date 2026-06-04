def adaptive_quorum(active_nodes, avg_trust):
    base = 0.67
    adjustment = 0.1 * (avg_trust - 0.5)
    return max(0.5, min(0.9, base + adjustment))
