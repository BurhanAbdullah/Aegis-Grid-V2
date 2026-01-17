from v2_model.core.crypto.pqc import PQEngine
from v2_model.agents.grid_node import SmartGridNode
import matplotlib.pyplot as plt
import time

def run_stress_test():
    pqc = PQEngine()
    node = SmartGridNode("GRID_METER_01", pqc.generate_node_cert("GRID_METER_01"))
    
    print("Starting DDoS Stress Test (Layer 5/6 Verification)...")
    
    # 1. Simulate Variable Traffic
    for t in range(30):
        # 0-10s: Normal | 10-20s: DDoS | 20-30s: Recovery/Lockout
        if 10 <= t <= 25:
            rate = 5000 + random.randint(-500, 500)
        else:
            rate = 200 + random.randint(-50, 50)
            
        status = node.process_traffic(rate)
        time.sleep(0.05)

    # 2. Extract Data for Plotting
    times, rates, scores = zip(*node.history)
    relative_times = [x - times[0] for x in times]

    # 3. Generate Dual-Axis Plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Packet Rate (pkt/s)', color='tab:blue')
    ax1.plot(relative_times, rates, color='tab:blue', label='Traffic Rate', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('CAP Score (Agent Pressure)', color='tab:red')
    ax2.plot(relative_times, scores, color='tab:red', linestyle='--', label='CAP Score', linewidth=2)
    ax2.axhline(y=1.0, color='black', linestyle=':', label='Lockout Threshold')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('Aegis-Grid V2.0: Agentic Response to DDoS Attack')
    fig.tight_layout()
    plt.savefig('ddos_defense_plot.png')
    print("Test Complete. Plot saved as 'ddos_defense_plot.png'.")

if __name__ == "__main__":
    run_stress_test()
