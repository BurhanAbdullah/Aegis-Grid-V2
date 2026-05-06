import pandapower as pp
import pandapower.networks as pn
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# Load IEEE test case
# Change here:
#   pn.case9()
#   pn.case14()
#   pn.case30()
#   pn.case118()
# ---------------------------------------------------------
net = pn.case14()

# ---------------------------------------------------------
# Run baseline power flow
# ---------------------------------------------------------
pp.runpp(net)

# Save baseline voltages
baseline_vm = net.res_bus.vm_pu.copy()

# ---------------------------------------------------------
# Inject localized attack
# ---------------------------------------------------------
ATTACK_BUS = 5

if ATTACK_BUS in net.load.bus.values:
    attacked_loads = net.load[net.load.bus == ATTACK_BUS].index

    for idx in attacked_loads:
        net.load.at[idx, "p_mw"] *= 2.5
        net.load.at[idx, "q_mvar"] *= 2.0

# ---------------------------------------------------------
# Re-run power flow
# ---------------------------------------------------------
pp.runpp(net)

# ---------------------------------------------------------
# Voltage deviation
# ---------------------------------------------------------
delta_v = abs(net.res_bus.vm_pu - baseline_vm)

# ---------------------------------------------------------
# Bus coloring
# ---------------------------------------------------------
colors = []

for i, dv in enumerate(delta_v):

    if i == ATTACK_BUS:
        colors.append("red")

    elif dv > 0.03:
        colors.append("orange")

    elif dv > 0.01:
        colors.append("yellow")

    else:
        colors.append("skyblue")

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------
plt.figure(figsize=(12,8))

plot.simple_plot(
    net,
    bus_color=colors,
    bus_size=1.2,
    line_width=1.5,
    show_plot=False
)

plt.title(
    f"IEEE Grid Localized Load Attack Visualization\n"
    f"Attack Bus = {ATTACK_BUS}"
)

# ---------------------------------------------------------
# Save figure
# ---------------------------------------------------------
outfile = "visualization/outputs/case14_localized_attack.png"

plt.savefig(outfile, dpi=300, bbox_inches="tight")

print(f"Saved: {outfile}")
