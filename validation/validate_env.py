#!/usr/bin/env python3

import os
import sys

required_dirs = [
    "config",
    "agents",
    "core",
    "experiments",
    "results",
    "plotting_data",
    "paper/figures"
]

missing = []

for d in required_dirs:
    if not os.path.isdir(d):
        missing.append(d)

if missing:
    print("Missing directories:")
    for d in missing:
        print(" -", d)
    sys.exit(1)

print("Environment validation passed.")
