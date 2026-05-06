import pandapower as pp
import pandapower.networks as pn

import networkx as nx
import plotly.graph_objects as go
import numpy as np
import os

# ======================================================
# Load IEEE case
# ======================================================
net = pn.case14()

# ======================================================
# Baseline PF
# ======================================================
pp.runpp(net)

baseline_vm = net.res_bus.vm_pu.copy()

# ======================================================
# Attack Injection
# ======================================================
ATTACK_BUS = 5

for idx in net.load.index:

    if net.load.at[idx, "bus"] == ATTACK_BUS:

        net.load.at[idx, "p_mw"] *= 2.5
        net.load.at[idx, "q_mvar"] *= 2.0

# ======================================================
# Re-run PF
# ======================================================
pp.runpp(net)

# ======================================================
# Voltage deviation
# ======================================================
delta_v = abs(net.res_bus.vm_pu - baseline_vm)

# ======================================================
# Build graph
# ======================================================
G = nx.Graph()

for _, row in net.line.iterrows():

    G.add_edge(
        int(row["from_bus"]),
        int(row["to_bus"])
    )

# ======================================================
# Layout
# ======================================================
pos = nx.spring_layout(G, seed=42, dim=3)

# ======================================================
# Nodes
# ======================================================
x_nodes = []
y_nodes = []
z_nodes = []

colors = []

for node in G.nodes():

    x, y, _ = pos[node]

    anomaly = float(delta_v[node]) * 100

    x_nodes.append(x)
    y_nodes.append(y)
    z_nodes.append(anomaly)

    if node == ATTACK_BUS:
        colors.append("red")

    elif anomaly > 2:
        colors.append("orange")

    else:
        colors.append("skyblue")

# ======================================================
# Edges
# ======================================================
edge_x = []
edge_y = []
edge_z = []

for edge in G.edges():

    x0, y0, _ = pos[edge[0]]
    x1, y1, _ = pos[edge[1]]

    z0 = z_nodes[edge[0]]
    z1 = z_nodes[edge[1]]

    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_z += [z0, z1, None]

# ======================================================
# Plot
# ======================================================
fig = go.Figure()

# edges
fig.add_trace(
    go.Scatter3d(
        x=edge_x,
        y=edge_y,
        z=edge_z,
        mode='lines',
        line=dict(width=2, color='gray'),
        hoverinfo='none'
    )
)

# nodes
fig.add_trace(
    go.Scatter3d(
        x=x_nodes,
        y=y_nodes,
        z=z_nodes,
        mode='markers+text',
        text=[f"Bus {n}" for n in G.nodes()],
        textposition="top center",
        marker=dict(
            size=8,
            color=colors
        )
    )
)

fig.update_layout(
    title="3D Localized Load Attack Propagation",
    scene=dict(
        xaxis_title="Grid X",
        yaxis_title="Grid Y",
        zaxis_title="Anomaly Severity"
    ),
    margin=dict(l=0, r=0, b=0, t=50)
)

# ======================================================
# Save HTML
# ======================================================
os.makedirs("visualization/3d", exist_ok=True)

outfile = "visualization/3d/case14_3d_attack.html"

fig.write_html(outfile)

print(f"Saved: {outfile}")
