import random
import os

def apply_stealth_policy(data, agent_state):
    """Actuates the agent's stealth decision"""
    if agent_state == "MUTATING_PROTOCOL":
        burst_size = 16 # Increase complexity under stress
    elif agent_state == "DECOY_INJECTION":
        burst_size = 12
    else:
        burst_size = 8  # Baseline
        
    package = [os.urandom(32).hex() for _ in range(burst_size - 1)]
    package.append(data)
    random.shuffle(package)
    return package, package.index(data)
