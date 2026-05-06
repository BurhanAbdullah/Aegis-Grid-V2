import pandapower as pp
import pandapower.networks as pn
import pandapower.plotting as plot

import matplotlib.pyplot as plt
import numpy as np
import os

# =========================================================
# Cases
# =========================================================
CASES = {
    "case9": pn.case9,
    "case14": pn.case14,
    "case30": pn.case30,
    "case118": pn.case118,
}

# =========================================================
# Output directory
# =========================================================
OUTDIR = "visualization/outputs"
os.makedirs(OUTDIR, exist_ok=True)

# =========================================================
# Loop all IEEE cases
# =========================================================
for case_name, case_fn in CASES.items():

    print(f"\nProcessing {case_name}")

    # -----------------------------------------------------
    # Load network
    # -----------------------------------------------------
    net = case_fn()

    # -----------------------------------------------------
    # Baseline PF
    # -----------------------------------------------------
    pp.runpp(net)

    baseline_vm = net.res_bus.vm_pu.copy()

    # -----------------------------------------------------
    # Choose attack bus
    # -----------------------------------------------------
    attack_bus = int(len(net.bus) * 0.4)

    # -----------------------------------------------------
    # Inject localized load attack
    # -----------------------------------------------------
    attacked = False

    for idx in net.load.index:

        if net.load.at[idx, "bus"] == attack_bus:

            net.load.at[idx, "p_mw"] *= 2.5
            net.load.at[idx, "q_mvar"] *= 2.0
            attacked = True

    # fallback if no load at chosen bus
    if not attacked and len(net.load):

        idx = net.load.index[0]

        attack_bus = int(net.load.at[idx, "bus"])

        net.load.at[idx, "p_mw"] *= 2.5
        net.load.at[idx, "q_mvar"] *= 2.0

    # -----------------------------------------------------
    # Re-run PF
    # -----------------------------------------------------
    pp.runpp(net)

    # -----------------------------------------------------
    # Voltage deviation
    # -----------------------------------------------------
    delta_v = abs(net.res_bus.vm_pu - baseline_vm)

    # -----------------------------------------------------
    # Color buses
    # -----------------------------------------------------
    colors = []

    for i, dv in enumerate(delta_v):

        if i == attack_bus:
            colors.append("red")

        elif dv > 0.03:
            colors.append("orange")

        elif dv > 0.015:
            colors.append("yellow")

        else:
            colors.append("skyblue")

    # -----------------------------------------------------
    # Plot
    # -----------------------------------------------------
    plt.figure(figsize=(12,8))

    plot.simple_plot(
        net,
        bus_color=colors,
        bus_size=1.5,
        line_width=1.5,
        show_plot=False
    )

    plt.title(
        f"{case_name.upper()} - Localized Load Attack\n"
        f"Attack Bus: {attack_bus}"
    )

    outfile = f"{OUTDIR}/{case_name}_localized_attack.png"

    plt.savefig(
        outfile,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Saved: {outfile}")

print("\nDone.")
