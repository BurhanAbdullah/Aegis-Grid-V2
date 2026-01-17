import time

class AegisAgent:
    def __init__(self, node_id, cert, mac):
        self.node_id = node_id
        self.cert = cert
        self.mac = mac
        self.cap_score = 0.0
        self.data_locked = False

    def analyze_packet(self, packet, incoming_mac, engine=None):
        # 1. Hardware Fingerprint Check
        if incoming_mac != self.mac:
            if engine: engine.log_event("CRITICAL", self.node_id, "Hardware MAC Mismatch")
            self.data_locked = True
            return "TERMINAL_HARDWARE_MISMATCH"
        
        # 2. Temporal Freshness Check
        delay = time.time() - packet['ts']
        if delay > 2.0:
            self.cap_score += 0.3
            if engine: engine.log_event("WARNING", self.node_id, f"Temporal Deviation: {delay:.2f}s")
        else:
            self.cap_score = max(0, self.cap_score - 0.1)

        # 3. Fail-Secure Trigger
        if self.cap_score >= 1.0:
            self.data_locked = True
            return "FAIL_SECURE_LOCKED"
            
        return "VERIFIED"
