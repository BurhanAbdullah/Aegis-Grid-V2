from v2_model.core.crypto.pqc import PQEngine
from v2_model.agents.grid_node import SmartGridNode
import time

def run_simulation():
    print("\n" + "="*50)
    print("AEGIS-GRID V2.0: FULL 7-LAYER ADVERSARIAL SIMULATION")
    print("="*50)
    
    pqc = PQEngine()
    node = SmartGridNode("GRID_METER_PQ_01", pqc.generate_cert("GRID_METER_PQ_01"))
    print(f"L1: PQ-Identity Initialized. Root Hash: {node.cert[:16]}...")

    print("\n[SCENARIO 1] Normal Operation (Shannon Stealth)")
    packet = node.transmit("TELEMETRY: 240V_SAFE")
    encrypted = pqc.encrypt_frame(packet['data'], node.cert)
    print(f"L4 Shannon Stealth: Encrypted Data ({encrypted[:8]}) mirrored by Dummy Noise ({packet['noise'][:8]})")

    print("\n[SCENARIO 2] Adversarial DDoS (L5/L6)")
    for sec in range(1, 6):
        status = node.process_traffic(packet_rate=5000)
        print(f"T+{sec}s | CAP Score: {node.cap_score:.2f} | Agent Status: {status}")
        if node.is_locked:
            print("\nRESULT: Fail-Secure Lockout Active. L7 Isolation Confirmed.")
            break
    print("="*50 + "\n")

if __name__ == "__main__":
    run_simulation()
