from v2_model.core.crypto.pqc import PQEngine
from v2_model.agents.grid_node import SmartGridNode
import time

def test_integrity_and_delay():
    pqc = PQEngine()
    node = SmartGridNode("GRID_ALPHA", pqc.generate_node_cert("GRID_ALPHA"))
    print("\n--- AEGIS-GRID V2.0: INTEGRITY & DELAY AUDIT ---")

    # Test 1: Fast Packet
    tx_fast = {"payload_burst": ["dummy"]*8, "ts": time.time()}
    print(f"\n[Test 1] Normal Packet: {node.verify_integrity(tx_fast, 3)}")

    # Test 2: Delayed Packet (Attack Simulation)
    tx_slow = {"payload_burst": ["dummy"]*8, "ts": time.time() - 0.5}
    print(f"\n[Test 2] Delayed Packet: {node.verify_integrity(tx_slow, 5)}")

if __name__ == "__main__":
    test_integrity_and_delay()
