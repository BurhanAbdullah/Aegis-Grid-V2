def survivability(successful_rounds, total_rounds):
    if total_rounds == 0:
        return 0.0
    return successful_rounds / total_rounds
