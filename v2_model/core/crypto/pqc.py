import hashlib
import os
import time
import json

class PQEngine:
    def __init__(self):
        self.master_key = os.urandom(64)
        self.log_path = "v2_model/logs/audit_trail.log"

    def log_event(self, event_type, node_id, details):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        entry = f"[{timestamp}] [{event_type.upper()}] Node: {node_id} | {details}\n"
        with open(self.log_path, "a") as f:
            f.write(entry)

    def generate_node_cert(self, node_id, mac_id):
        ts = str(int(time.time())).encode()
        cert_sig = hashlib.shake_256(self.master_key + node_id.encode() + mac_id.encode() + ts).hexdigest(32)
        return {"node_id": node_id, "mac_id": mac_id, "cert_sig": cert_sig}
