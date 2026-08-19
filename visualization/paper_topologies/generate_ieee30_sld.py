import os
import numpy as np
import matplotlib.pyplot as plt
from pypower.api import case30

# ================================================================
# IEEE 30-BUS TEST SYSTEM — PUBLICATION-QUALITY SLD
# ================================================================
#
# Electrical topology:
#     Directly from PYPOWER case30()
#
# Graphical coordinates:
#     Deliberately selected for readability only.
#
# Stealth attack:
#     Branch 1-3
#     X_ij^att = 1.10 X_ij
#
# The attack is shown ONLY as a graphical overlay.
# The underlying electrical topology remains unchanged.
# ================================================================


OUT = os.path.dirname(os.path.abspath(__file__))


# ================================================================
# LOAD IEEE 30-BUS CASE
# ================================================================

mpc = case30()

bus = np.asarray(mpc["bus"], dtype=float)
branch = np.asarray(mpc["branch"], dtype=float)
gen = np.asarray(mpc["gen"], dtype=float)


# ================================================================
# PYPOWER / MATPOWER COLUMN DEFINITIONS
# ================================================================

BUS_I = 0
BUS_TYPE = 1
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

assert len(bus) == 30, "Expected IEEE 30-bus system."
assert len(branch) == 41, "Expected 41 branches."

bus_ids = bus[:, BUS_I].astype(int)

case_buses = set(bus_ids)

# Every bus must have a graphical coordinate.
# The POS dictionary below is checked later.
# ================================================================


# ================================================================
# DELIBERATE PUBLICATION SLD GEOMETRY
# ================================================================
#
# The system is arranged in five electrical corridors.
#
# Upper corridor:
#     1 -- 2 -- 5 -- 7 -- 8
#
# Upper-middle:
#     3 -- 4 -- 6 -- 9 -- 10 -- 11
#
# Middle:
#     12 -- 13 -- 14 -- 15 -- 18 -- 19 -- 20
#
# Lower:
#     16 -- 17       21 -- 22
#
# Bottom:
#     23 -- 24 -- 25 -- 26 -- 27
#                         |
#                         30
#
# Coordinates are NOT electrical data.
# ================================================================

POS = {

    # ------------------------------------------------------------
    # Upper corridor
    # ------------------------------------------------------------

    1:  (0.0,  6.4),
    2:  (3.0,  6.4),
    5:  (6.5,  6.4),
    7:  (10.0, 6.4),
    8:  (13.5, 6.4),

    # ------------------------------------------------------------
    # Upper-middle corridor
    # ------------------------------------------------------------

    3:  (0.8,  4.5),
    4:  (3.8,  4.5),
    6:  (6.8,  4.5),
    9:  (10.0, 4.5),
    10: (13.0, 4.5),
    11: (16.0, 4.5),

    # ------------------------------------------------------------
    # Middle corridor
    # ------------------------------------------------------------

    12: (2.0,  2.5),
    13: (5.0,  2.5),
    14: (8.0,  2.5),
    15: (11.0, 2.5),
    18: (14.0, 2.5),
    19: (17.0, 2.5),
    20: (19.5, 2.5),

    # ------------------------------------------------------------
    # Lower-middle corridor
    # ------------------------------------------------------------

    16: (3.5,  0.3),
    17: (7.0,  0.3),

    21: (12.0, 0.3),
    22: (15.0, 0.3),

    # ------------------------------------------------------------
    # Bottom corridor
    # ------------------------------------------------------------

    23: (8.5, -2.0),
    24: (11.5, -2.0),
    25: (14.5, -2.0),
    26: (17.0, -2.0),
    27: (19.5, -2.0),

    # ------------------------------------------------------------
    # Bottom terminal
    # ------------------------------------------------------------

    28: (17.0, 0.3),
    29: (19.5, -2.0),
    30: (19.5, -4.0),
}


# ================================================================
# CHECK COORDINATES
# ================================================================

if set(POS) != case_buses:

    missing = sorted(case_buses - set(POS))
    extra = sorted(set(POS) - case_buses)

    raise RuntimeError(
        f"Coordinate mismatch. Missing={missing}, Extra={extra}"
    )


# ================================================================
# FIGURE
# ================================================================

fig, ax = plt.subplots(
    figsize=(15.5, 8.8)
)

ax.set_aspect("equal")
ax.axis("off")


# ================================================================
# DRAWING PARAMETERS
# ================================================================

BUSBAR_LENGTH = 0.72
BUSBAR_WIDTH = 4.0

BRANCH_WIDTH = 1.35
ATTACK_WIDTH = 3.0

BUS_LABEL_SIZE = 9.0
GEN_LABEL_SIZE = 9.0

LOAD_WIDTH = 0.52
LOAD_HEIGHT = 0.34


# ================================================================
# DRAW BUSBAR
# ================================================================

def draw_busbar(ax, x, y):

    ax.plot(
        [
            x - BUSBAR_LENGTH / 2,
            x + BUSBAR_LENGTH / 2
        ],
        [
            y,
            y
        ],
        color="black",
        linewidth=BUSBAR_WIDTH,
        solid_capstyle="butt",
        zorder=6,
    )


# ================================================================
# DRAW GENERATOR
# ================================================================

def draw_generator(
    ax,
    x,
    y,
    label,
    direction="up"
):

    r = 0.28

    if direction == "up":

        cy = y + 0.88

        ax.plot(
            [x, x],
            [y + 0.03, cy - r],
            color="black",
            linewidth=1.35,
            zorder=3,
        )

        label_y = cy + r + 0.20

    else:

        cy = y - 0.88

        ax.plot(
            [x, x],
            [y - 0.03, cy + r],
            color="black",
            linewidth=1.35,
            zorder=3,
        )

        label_y = cy - r - 0.22


    circle = plt.Circle(
        (x, cy),
        r,
        facecolor="white",
        edgecolor="black",
        linewidth=1.4,
        zorder=8,
    )

    ax.add_patch(circle)


    # AC waveform

    t = np.linspace(
        -np.pi,
        np.pi,
        100
    )

    ax.plot(
        x + 0.17 * t / np.pi,
        cy + 0.085 * np.sin(t),
        color="black",
        linewidth=0.95,
        zorder=9,
    )


    ax.text(
        x,
        label_y,
        label,
        ha="center",
        va="center",
        fontsize=GEN_LABEL_SIZE,
        fontweight="bold",
        zorder=10,
    )


# ================================================================
# DRAW LOAD
# ================================================================

def draw_load(
    ax,
    x,
    y
):

    cy = y - 0.65

    # vertical connection

    ax.plot(
        [x, x],
        [
            y - 0.03,
            cy + LOAD_HEIGHT / 2
        ],
        color="black",
        linewidth=1.15,
        zorder=3,
    )


    # load rectangle

    rect = plt.Rectangle(
        (
            x - LOAD_WIDTH / 2,
            cy - LOAD_HEIGHT / 2
        ),
        LOAD_WIDTH,
        LOAD_HEIGHT,
        facecolor="white",
        edgecolor="black",
        linewidth=1.15,
        zorder=8,
    )

    ax.add_patch(rect)


    ax.text(
        x,
        cy,
        "L",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
        zorder=9,
    )


# ================================================================
# DRAW BUS NUMBER
# ================================================================

def draw_bus_label(
    ax,
    x,
    y,
    number
):

    ax.text(
        x,
        y + 0.22,
        str(number),
        ha="center",
        va="bottom",
        fontsize=BUS_LABEL_SIZE,
        fontweight="bold",
        zorder=10,
    )


# ================================================================
# DRAW TRANSMISSION NETWORK
# ================================================================
#
# Every branch comes directly from case30().
#
# Branch 1-3 is intentionally highlighted later as the
# stealth-attack branch.
# ================================================================

attack_from = 1
attack_to = 3


for row in branch:

    if row[BR_STATUS] <= 0:
        continue

    f = int(row[F_BUS])
    t = int(row[T_BUS])

    x1, y1 = POS[f]
    x2, y2 = POS[t]

    is_attack = (
        (f == attack_from and t == attack_to)
        or
        (f == attack_to and t == attack_from)
    )


    # ------------------------------------------------------------
    # Normal branch
    # ------------------------------------------------------------

    if not is_attack:

        ax.plot(
            [x1, x2],
            [y1, y2],
            color="black",
            linewidth=BRANCH_WIDTH,
            solid_capstyle="round",
            zorder=1,
        )


# ================================================================
# ATTACKED BRANCH — RED DASHED OVERLAY
# ================================================================

x1, y1 = POS[attack_from]
x2, y2 = POS[attack_to]

ax.plot(
    [x1, x2],
    [y1, y2],
    color="red",
    linewidth=ATTACK_WIDTH,
    linestyle="--",
    solid_capstyle="round",
    zorder=4,
)


# ================================================================
# ATTACK MARKER
# ================================================================
#
# Small circular marker placed approximately halfway along the
# attacked branch.
# ================================================================

mx = 0.5 * (x1 + x2)
my = 0.5 * (y1 + y2)

ax.scatter(
    [mx],
    [my],
    s=230,
    facecolors="white",
    edgecolors="red",
    linewidths=2.2,
    zorder=11,
)

ax.text(
    mx,
    my,
    "A",
    ha="center",
    va="center",
    color="red",
    fontsize=10,
    fontweight="bold",
    zorder=12,
)


# ================================================================
# DRAW BUSBARS + LABELS
# ================================================================

for b in sorted(bus_ids):

    x, y = POS[b]

    draw_busbar(
        ax,
        x,
        y
    )

    draw_bus_label(
        ax,
        x,
        y,
        b
    )


# ================================================================
# GENERATORS
# ================================================================

active_generators = []

for row in gen:

    if row[GEN_STATUS] <= 0:
        continue

    b = int(row[GEN_BUS])

    active_generators.append(b)


# Generator numbering follows the active generator rows in
# case30(), not manually assigned electrical data.

for i, b in enumerate(
    active_generators,
    start=1
):

    x, y = POS[b]

    # Keep generator symbols above the bus.
    draw_generator(
        ax,
        x,
        y,
        label=f"G{i}",
        direction="up",
    )


# ================================================================
# LOADS
# ================================================================

load_buses = []

for row in bus:

    b = int(row[BUS_I])

    pd = float(row[PD])
    qd = float(row[QD])

    if (
        abs(pd) > 1e-10
        or
        abs(qd) > 1e-10
    ):

        load_buses.append(b)


for b in load_buses:

    x, y = POS[b]

    draw_load(
        ax,
        x,
        y
    )


# ================================================================
# TITLE
# ================================================================

ax.text(
    9.8,
    7.55,
    "IEEE 30-bus test system",
    ha="center",
    va="center",
    fontsize=16,
    fontweight="bold",
)


# ================================================================
# STEALTH ATTACK INFORMATION PANEL
# ================================================================

panel_x = 14.4
panel_y = 7.05


ax.text(
    panel_x,
    panel_y,
    "STEALTH ATTACK",
    color="red",
    fontsize=11,
    fontweight="bold",
    ha="left",
    va="center",
)


ax.text(
    panel_x,
    panel_y - 0.40,
    r"Branch 1--3:  $X_{ij}^{att}=1.10X_{ij}$",
    color="black",
    fontsize=9.5,
    ha="left",
    va="center",
)


# ================================================================
# SMALL ATTACK DESCRIPTION
# ================================================================

ax.text(
    panel_x,
    panel_y - 0.82,
    "Red dashed overlay = attacked branch",
    color="red",
    fontsize=8.5,
    ha="left",
    va="center",
)


# ================================================================
# LEGEND
# ================================================================

legend_x = 14.4
legend_y = -4.55


# Normal transmission branch

ax.plot(
    [
        legend_x,
        legend_x + 0.55
    ],
    [
        legend_y,
        legend_y
    ],
    color="black",
    linewidth=1.5,
)


ax.text(
    legend_x + 0.70,
    legend_y,
    "Transmission branch",
    fontsize=8.5,
    va="center",
)


# Attacked branch

ax.plot(
    [
        legend_x,
        legend_x + 0.55
    ],
    [
        legend_y - 0.35,
        legend_y - 0.35
    ],
    color="red",
    linewidth=3.0,
    linestyle="--",
)


ax.text(
    legend_x + 0.70,
    legend_y - 0.35,
    "Attacked branch",
    fontsize=8.5,
    va="center",
    color="black",
)


# Generator legend

gx = legend_x + 3.15
gy = legend_y


ax.add_patch(
    plt.Circle(
        (gx, gy),
        0.13,
        facecolor="white",
        edgecolor="black",
        linewidth=1.2,
    )
)


ax.text(
    gx + 0.30,
    gy,
    "Generator",
    fontsize=8.5,
    va="center",
)


# Load legend

lx = legend_x + 3.15
ly = legend_y - 0.35


ax.add_patch(
    plt.Rectangle(
        (
            lx - 0.15,
            ly - 0.10
        ),
        0.30,
        0.20,
        facecolor="white",
        edgecolor="black",
        linewidth=1.0,
    )
)


ax.text(
    lx + 0.30,
    ly,
    "Load",
    fontsize=8.5,
    va="center",
)


# ================================================================
# SYSTEM SUMMARY
# ================================================================

summary = (
    f"{len(bus)} buses  |  "
    f"{len(branch)} branches  |  "
    f"{len(active_generators)} generators  |  "
    f"{len(load_buses)} load buses"
)


ax.text(
    -0.15,
    -4.55,
    summary,
    fontsize=8.5,
    ha="left",
    va="center",
)


# ================================================================
# ATTACK MODEL FOOTNOTE
# ================================================================

ax.text(
    9.8,
    -4.55,
    r"Attack model: $X_{ij}^{att}=1.10X_{ij}$",
    fontsize=8.5,
    ha="center",
    va="center",
)


# ================================================================
# AXIS LIMITS
# ================================================================

ax.set_xlim(
    -1.0,
    21.2
)

ax.set_ylim(
    -5.0,
    8.0
)


# ================================================================
# LAYOUT
# ================================================================

plt.tight_layout(
    pad=0.25
)


# ================================================================
# OUTPUT FILES
# ================================================================

pdf_path = os.path.join(
    OUT,
    "ieee30_sld.pdf"
)

png_path = os.path.join(
    OUT,
    "ieee30_sld.png"
)


# Vector PDF

fig.savefig(
    pdf_path,
    bbox_inches="tight",
    pad_inches=0.04,
)


# High-resolution PNG

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
print("IEEE 30-BUS SLD GENERATED")
print("=" * 70)

print(f"Buses          : {len(bus)}")
print(f"Branches       : {len(branch)}")
print(f"Generators     : {len(active_generators)}")
print(f"Load buses     : {len(load_buses)}")

print(
    f"Attack branch  : "
    f"{attack_from} -> {attack_to}"
)

print(
    "Attack model   : "
    "X_ij -> 1.10 X_ij"
)

print()

print(f"PDF            : {pdf_path}")
print(f"PNG            : {png_path}")

print("=" * 70)