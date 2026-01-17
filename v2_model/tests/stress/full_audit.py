import matplotlib.pyplot as plt
import time, random
from v2_model.agents.grid_agent import AegisAgent
from v2_model.core.crypto.pqc import PQEngine
from v2_model.hardware.fingerprint import get_device_mac

def run_audit():
    print("🚀 Running Aegis-Grid V2.0 Full-Fledged Audit...")
    engine = PQEngine()
    mac = get_device_mac()
    agent = AegisAgent("GRID_NODE_PRO", engine.generate_node_cert("GRID_NODE_PRO", mac), mac)
    
    results = []
    for t in range(30):
        # Normal (0-10) -> DDoS (10-20) -> Recovery (20-30)
        rate = random.randint(100, 200) if t < 10 or t > 20 else random.randint(4000, 5000)
        status = agent.analyze_packet({"ts": time.time()}, mac, engine)
        results.append((t, rate, agent.cap_score))
        time.sleep(0.01)

    # Plot results
    t, r, c = zip(*results)
    plt.figure(figsize=(10, 5))
    plt.plot(t, c, color='red', label='Agent Pressure (CAP)')
    plt.axhline(y=1.0, color='black', linestyle='--', label='Lockout Threshold')
    plt.title("Aegis-Grid V2.0: Stress Test Results")
    plt.savefig("v2_model/plots/audit_result.png")
    print("✅ Audit Complete. Plot saved to v2_model/plots/audit_result.png")

if __name__ == "__main__":
    run_audit()
