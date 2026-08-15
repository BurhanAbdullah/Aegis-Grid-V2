#!/usr/bin/env python3
import os, hashlib

fig_dir = "results/independent_validation_run/paper_figures"
files = sorted([f for f in os.listdir(fig_dir) if f != "SHA256SUMS.txt"])

out_lines = []
for f in files:
    filepath = os.path.join(fig_dir, f)
    h = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
    out_lines.append(f"{h}  {f}")

with open(os.path.join(fig_dir, "SHA256SUMS.txt"), "w") as out_f:
    out_f.write("\n".join(out_lines) + "\n")

print(f"Generated SHA256SUMS.txt for {len(files)} files in {fig_dir}")
