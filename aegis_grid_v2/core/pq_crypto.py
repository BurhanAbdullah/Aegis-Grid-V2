import os

class LatticeRoot:

    def __init__(self):
        self.root_seed = os.urandom(32)

    def issue_cert(self, node_id):
        return {
            "node": node_id,
            "certificate": f"LATTICE_CERT::{node_id}",
            "status": "issued"
        }
