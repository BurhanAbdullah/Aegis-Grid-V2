#!/usr/bin/env python3

import glob

figs = sorted(glob.glob("paper/figures/*"))

with open("paper/FIGURE_MANIFEST.md", "w") as f:

    f.write("# FIGURE MANIFEST\n\n")

    for fig in figs:
        f.write(f"- {fig}\n")

print("Figure manifest generated.")
