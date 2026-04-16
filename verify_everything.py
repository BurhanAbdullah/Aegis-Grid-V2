from aegis_v2.core.pq_crypto import LatticeRoot as PQEngine
from aegis_v2.agents.adaptive_agent import AegisAgentV2
from aegis_v2.attacks.simulator import Adversary

def run_full_test():
    engine = PQEngine()
    agent = AegisAgentV2()
    attacker = Adversary()

    print("--- Stage 1: Issuing PQ Certificates ---")
    node_cert = engine.issue_cert("Grid_Node_01")
    print(f"Node Certificate: {node_cert}")

    print("\n--- Stage 2: Starting Dummy Traffic (Shannon Stealth) ---")
    print(f"Noise Injected: {agent.inject_dummies()}")

    print("\n--- Stage 3: Simulating DDoS Attack ---")
    flood_rate = attacker.simulate_flood()
    status = agent.monitor_traffic(flood_rate, 100)
    
    if agent.is_locked:
        print("Result: FAIL-SECURE TRIGGERED. System isolated from DDoS.")

if __name__ == "__main__":
    run_full_test()
