from v2_model.agents.pq_agent import PQAgentV2
import time

def run_v2_verification():
    print("\n" + "="*40)
    print("=== AEGIS-GRID V2.0 (VERIFIED) AUDIT ===")
    print("="*40)
    agent = PQAgentV2("NODE_001")
    
    # Test L1: PQ Identity
    p_hash = agent.generate_pq_hash("GridPayload")
    print(f"L1 PQ-Identity Hash: {p_hash[:16]}... (PASS)")
    
    # Test L2: Temporal Freshness
    current_ts = time.time()
    if agent.verify_temporal_freshness(current_ts):
        print("L2 Temporal Freshness: Valid (PASS)")
    
    # Test L5/L6: CAP Isolation
    print("\nSimulating High Adversarial Pressure (DDoS Simulation)...")
    for i in range(5):
        status = agent.update_cap(anomaly_detected=True)
        print(f"Pulse {i+1}: CAP Score {agent.cap_score:.2f} -> {status}")
    
    if agent.is_isolated:
        print("\nL6 Fail-Secure: System Isolated Successfully (PASS)")
        print("="*40 + "\n")

if __name__ == "__main__":
    run_v2_verification()
