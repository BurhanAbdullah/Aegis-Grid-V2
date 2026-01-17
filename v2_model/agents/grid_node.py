import time
import os

class SmartGridNode:
    def __init__(self, node_id, cert):
        self.node_id = node_id
        self.cert = cert
        self.current_key_material = cert['cert_sig']
        self.cap_score = 0.0
        self.expected_latency = 0.05
        self.handshake_count = 0

    def rotate_keys(self, engine):
        """L3/L7: Forces a re-verification handshake"""
        new_salt = os.urandom(8).hex()
        self.current_key_material = engine.derive_sub_key(self.cert['cert_sig'], new_salt)
        self.handshake_count += 1
        return f"HANDSHAKE_SUCCESS_V{self.handshake_count}"

    def verify_integrity(self, packet, secret_index, engine):
        sent_ts = packet['ts']
        current_ts = time.time()
        delay = current_ts - sent_ts

        if delay > (self.expected_latency * 2):
            print(f"[ALERT] Injection Risk! Delay: {delay:.4f}s. Triggering Re-Verification...")
            self.cap_score += 0.2
            self.rotate_keys(engine)
            return "RE_VERIFIED_NEW_KEY_ENGAGED"
            
        return "INTEGRITY_PASSED"
