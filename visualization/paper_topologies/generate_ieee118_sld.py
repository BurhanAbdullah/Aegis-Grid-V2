import os
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pypower.api import case118

# ================================================================
# IEEE 118-BUS TEST SYSTEM — TRANSACTIONS-STYLE TOPOLOGY FIGURE
# ================================================================
# Electrical topology/data: PYPOWER case118()
# Coordinates: visualization only.
# Attack: branch 1-2, X_ij^att = 1.10 X_ij
#
# 118-bus design:
#   * exact electrical branch records are preserved;
#   * bus numbers remain visible;
#   * generator/load symbols are compact;
#   * Gxx/L labels are intentionally removed from individual nodes;
#   * attacked branch is a red dashed overlay;
#   * legend carries the symbol meanings.
# ================================================================

OUT = os.path.dirname(os.path.abspath(__file__))

mpc = case118()
bus = np.asarray(mpc["bus"], dtype=float)
branch = np.asarray(mpc["branch"], dtype=float)
gen = np.asarray(mpc["gen"], dtype=float)

# PYPOWER / MATPOWER columns
BUS_I = 0
PD = 2
QD = 3
GEN_BUS = 0
GEN_STATUS = 7
F_BUS = 0
T_BUS = 1
BR_STATUS = 10

# ================================================================
# VALIDATION
# ================================================================

assert len(bus) == 118, "Expected IEEE 118-bus system."
assert len(branch) == 186, "Expected 186 branch records."

bus_ids = bus[:, BUS_I].astype(int)
assert len(bus_ids) == 118
assert len(set(bus_ids)) == 118

# Keep branch records separately.  Do NOT use Graph edge count as
# the electrical branch count because a simple Graph can collapse
# parallel records.
active_edges = []
for row in branch:
    if row[BR_STATUS] > 0:
        active_edges.append((int(row[F_BUS]), int(row[T_BUS])))

assert len(active_edges) == 186, "Expected 186 active branches."

# Generator buses
generator_buses = []
for row in gen:
    if row[GEN_STATUS] > 0:
        b = int(row[GEN_BUS])
        if b not in generator_buses:
            generator_buses.append(b)

# Load buses
load_buses = []
for row in bus:
    b = int(row[BUS_I])
    if abs(float(row[PD])) > 1e-10 or abs(float(row[QD])) > 1e-10:
        load_buses.append(b)

# ================================================================
# GRAPH FOR LAYOUT ONLY
# ================================================================

G = nx.Graph()
G.add_nodes_from(int(b) for b in bus_ids)
G.add_edges_from(active_edges)

assert G.number_of_nodes() == 118

print("Generating collision-aware IEEE 118-bus layout...")

pos_nx = nx.spring_layout(
    G,
    seed=118,
    k=1.15,
    iterations=4000,
    threshold=1e-6,
    scale=1.0,
    weight=None,
)

nodes = sorted(G.nodes())
P = np.asarray([pos_nx[b] for b in nodes], dtype=float)

# ================================================================
# COLLISION RELAXATION
# ================================================================

def relax_nodes(points, minimum_distance=0.165, iterations=420,
                strength=0.28):
    points = points.copy()
    n = len(points)

    for _ in range(iterations):
        displacement = np.zeros_like(points)

        for i in range(n):
            for j in range(i + 1, n):
                d = points[i] - points[j]
                dist = np.linalg.norm(d)

                if dist < 1e-10:
                    angle = 2.0 * np.pi * ((i + 1) / (n + 1))
                    d = np.array([np.cos(angle), np.sin(angle)])
                    dist = 1e-10

                if dist < minimum_distance:
                    amount = minimum_distance - dist
                    direction = d / dist
                    displacement[i] += 0.5 * amount * direction
                    displacement[j] -= 0.5 * amount * direction

        points += strength * displacement

    return points

P = relax_nodes(P)

# Normalize
P[:, 0] -= P[:, 0].min()
P[:, 1] -= P[:, 1].min()
P[:, 0] /= max(P[:, 0].max(), 1e-12)
P[:, 1] /= max(P[:, 1].max(), 1e-12)

# ================================================================
# PUBLICATION CANVAS
# ================================================================

XMIN, XMAX = 0.85, 20.15
YMIN, YMAX = 1.10, 10.15

P[:, 0] = XMIN + P[:, 0] * (XMAX - XMIN)
P[:, 1] = YMIN + P[:, 1] * (YMAX - YMIN)

POS = {
    int(b): (float(P[i, 0]), float(P[i, 1]))
    for i, b in enumerate(nodes)
}

# ================================================================
# FIGURE
# ================================================================

fig, ax = plt.subplots(figsize=(21.0, 12.0))
ax.set_aspect("equal")
ax.axis("off")

# Compact 118-bus visual language
BUSBAR_LENGTH = 0.22
BUSBAR_WIDTH = 1.7
BRANCH_WIDTH = 0.50
ATTACK_WIDTH = 1.65
GEN_RADIUS = 0.070
LOAD_SIZE = 0.105
BUS_FONT = 4.4

# ================================================================
# DRAWING HELPERS
# ================================================================

def draw_busbar(ax, x, y):
    ax.plot(
        [x - BUSBAR_LENGTH / 2, x + BUSBAR_LENGTH / 2],
        [y, y],
        color="black",
        linewidth=BUSBAR_WIDTH,
        solid_capstyle="butt",
        zorder=5,
    )

def outward_direction(b):
    """Return a stable outward direction for compact generator/load markers."""
    x, y = POS[b]
    neighbours = list(G.neighbors(b))

    if neighbours:
        nbr = np.asarray([POS[n] for n in neighbours], dtype=float)
        v = np.asarray([x, y]) - nbr.mean(axis=0)
    else:
        v = np.asarray([x, y]) - P.mean(axis=0)

    norm = np.linalg.norm(v)
    if norm < 1e-9:
        # Deterministic direction based on bus number.
        theta = 2.0 * np.pi * ((b % 17) / 17.0)
        v = np.array([np.cos(theta), np.sin(theta)])
        norm = 1.0

    return v / norm


def draw_generator(ax, x, y, direction):
    """Tiny generator marker offset from the bus; no text label."""
    dx, dy = direction
    stem = 0.105
    cx = x + dx * stem
    cy = y + dy * stem

    ax.plot(
        [x, cx],
        [y, cy],
        color="black",
        linewidth=0.38,
        zorder=6,
    )

    ax.add_patch(
        plt.Circle(
            (cx, cy),
            GEN_RADIUS,
            facecolor="white",
            edgecolor="black",
            linewidth=0.55,
            zorder=11,
        )
    )


def draw_load(ax, x, y, direction):
    """Tiny load marker offset from the bus; no text label."""
    dx, dy = direction
    stem = 0.095
    cx = x + dx * stem
    cy = y + dy * stem

    ax.plot(
        [x, cx],
        [y, cy],
        color="black",
        linewidth=0.34,
        zorder=6,
    )

    ax.add_patch(
        plt.Rectangle(
            (cx - LOAD_SIZE / 2, cy - LOAD_SIZE / 2),
            LOAD_SIZE,
            LOAD_SIZE,
            facecolor="white",
            edgecolor="black",
            linewidth=0.48,
            zorder=11,
        )
    )


# ================================================================
# TRANSMISSION BRANCHES
# ================================================================

ATTACK_FROM = 1
ATTACK_TO = 2

for f, t in active_edges:

    if {f, t} == {ATTACK_FROM, ATTACK_TO}:
        continue

    x1, y1 = POS[f]
    x2, y2 = POS[t]

    ax.plot(
        [x1, x2],
        [y1, y2],
        color="black",
        linewidth=BRANCH_WIDTH,
        solid_capstyle="round",
        zorder=1,
    )

# Attacked branch
x1, y1 = POS[ATTACK_FROM]
x2, y2 = POS[ATTACK_TO]

ax.plot(
    [x1, x2],
    [y1, y2],
    color="red",
    linewidth=ATTACK_WIDTH,
    linestyle="--",
    solid_capstyle="round",
    zorder=7,
)

# Attack marker
mx = 0.5 * (x1 + x2)
my = 0.5 * (y1 + y2)

ax.scatter(
    [mx],
    [my],
    s=72,
    facecolors="white",
    edgecolors="red",
    linewidths=1.1,
    zorder=12,
)

ax.text(
    mx,
    my,
    "A",
    ha="center",
    va="center",
    color="red",
    fontsize=4.8,
    fontweight="bold",
    zorder=13,
)

# ================================================================
# BUSBARS + BUS NUMBERS
# ================================================================

for b in nodes:

    x, y = POS[b]

    draw_busbar(ax, x, y)

    # White halo keeps bus numbers readable over nearby branches.
    ax.text(
        x,
        y + 0.075,
        str(b),
        ha="center",
        va="bottom",
        fontsize=BUS_FONT,
        fontweight="bold",
        color="black",
        zorder=14,
        bbox=dict(
            boxstyle="round,pad=0.025",
            facecolor="white",
            edgecolor="none",
            alpha=0.88,
        ),
    )

# ================================================================
# GENERATOR / LOAD SYMBOLS
# ================================================================
# Deliberately no Gxx/L text at 118-bus scale.  The legend identifies
# the symbols, which removes the label collisions visible in the old
# figure.

for b in generator_buses:
    d = outward_direction(b)
    draw_generator(ax, *POS[b], d)

for b in load_buses:
    d = outward_direction(b)

    if b in generator_buses:
        d = -d

    draw_load(ax, *POS[b], d)

# ================================================================
# TITLE
# ================================================================

ax.text(
    10.5,
    11.02,
    "IEEE 118-bus test system",
    ha="center",
    va="center",
    fontsize=17,
    fontweight="bold",
)

# ================================================================
# ATTACK CALLOUT
# ================================================================

ax.text(
    15.20,
    10.72,
    "STEALTH ATTACK",
    color="red",
    fontsize=10.5,
    fontweight="bold",
    ha="left",
    va="center",
    bbox=dict(facecolor="white", edgecolor="none", pad=3.0),
)

ax.text(
    15.20,
    10.43,
    r"Branch 1--2:  $X_{ij}^{att}=1.10X_{ij}$",
    fontsize=8.2,
    ha="left",
    va="center",
)

ax.text(
    15.20,
    10.17,
    "Red dashed overlay = attacked branch",
    color="red",
    fontsize=7.2,
    ha="left",
    va="center",
)

# ================================================================
# LEGEND
# ================================================================

# Dedicated white legend band to prevent network/legend collisions.
ax.add_patch(
    plt.Rectangle(
        (11.75, 0.12),
        8.85,
        0.72,
        facecolor="white",
        edgecolor="none",
        zorder=20,
    )
)

legend_y = 0.42
legend_x = 13.10

ax.plot(
    [legend_x, legend_x + 0.40],
    [legend_y, legend_y],
    color="black",
    linewidth=1.15,
)

ax.text(
    legend_x + 0.52,
    legend_y,
    "Transmission branch",
    fontsize=7.2,
    va="center",
)

ax.plot(
    [legend_x, legend_x + 0.40],
    [legend_y - 0.28, legend_y - 0.28],
    color="red",
    linewidth=1.8,
    linestyle="--",
)

ax.text(
    legend_x + 0.52,
    legend_y - 0.28,
    "Attacked branch",
    fontsize=7.2,
    va="center",
)

gx = legend_x + 2.65

ax.add_patch(
    plt.Circle(
        (gx, legend_y),
        0.070,
        facecolor="white",
        edgecolor="black",
        linewidth=0.65,
    )
)

ax.text(
    gx + 0.18,
    legend_y,
    "Generator",
    fontsize=7.2,
    va="center",
)

lx = gx
ly = legend_y - 0.28

ax.add_patch(
    plt.Rectangle(
        (lx - 0.065, ly - 0.045),
        0.13,
        0.09,
        facecolor="white",
        edgecolor="black",
        linewidth=0.55,
    )
)

ax.text(
    lx + 0.18,
    ly,
    "Load",
    fontsize=7.2,
    va="center",
)

# ================================================================
# SUMMARY / ATTACK MODEL
# ================================================================

summary = (
    f"{len(bus)} buses  |  "
    f"{len(active_edges)} branches  |  "
    f"{len(generator_buses)} generators  |  "
    f"{len(load_buses)} load buses"
)

ax.text(
    0.75,
    0.42,
    summary,
    fontsize=7.7,
    ha="left",
    va="center",
)

ax.text(
    8.0,
    0.42,
    r"Attack model: $X_{ij}^{att}=1.10X_{ij}$",
    fontsize=7.7,
    ha="center",
    va="center",
)

# ================================================================
# LIMITS / SAVE
# ================================================================

ax.set_xlim(0.45, 21.0)
ax.set_ylim(0.05, 11.35)

plt.tight_layout(pad=0.25)

pdf_path = os.path.join(OUT, "ieee118_sld.pdf")
png_path = os.path.join(OUT, "ieee118_sld.png")

fig.savefig(
    pdf_path,
    bbox_inches="tight",
    pad_inches=0.04,
)

fig.savefig(
    png_path,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.04,
)

plt.close(fig)

# ================================================================
# FINAL REPORT
# ================================================================

print("=" * 70)
print("IEEE 118-BUS TRANSACTIONS-STYLE SLD GENERATED")
print("=" * 70)
print(f"Buses          : {len(bus)}")
print(f"Branches       : {len(active_edges)}")
print(f"Generators     : {len(generator_buses)}")
print(f"Load buses     : {len(load_buses)}")
print(f"Attack branch  : {ATTACK_FROM} -> {ATTACK_TO}")
print("Attack model   : X_ij -> 1.10 X_ij")
print()
print(f"PDF            : {pdf_path}")
print(f"PNG            : {png_path}")
print("=" * 70)