from v2_model.core.crypto.pqc import PQEngine
from v2_model.agents.grid_node import SmartGridNode

def test_dynamic_shuffling():
    pqc = PQEngine()
    node = SmartGridNode("GRID_NODE_ALPHA", pqc.generate_node_cert("GRID_NODE_ALPHA"))
    
    print("--- AEGIS-GRID V2.0: DYNAMIC SHUFFLING AUDIT ---")
    
    indices = []
    for i in range(5):
        tx = node.prepare_transmission("COMMAND: OPEN_CIRCUIT_01", pqc)
        indices.append(tx['metadata_index'])
        print(f"Packet {i+1} | Data hidden at Index: {tx['metadata_index']} | Burst Size: {len(tx['payload_burst'])}")
    
    if len(set(indices)) > 1:
        print("\nRESULT: Success. Data position randomized per packet (L4 Stealth).")
    else:
        print("\nRESULT: Failed. Data position is static.")

if __name__ == "__main__":
    test_dynamic_shuffling()
