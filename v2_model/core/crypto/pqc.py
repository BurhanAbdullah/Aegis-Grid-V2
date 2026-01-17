import hashlib
import os
import time

class PQEngine:
    def __init__(self):
        # L1: Master Key (Root of Trust)
        self.master_key = os.urandom(64) 
        
    def generate_node_cert(self, node_id):
        """Generates a Time-Bounded PQ Certificate"""
        timestamp = str(int(time.time())).encode()
        cert_sig = hashlib.shake_256(self.master_key + node_id.encode() + timestamp).hexdigest(32)
        return {"node_id": node_id, "cert_sig": cert_sig, "issued_at": timestamp}

    def encrypt_payload(self, data, cert_sig):
        """L4: AES-256-GCM Simulation using SHAKE-256 derived keys"""
        session_key = hashlib.sha3_256(cert_sig.encode()).digest()
        # Simulated high-entropy ciphertext
        return hashlib.sha3_256(data.encode() + session_key).hexdigest()
