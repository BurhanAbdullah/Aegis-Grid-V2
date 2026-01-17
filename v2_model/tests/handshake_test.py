from v2_model.core.crypto.pqc import PQEngine
from v2_model.agents.grid_node import SmartGridNode
import time

def test_key_rotation_on_attack():
    pqc = PQEngine()
    node = SmartGridNode("GRID_BETA", pqc.generate_node_cert("GRID_BETA"))
    
    print("\n--- AEGIS-GRID V2.0: AGENTIC HANDSHAKE AUDIT ---")
    initial_key = node.current_key_material
    
    # Simulate an Injection Attack (High Delay)
    tx_slow = {"payload_burst": ["dummy"]*8, "ts": time.time() - 0.5}
    result = node.verify_integrity(tx_slow, 2, pqc)
    
    print(f"Agent Decision: {result}")
    
    if node.current_key_material != initial_key:
        print("L7 Isolation: Success. Session key rotated autonomously.")
        print(f"New Key Material: {node.current_key_material[:16]}...")
    else:
        print("L7 Isolation: Failed. System still using compromised key.")

if __name__ == "__main__":
    test_key_rotation_on_attack()
