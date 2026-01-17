import matplotlib.pyplot as plt
import os

versions = ['V2.1', 'V2.2', 'V3.0', 'V4.0']
latency = [344, 89, 25, 11]
stability = [82.4, 91.2, 97.8, 99.9]

fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.set_xlabel('Station Evolution')
ax1.set_ylabel('Latency (ms)', color='tab:red')
ax1.plot(versions, latency, color='tab:red', marker='o', linewidth=3)
ax1.tick_params(axis='y', labelcolor='tab:red')

ax2 = ax1.twinx()
ax2.set_ylabel('Stability (%)', color='tab:green')
ax2.bar(versions, stability, color='tab:green', alpha=0.3)
ax2.set_ylim(80, 105)

plt.title('V4.0 HIVE-CELL: FINAL FORENSIC PERFORMANCE')
plt.savefig('research_docs/FINAL_STRESS_RESULTS.png')
