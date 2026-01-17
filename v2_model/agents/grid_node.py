import random
import time

class SmartGridNode:
    def __init__(self, node_id, cert):
        self.node_id = node_id
        self.cert = cert
        self.cap_score = 0.0
        self.is_locked = False
        self.history = [] # For plotting

    def process_traffic(self, packet_rate):
        """L5: CAP Logic - Monitors DDoS pressure"""
        if packet_rate > 1000:
            self.cap_score = min(1.5, self.cap_score + 0.15)
        else:
            self.cap_score = max(0.0, self.cap_score - 0.05)
        
        if self.cap_score >= 1.0:
            self.is_locked = True
        
        # Log state for visualization
        self.history.append((time.time(), packet_rate, self.cap_score))
        return "ISOLATED" if self.is_locked else "STABLE"
