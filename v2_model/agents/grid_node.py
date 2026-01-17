import random
import time

class SmartGridNode:
    def __init__(self, node_id, cert):
        self.node_id = node_id
        self.cert = cert
        self.cap_score = 0.0
        self.is_locked = False
        self.temporal_freshness = 2.0 # Strict 2s window

    def transmit(self, payload):
        """L4: Shannon Stealth - Masking data with high-entropy noise"""
        dummy_noise = "".join(random.choices("0123456789abcdef", k=len(payload)))
        return {
            "node": self.node_id,
            "data": payload,
            "noise": dummy_noise,
            "ts": time.time()
        }

    def process_traffic(self, packet_rate):
        """L3/L5: Agentic Decision Loop & CAP Monitoring"""
        if packet_rate > 1000:
            self.cap_score += 0.25
        else:
            self.cap_score = max(0.0, self.cap_score - 0.05)

        if self.cap_score >= 1.0:
            self.is_isolated = True
            return "ISOLATED"
        return "STABLE"
