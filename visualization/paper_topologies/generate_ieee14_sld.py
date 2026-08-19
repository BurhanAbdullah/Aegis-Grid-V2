import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from pypower.api import case14


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

OUT = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# PYPOWER COLUMN INDICES
# ============================================================

BUS_I = 0
PD = 2
QD = 3

GEN_BUS = 0
GEN_STATUS = 7

F_BUS = 0
T_BUS = 1
BR_STATUS = 10


# ============================================================
# LOAD IEEE 14-BUS BENCHMARK
# ============================================================

mpc = case14()

bus = np.asarray(mpc["bus"], dtype=float)
branch = np.asarray(mpc["branch"], dtype=float)
gen = np.asarray(mpc["gen"], dtype=float)


# ============================================================
# HARD VALIDATION
# ============================================================

assert len(bus) == 14, \
    "IEEE 14-bus case must contain 14 buses"

assert len(branch) == 20, \
    "IEEE 14-bus case must contain 20 branches"


# ============================================================
# PUBLICATION SLD GEOMETRY
#
# Coordinates affect ONLY the graphical appearance.
# Electrical topology comes directly from case14().
# ============================================================

POS = {

    # --------------------------------------------------------
    # TOP CORRIDOR
    # --------------------------------------------------------

    1:  (0.0,  5.2),
    2:  (2.7,  5.2),
    3:  (5.4,  5.2),
    4:  (8.2,  5.2),
    5:  (11.0, 5.2),

    # --------------------------------------------------------
    # MIDDLE SECTION
    # --------------------------------------------------------

    7:  (6.2,  3.55),
    8:  (9.0,  3.55),

    6:  (5.0,  2.25),
    9:  (9.8,  2.25),

    # --------------------------------------------------------
    # LOWER SECTION
    # --------------------------------------------------------

    10: (11.8,  1.0),
    11: (7.0,   0.85),

    12: (4.8,  -0.35),
    13: (8.3,  -0.35),
    14: (11.5, -0.35),
}


# ============================================================
# VERIFY BUS POSITIONS
# ============================================================

case_buses = set(
    bus[:, BUS_I].astype(int)
)

position_buses = set(POS.keys())

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


# ============================================================
# GENERATOR DIRECTIONS
#
# Graphical placement only.
# ============================================================

GEN_DIRECTION = {

    1: "up",
    2: "up",
    3: "up",

    # Side-mounted generators reduce overlap
    6: "left",
    8: "right",
}


# ============================================================
# DRAW BUSBAR
# ============================================================

def draw_busbar(ax, x, y):

    ax.plot(
        [x - 0.34, x + 0.34],
        [y, y],
        color="black",
        linewidth=3.6,
        solid_capstyle="butt",
        zorder=5,
    )


# ============================================================
# DRAW GENERATOR
# ============================================================

def draw_generator(
    ax,
    x,
    y,
    label,
    direction="up",
):

    radius = 0.25

    # --------------------------------------------------------
    # Generator position
    # --------------------------------------------------------

    if direction == "up":

        cx = x
        cy = y + 0.85

        ax.plot(
            [x, x],
            [y, cy - radius],
            color="black",
            linewidth=1.3,
            zorder=2,
        )

    elif direction == "right":

        cx = x + 0.85
        cy = y

        ax.plot(
            [x, cx - radius],
            [y, y],
            color="black",
            linewidth=1.3,
            zorder=2,
        )

    elif direction == "left":

        cx = x - 0.85
        cy = y

        ax.plot(
            [x, cx + radius],
            [y, y],
            color="black",
            linewidth=1.3,
            zorder=2,
        )

    else:

        raise ValueError(
            "Generator direction must be "
            "'up', 'left', or 'right'."
        )


    # --------------------------------------------------------
    # Generator circle
    # --------------------------------------------------------

    ax.add_patch(
        plt.Circle(
            (cx, cy),
            radius,
            facecolor="white",
            edgecolor="black",
            linewidth=1.3,
            zorder=7,
        )
    )


    # --------------------------------------------------------
    # Generator waveform
    # --------------------------------------------------------

    t = np.linspace(
        -np.pi,
        np.pi,
        100,
    )

    ax.plot(
        cx + 0.15 * t / np.pi,
        cy + 0.08 * np.sin(t),
        color="black",
        linewidth=0.9,
        zorder=8,
    )


    # --------------------------------------------------------
    # Generator label
    # --------------------------------------------------------

    if direction == "up":

        lx = cx
        ly = cy + 0.38

        ha = "center"
        va = "bottom"

    elif direction == "right":

        lx = cx + 0.38
        ly = cy

        ha = "left"
        va = "center"

    else:

        lx = cx - 0.38
        ly = cy

        ha = "right"
        va = "center"


    ax.text(
        lx,
        ly,
        label,
        ha=ha,
        va=va,
        fontsize=8.5,
        fontweight="bold",
        zorder=9,
    )


# ============================================================
# DRAW LOAD
# ============================================================

def draw_load(
    ax,
    x,
    y,
):

    width = 0.48
    height = 0.32

    center_y = y - 0.68


    # --------------------------------------------------------
    # Load connection
    # --------------------------------------------------------

    ax.plot(
        [x, x],
        [
            y,
            center_y + height / 2,
        ],
        color="black",
        linewidth=1.2,
        zorder=2,
    )


    # --------------------------------------------------------
    # Load rectangle
    # --------------------------------------------------------

    ax.add_patch(
        plt.Rectangle(
            (
                x - width / 2,
                center_y - height / 2,
            ),
            width,
            height,
            facecolor="white",
            edgecolor="black",
            linewidth=1.1,
            zorder=7,
        )
    )


    # --------------------------------------------------------
    # Load symbol
    # --------------------------------------------------------

    ax.text(
        x,
        center_y,
        "L",
        ha="center",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        zorder=8,
    )


# ============================================================
# CREATE FIGURE
# ============================================================

fig, ax = plt.subplots(
    figsize=(12.8, 7.6)
)

ax.set_aspect("equal")
ax.axis("off")


# ============================================================
# DRAW ELECTRICAL BRANCHES
#
# ALL BRANCHES COME DIRECTLY FROM case14()
# ============================================================

for row in branch:

    if row[BR_STATUS] <= 0:
        continue

    from_bus = int(row[F_BUS])
    to_bus = int(row[T_BUS])

    x1, y1 = POS[from_bus]
    x2, y2 = POS[to_bus]

    ax.plot(
        [x1, x2],
        [y1, y2],
        color="black",
        linewidth=1.25,
        solid_capstyle="round",
        zorder=1,
    )


# ============================================================
# DRAW BUSBARS AND BUS NUMBERS
# ============================================================

for row in bus:

    bus_number = int(row[BUS_I])

    x, y = POS[bus_number]

    draw_busbar(
        ax,
        x,
        y,
    )

    ax.text(
        x,
        y + 0.22,
        str(bus_number),
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        zorder=10,
    )


# ============================================================
# DRAW GENERATORS
# ============================================================

generator_count = 0

for row in gen:

    if row[GEN_STATUS] <= 0:
        continue

    bus_number = int(row[GEN_BUS])

    x, y = POS[bus_number]

    generator_count += 1

    direction = GEN_DIRECTION.get(
        bus_number,
        "up",
    )

    draw_generator(
        ax,
        x,
        y,
        f"G{generator_count}",
        direction,
    )


# ============================================================
# DRAW LOADS
#
# Load buses determined directly from PD/QD.
# ============================================================

load_count = 0

for row in bus:

    bus_number = int(row[BUS_I])

    pd = row[PD]
    qd = row[QD]

    if (
        abs(pd) < 1e-10
        and
        abs(qd) < 1e-10
    ):
        continue

    x, y = POS[bus_number]

    draw_load(
        ax,
        x,
        y,
    )

    load_count += 1


# ============================================================
# STEALTH ATTACK
#
# The experiment perturbs the reactance of the SECOND
# branch in the case14 branch matrix:
#
#       X_ij -> 1.10 X_ij
#
# Python index = 1.
#
# This figure only VISUALIZES the attacked branch.
# It does not modify the case data.
# ============================================================

ATTACK_BRANCH_INDEX = 1

attack_branch = branch[
    ATTACK_BRANCH_INDEX
]

attack_from = int(
    attack_branch[F_BUS]
)

attack_to = int(
    attack_branch[T_BUS]
)

x1, y1 = POS[attack_from]
x2, y2 = POS[attack_to]


# ============================================================
# RED DASHED ATTACK OVERLAY
# ============================================================

ax.plot(
    [x1, x2],
    [y1, y2],
    color="red",
    linewidth=3.2,
    linestyle="--",
    solid_capstyle="round",
    zorder=6,
)


# ============================================================
# ATTACK MARKER
# ============================================================

xm = 0.5 * (x1 + x2)
ym = 0.5 * (y1 + y2)


# White centre with red border
ax.add_patch(
    plt.Circle(
        (xm, ym),
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


# ============================================================
# ATTACK ANNOTATION
#
# Compact scientific description.
# ============================================================

ax.text(
    9.35,
    6.48,
    "STEALTH ATTACK",
    ha="left",
    va="center",
    fontsize=8.5,
    fontweight="bold",
    color="red",
    zorder=14,
)


ax.text(
    9.35,
    6.18,
    rf"Branch {attack_from}--{attack_to}: "
    r"$X_{ij}^{\mathrm{att}}=1.10X_{ij}$",
    ha="left",
    va="center",
    fontsize=8.2,
    zorder=14,
)


# ============================================================
# TITLE
# ============================================================

ax.text(
    6.0,
    7.05,
    "IEEE 14-bus test system",
    ha="center",
    va="center",
    fontsize=15,
    fontweight="bold",
    zorder=14,
)


# ============================================================
# COMPACT SYSTEM INFORMATION
# ============================================================

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


# ============================================================
# LEGEND
#
# Minimal and publication-oriented.
# ============================================================

legend_handles = [

    Line2D(
        [0],
        [0],
        color="black",
        linewidth=1.25,
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


# ============================================================
# FRAME LIMITS
# ============================================================

ax.set_xlim(
    -1.45,
    13.2,
)

ax.set_ylim(
    -1.85,
    7.45,
)


# ============================================================
# EXPORT
# ============================================================

plt.tight_layout(
    pad=0.3
)


pdf_path = os.path.join(
    OUT,
    "ieee14_sld.pdf",
)

png_path = os.path.join(
    OUT,
    "ieee14_sld.png",
)


# ------------------------------------------------------------
# VECTOR PDF
# ------------------------------------------------------------

fig.savefig(
    pdf_path,
    bbox_inches="tight",
    pad_inches=0.04,
)


# ------------------------------------------------------------
# HIGH-RESOLUTION PNG
# ------------------------------------------------------------

fig.savefig(
    png_path,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.04,
)


plt.close(fig)


# ============================================================
# FINAL VALIDATION
# ============================================================

print("=" * 70)
print("IEEE 14-BUS SLD + STEALTH ATTACK GENERATED")
print("=" * 70)

print(f"Buses          : {len(bus)}")
print(f"Branches       : {len(branch)}")
print(f"Generators     : {generator_count}")
print(f"Load buses     : {load_count}")

print(
    f"Attack branch  : "
    f"{attack_from} -> {attack_to}"
)

print(
    "Attack model   : "
    "X_ij -> 1.10 X_ij"
)

print(f"PDF            : {pdf_path}")
print(f"PNG            : {png_path}")

print("=" * 70)