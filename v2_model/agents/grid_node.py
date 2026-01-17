import time
import os

class SmartGridNode:
    def __init__(self, node_id, cert, mac_id):
        self.node_id = node_id
        self.cert = cert
        self.registered_mac = mac_id
        self.current_key_material = cert['cert_sig']
        self.cap_score = 0.0
        self.data_locked = False # L6: Data Lock state

    def verify_full_stack(self, packet, incoming_mac, engine):
        """
        L1: MAC ID Verification
        L2: Temporal Validation
        L6: Data Lock Persistence
        """
        # 1. MAC Verification
        if incoming_mac != self.registered_mac:
            engine.log_event("critical", f"MAC Spoofing detected from {incoming_mac}")
            self.data_locked = True
            return "TERMINAL_HARDWARE_MISMATCH"

        # 2. Temporal/Delay Check
        delay = time.time() - packet['ts']
        if delay > 2.0:
            engine.log_event("warning", f"Latency spike ({delay:.2f}s) on Node {self.node_id}")
            self.cap_score += 0.3
            if self.cap_score >= 1.0:
                self.data_locked = True
            return "TEMPORAL_ANOMALY"

        engine.log_event("info", f"Packet verified for {self.node_id}")
        return "SUCCESS"
