import time

class AegisAgent:
    def __init__(self, node_id, cert, mac):
        self.node_id = node_id
        self.cert = cert
        self.mac = mac
        self.cap_score = 0.0
        self.data_locked = False

    def analyze_packet(self, packet, incoming_mac, engine=None):
        if incoming_mac != self.mac:
            self.data_locked = True
            return "TERMINAL_HARDWARE_MISMATCH"
        
        delay = time.time() - packet['ts']
        if delay > 2.0:
            self.cap_score += 0.3
        else:
            self.cap_score = max(0, self.cap_score - 0.1)

        if self.cap_score >= 1.0:
            self.data_locked = True
            return "FAIL_SECURE_LOCKED"
            
        return "VERIFIED"
