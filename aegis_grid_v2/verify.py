from .aegis_v2_core.agents.pq_agent import AegisV2Agent
import time

def run_v2_audit():
    print("Initializing V2 Post-Quantum Audit...")
    agent = AegisV2Agent("INTERNAL_KEY_ROOT")
    
    # Test 1: Freshness
    success, msg = agent.validate_quantum_frame(b"test", time.time(), "sig_test")
    status = "PASS" if success else "FAIL"
    print(f"Layer 1-7 Integrity: {status} ({msg})")

if __name__ == "__main__":
    run_v2_audit()
