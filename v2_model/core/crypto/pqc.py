import hashlib
import os
import random
import time

class PQEngine:
    def __init__(self):
        self.master_key = os.urandom(64) 
        
    def generate_node_cert(self, node_id):
        timestamp = str(int(time.time())).encode()
        cert_sig = hashlib.shake_256(self.master_key + node_id.encode() + timestamp).hexdigest(32)
        return {"node_id": node_id, "cert_sig": cert_sig, "issued_at": timestamp}

    def encrypt_and_shuffle(self, data, cert_sig, seq_num):
        session_key = hashlib.sha3_256(cert_sig.encode()).digest()
        payload = f"{seq_num}|{data}|{time.time()}".encode()
        encrypted_data = hashlib.sha3_256(payload + session_key).hexdigest()
        package = [os.urandom(32).hex() for _ in range(7)]
        package.append(encrypted_data)
        random.shuffle(package)
        return package, package.index(encrypted_data)
