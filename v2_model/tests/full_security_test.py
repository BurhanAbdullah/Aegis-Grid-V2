from v2_model.core.crypto.pqc import PQEngine
from v2_model.agents.grid_node import SmartGridNode
import time

def run_comprehensive_test():
    engine = PQEngine()
    REAL_MAC = "00:1A:2B:3C:4D:5E"
    FAKE_MAC = "FF:EE:DD:CC:BB:AA"
    
    node = SmartGridNode("GRID_NODE_01", engine.generate_node_cert("GRID_NODE_01", REAL_MAC), REAL_MAC)
    
    print("\n--- AEGIS-GRID V2.0: FULL STACK SECURITY AUDIT ---")

    # Test 1: Authorized Access
    print("\n[Test 1] Authorized Packet (Correct MAC + Time):")
    pkt1 = {"ts": time.time()}
    print(f"Result: {node.verify_full_stack(pkt1, REAL_MAC, engine)}")

    # Test 2: MAC Spoofing Attempt
    print("\n[Test 2] Adversary MAC Spoofing Attempt:")
    pkt2 = {"ts": time.time()}
    print(f"Result: {node.verify_full_stack(pkt2, FAKE_MAC, engine)}")
    
    if node.data_locked:
        print("L6 Status: DATA_LOCKED (System isolated due to hardware mismatch)")

    # Test 3: Log Review
    print("\n--- SECURE AUDIT LOG ---")
    for entry in engine.audit_log:
        print(entry)

if __name__ == "__main__":
    run_comprehensive_test()
