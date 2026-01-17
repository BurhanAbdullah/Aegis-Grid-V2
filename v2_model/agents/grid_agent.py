import time
import os

class AegisAgent: # Renamed for backward compatibility with audit scripts
    def __init__(self, node_id, cert, mac):
        self.node_id = node_id
        self.cert = cert
        self.mac = mac
        
        # V3 State Vectors
        self.vectors = {
            "pressure": 0.0,
            "timing": 0.0,
            "trust": 1.0
        }
        self.cap_score = 0.0
        self.data_locked = False

    def analyze_packet(self, packet, incoming_mac, engine=None):
        # L1: Hardware Actuator check
        if incoming_mac != self.mac:
            if engine: engine.log_event("CRITICAL", self.node_id, "Hardware MAC Mismatch")
            self.data_locked = True
            return "TERMINAL_HARDWARE_MISMATCH"
        
        # L2: Causal Jitter Analysis
        delay = time.time() - packet['ts']
        if delay > 2.0:
            self.cap_score += 0.3
            if engine: engine.log_event("WARNING", self.node_id, f"Temporal Deviation: {delay:.2f}s")
        else:
            self.cap_score = max(0, self.cap_score - 0.1)

        # L6: Fail-Secure Lockout
        if self.cap_score >= 1.0:
            self.data_locked = True
            return "FAIL_SECURE_LOCKED"
            
        return "VERIFIED"
