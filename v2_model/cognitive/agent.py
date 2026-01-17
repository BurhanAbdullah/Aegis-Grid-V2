import time
import numpy as np

class AegisV2Agent:
    def __init__(self, node_id, mac_id):
        self.node_id = node_id
        self.mac_id = mac_id
        
        # Internal Cognitive State Vectors
        self.vectors = {
            "pressure": 0.0, # Rolling CAP + Trend
            "timing": 0.0,   # Latency Drift + Jitter Slope
            "entropy": 1.0,  # Stealth Effectiveness
            "trust": 1.0     # Hardware Confidence
        }
        self.state = "STABLE"

    def reason(self, metrics, incoming_mac):
        """Decision Model: R = (P * T) / (E * G)"""
        
        # L1: Hardware Fingerprint Actuation
        if incoming_mac != self.mac_id:
            self.vectors["trust"] = 0.0
            self.state = "ISOLATED_HARDWARE_FAILURE"
            return self.state

        # Update Vectors (Predictive, not reactive)
        self.vectors["pressure"] = (self.vectors["pressure"] * 0.8) + (metrics.get('load_trend', 0) * 0.2)
        self.vectors["timing"] += metrics.get('jitter_slope', 0)
        
        # Calculate Composite Risk Surface
        risk = (self.vectors["pressure"] * (1 + self.vectors["timing"])) / (self.vectors["entropy"] * self.vectors["trust"] + 1e-6)

        # Policy-Based Transitions
        if risk > 0.85:
            self.state = "MUTATING_PROTOCOL" # Pre-emptive Key Fracturing
        elif risk > 0.5:
            self.state = "DECOY_INJECTION"  # Active Camouflage
        else:
            self.state = "STABLE"
            
        return self.state
