import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from pypower.api import case9


# ================================================================
# OUTPUT DIRECTORY
# ================================================================

OUT = os.path.dirname(os.path.abspath(__file__))


# ================================================================
# IEEE 9-BUS TEST SYSTEM — PUBLICATION SLD
# ================================================================
#
# Electrical topology and load/generator data are taken directly
# from PYPOWER case9().
#
# Coordinates affect ONLY the graphical layout.
#
# The red dashed overlay indicates the stealth perturbation used
# in the benchmark illustration:
#
#       X_ij -> 1.10 X_ij
#
# The attack overlay does NOT modify the electrical case.
# ================================================================


# ================================================================
# LOAD IEEE 9-BUS BENCHMARK
# ================================================================

mpc = case9()

bus = np.asarray(
    mpc["bus"],
    dtype=float
)

branch = np.asarray(
    mpc["branch"],
    dtype=float
)

gen = np.asarray(
    mpc["gen"],
    dtype=float
)


# ================================================================
# PYPOWER / MATPOWER COLUMN INDICES
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
# HARD VALIDATION
# ================================================================

assert len(bus) == 9, \
    "Expected IEEE 9-bus system."

assert len(branch) == 9, \
    "Expected IEEE 9-bus system to contain 9 branches."


# ================================================================
# BUS IDENTIFIERS
# ================================================================

bus_ids = bus[:, BUS_I].astype(int)


# ================================================================
# PUBLICATION SLD GEOMETRY
#
# Coordinates are graphical only.
# Electrical topology comes directly from case9().
# ================================================================

POS = {

    # ------------------------------------------------------------
    # UPPER CORRIDOR
    # ------------------------------------------------------------

    1: (0.0, 4.0),
    4: (3.0, 4.0),
    5: (6.0, 4.0),
    6: (9.0, 4.0),
    3: (12.0, 4.0),

    # ------------------------------------------------------------
    # LOWER CORRIDOR
    # ------------------------------------------------------------

    2: (0.0, 1.0),
    7: (3.0, 1.0),
    8: (6.0, 1.0),
    9: (9.0, 1.0),
}


# ================================================================
# VERIFY BUS POSITIONS
# ================================================================

case_buses = set(
    bus_ids
)

position_buses = set(
    POS.keys()
)

if case_buses != position_buses:

    missing = sorted(
        case_buses - position_buses
    )

    extra = sorted(
        position_buses - case_buses
    )

    raise RuntimeError(
        "Bus-coordinate mismatch.\n"
        f"Missing buses: {missing}\n"
        f"Extra coordinates: {extra}"
    )


# ================================================================
# ATTACK CONFIGURATION
# ================================================================
#
# PYPOWER uses zero-based Python indexing.
#
# ATTACK_BRANCH_INDEX = 1 means the SECOND branch in case9().
#
# In the standard PYPOWER IEEE 9-bus case this corresponds to:
#
#       bus 4 -> bus 5
#
# The actual network data are NOT changed.
# ================================================================

ATTACK_BRANCH_INDEX = 1

assert 0 <= ATTACK_BRANCH_INDEX < len(branch), \
    "Invalid attack branch index."


attack_branch = branch[
    ATTACK_BRANCH_INDEX
]

ATTACK_FROM = int(
    attack_branch[F_BUS]
)

ATTACK_TO = int(
    attack_branch[T_BUS]
)


# ================================================================
# FIGURE
# ================================================================

fig, ax = plt.subplots(
    figsize=(12.8, 7.2)
)

ax.set_aspect(
    "equal"
)

ax.axis("off")


# ================================================================
# DRAWING HELPERS
# ================================================================

def draw_busbar(
    ax,
    x,
    y,
    length=0.72,
):

    ax.plot(
        [
            x - length / 2,
            x + length / 2
        ],
        [
            y,
            y
        ],
        color="black",
        linewidth=4.0,
        solid_capstyle="butt",
        zorder=5,
    )


# ================================================================
# GENERATOR SYMBOL
# ================================================================

def draw_generator(
    ax,
    x,
    y,
    label=None,
):

    stem_top = y + 0.92

    cx = x
    cy = y + 1.45

    radius = 0.32


    # ------------------------------------------------------------
    # Generator connection
    # ------------------------------------------------------------

    ax.plot(
        [x, x],
        [
            y + 0.03,
            stem_top
        ],
        color="black",
        linewidth=1.5,
        zorder=2,
    )


    # ------------------------------------------------------------
    # Generator circle
    # ------------------------------------------------------------

    circle = plt.Circle(
        (cx, cy),
        radius,
        facecolor="white",
        edgecolor="black",
        linewidth=1.5,
        zorder=6,
    )

    ax.add_patch(
        circle
    )


    # ------------------------------------------------------------
    # Generator waveform
    # ------------------------------------------------------------

    t = np.linspace(
        -np.pi,
        np.pi,
        100,
    )

    ax.plot(
        cx + 0.20 * t / np.pi,
        cy + 0.10 * np.sin(t),
        color="black",
        linewidth=1.0,
        zorder=7,
    )


    # ------------------------------------------------------------
    # Generator label
    # ------------------------------------------------------------

    if label:

        ax.text(
            cx,
            cy + 0.48,
            label,
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            zorder=9,
        )


# ================================================================
# LOAD SYMBOL
# ================================================================

def draw_load(
    ax,
    x,
    y,
):

    stem_bottom = y - 0.82

    cx = x
    cy = y - 1.10

    width = 0.56
    height = 0.40


    # ------------------------------------------------------------
    # Load connection
    # ------------------------------------------------------------

    ax.plot(
        [x, x],
        [
            y - 0.03,
            stem_bottom
        ],
        color="black",
        linewidth=1.4,
        zorder=2,
    )


    # ------------------------------------------------------------
    # Load rectangle
    # ------------------------------------------------------------

    rect = plt.Rectangle(
        (
            cx - width / 2,
            cy - height / 2
        ),
        width,
        height,
        facecolor="white",
        edgecolor="black",
        linewidth=1.3,
        zorder=6,
    )

    ax.add_patch(
        rect
    )


    # ------------------------------------------------------------
    # Load symbol
    # ------------------------------------------------------------

    ax.text(
        cx,
        cy,
        "L",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        zorder=7,
    )


# ================================================================
# DRAW NORMAL TRANSMISSION BRANCHES
#
# Topology comes directly from case9().
# ================================================================

for index, row in enumerate(branch):

    if row[BR_STATUS] <= 0:
        continue


    f = int(
        row[F_BUS]
    )

    t = int(
        row[T_BUS]
    )


    x1, y1 = POS[f]
    x2, y2 = POS[t]


    ax.plot(
        [x1, x2],
        [y1, y2],
        color="black",
        linewidth=1.55,
        solid_capstyle="round",
        zorder=1,
    )


# ================================================================
# DRAW BUSBARS AND BUS NUMBERS
# ================================================================

for b in bus_ids:

    x, y = POS[b]


    draw_busbar(
        ax,
        x,
        y,
    )


    ax.text(
        x,
        y + 0.23,
        str(b),
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
        zorder=8,
    )


# ================================================================
# DRAW GENERATORS
#
# Generator locations are taken directly from case9().
# ================================================================

generator_count = 0

for row in gen:

    if row[GEN_STATUS] <= 0:
        continue


    b = int(
        row[GEN_BUS]
    )

    x, y = POS[b]


    generator_count += 1


    draw_generator(
        ax,
        x,
        y,
        label=f"G{generator_count}",
    )


# ================================================================
# DRAW LOADS
#
# Load locations are determined directly from PD/QD.
# ================================================================

load_count = 0

for row in bus:

    b = int(
        row[BUS_I]
    )

    pd = float(
        row[PD]
    )

    qd = float(
        row[QD]
    )


    if (
        abs(pd) < 1e-10
        and
        abs(qd) < 1e-10
    ):
        continue


    x, y = POS[b]


    draw_load(
        ax,
        x,
        y,
    )


    load_count += 1


# ================================================================
# STEALTH ATTACK OVERLAY
#
# Red dashed line deliberately overlays the attacked branch.
#
# Attack model:
#
#       X_ij^att = 1.10 X_ij
#
# This is a visual indication only.
# ================================================================

x1, y1 = POS[ATTACK_FROM]
x2, y2 = POS[ATTACK_TO]


ax.plot(
    [x1, x2],
    [y1, y2],
    color="red",
    linewidth=3.2,
    linestyle="--",
    solid_capstyle="round",
    zorder=6,
)


# ================================================================
# ATTACK MARKER
# ================================================================

xm = 0.5 * (
    x1 + x2
)

ym = 0.5 * (
    y1 + y2
)


ax.add_patch(
    plt.Circle(
        (
            xm,
            ym
        ),
        0.145,
        facecolor="white",
        edgecolor="red",
        linewidth=2.0,
        zorder=12,
    )
)


ax.text(
    xm,
    ym,
    "A",
    ha="center",
    va="center",
    fontsize=7.5,
    fontweight="bold",
    color="red",
    zorder=13,
)


# ================================================================
# ATTACK INFORMATION
# ================================================================

ax.text(
    9.55,
    5.15,
    "STEALTH ATTACK",
    ha="left",
    va="center",
    fontsize=8.5,
    fontweight="bold",
    color="red",
    zorder=14,
)


ax.text(
    9.55,
    4.86,
    rf"Branch {ATTACK_FROM}--{ATTACK_TO}: "
    r"$X_{ij}^{\mathrm{att}}=1.10X_{ij}$",
    ha="left",
    va="center",
    fontsize=8.2,
    zorder=14,
)


# ================================================================
# TITLE
# ================================================================

ax.text(
    6.0,
    5.65,
    "IEEE 9-bus test system",
    ha="center",
    va="center",
    fontsize=15,
    fontweight="bold",
    zorder=14,
)


# ================================================================
# SYSTEM INFORMATION
# ================================================================

info_text = (
    f"{len(bus)} buses  |  "
    f"{len(branch)} branches  |  "
    f"{generator_count} generators  |  "
    f"{load_count} load buses"
)


ax.text(
    0.05,
    0.035,
    info_text,
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize=7.5,
    color="black",
    zorder=14,
)


# ================================================================
# PUBLICATION LEGEND
# ================================================================

legend_handles = [

    Line2D(
        [0],
        [0],
        color="black",
        linewidth=1.55,
        label="Transmission branch",
    ),

    Line2D(
        [0],
        [0],
        color="red",
        linewidth=3.0,
        linestyle="--",
        label="Attacked branch",
    ),

    Line2D(
        [0],
        [0],
        marker="o",
        markersize=8,
        markerfacecolor="white",
        markeredgecolor="black",
        linestyle="None",
        label="Generator",
    ),

    Patch(
        facecolor="white",
        edgecolor="black",
        label="Load",
    ),
]


ax.legend(
    handles=legend_handles,
    loc="lower right",
    bbox_to_anchor=(0.985, 0.025),
    frameon=False,
    fontsize=7.2,
    ncol=2,
    columnspacing=1.0,
    handlelength=2.0,
    handletextpad=0.5,
)


# ================================================================
# FRAME / SPACING
# ================================================================

ax.set_xlim(
    -1.15,
    13.25,
)

ax.set_ylim(
    -1.75,
    6.10,
)


# ================================================================
# EXPORT
# ================================================================

plt.tight_layout(
    pad=0.35
)


pdf_path = os.path.join(
    OUT,
    "ieee9_sld.pdf",
)

png_path = os.path.join(
    OUT,
    "ieee9_sld.png",
)


# ---------------------------------------------------------------
# VECTOR PDF
# ---------------------------------------------------------------

fig.savefig(
    pdf_path,
    bbox_inches="tight",
    pad_inches=0.04,
)


# ---------------------------------------------------------------
# HIGH-RESOLUTION PNG
# ---------------------------------------------------------------

fig.savefig(
    png_path,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.04,
)


plt.close(
    fig
)


# ================================================================
# FINAL VALIDATION
# ================================================================

print("=" * 70)
print("IEEE 9-BUS SLD + STEALTH ATTACK GENERATED")
print("=" * 70)

print(
    f"Buses          : {len(bus)}"
)

print(
    f"Branches       : {len(branch)}"
)

print(
    f"Generators     : {generator_count}"
)

print(
    f"Load buses     : {load_count}"
)

print(
    f"Attack branch  : "
    f"{ATTACK_FROM} -> {ATTACK_TO}"
)

print(
    "Attack model   : "
    "X_ij -> 1.10 X_ij"
)

print()
print(
    f"PDF            : {pdf_path}"
)

print(
    f"PNG            : {png_path}"
)

print("=" * 70)