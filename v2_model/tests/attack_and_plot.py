import matplotlib.pyplot as plt
import time, random, os
from v2_model.core.crypto.pqc import PQEngine
from v2_model.agents.grid_node import SmartGridNode

def run_verified_simulation():
    engine = PQEngine()
    mac = "00:1A:22:3B:44:EE"
    node = SmartGridNode("NODE_ALPHA", engine.generate_node_cert("NODE_ALPHA", mac), mac)
    
    print("🚀 Starting High-Assurance Simulation...")
    results = []

    for t in range(40):
        # Normal (0-10) -> DDoS (10-25) -> Recovery (25-40)
        rate = random.randint(100, 300) if t < 10 or t > 25 else random.randint(4000, 6000)
        
        # Verify and Monitor
        pkt = {"ts": time.time()}
        status = node.verify_full_stack(pkt, mac, engine)
        results.append((t, rate, node.cap_score, node.data_locked))
        time.sleep(0.05)

    # Plotting Logic
    times, rates, caps, locks = zip(*results)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    ax1.set_xlabel('Simulation Time (s)')
    ax1.set_ylabel('Traffic Rate (pkt/s)', color='blue')
    ax1.fill_between(times, rates, color='blue', alpha=0.1)
    ax1.plot(times, rates, color='blue', label='DDoS Load')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Agent CAP Score', color='red')
    ax2.plot(times, caps, color='red', linewidth=2, label='Agent Pressure')
    ax2.axhline(y=1.0, color='black', linestyle='--', label='Security Threshold')
    
    plt.title('Aegis-Grid V2.0: Agentic Fail-Secure Response')
    plt.savefig('v2_model/plots/ddos_response_latest.png')
    print("✅ Simulation complete. Plot saved to v2_model/plots/")

if __name__ == "__main__":
    run_verified_simulation()
