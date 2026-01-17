import time
import math

class Q2AdaptiveAgent:
    """
    V2 Adaptive Agent: 
    Monitors adversarial pressure and adapts Lattice-parameters.
    """
    def __init__(self):
        self.security_level = 1
        self.threat_pressure = 0.0
        self.last_adaptation = time.time()

    def calculate_threshold(self, loss_rate, compute_load):
        # Adaptive (n, k) logic:
        # As threat pressure increases, we increase the quorum 'k'
        # while maintaining Shannon Entropy invariants.
        base_k = 3
        adaptation_factor = math.ceil(self.threat_pressure * 2)
        k_prime = base_k + adaptation_factor
        return min(k_prime, 10) # Cap at 10 for latency reasons

    def update_threat_model(self, anomalies):
        self.threat_pressure = min(1.0, self.threat_pressure + (anomalies * 0.1))
        print(f"[AGENT] Threat Pressure: {self.threat_pressure:.2f} | Adapting Quorum...")
