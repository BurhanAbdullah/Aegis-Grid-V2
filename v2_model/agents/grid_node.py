import time

class SmartGridNode:
    def __init__(self, node_id, cert):
        self.node_id = node_id
        self.cert = cert
        self.cap_score = 0.0
        self.expected_latency = 0.05
        self.history = []

    def verify_integrity(self, packet, secret_index):
        sent_ts = packet['ts']
        current_ts = time.time()
        delay = current_ts - sent_ts
        if delay > (self.expected_latency * 2):
            print(f"[WARNING] Temporal Deviation: {delay:.4f}s. Possible Injection!")
            self.cap_score += 0.15
            return "RE_VERIFY_REQUIRED"
        return "INTEGRITY_PASSED"
