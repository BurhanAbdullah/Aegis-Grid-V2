#!/usr/bin/env python3
"""
Update SHA256SUMS.txt Manifest
File: scripts/update_manifest_hash.py
"""

import os, hashlib

OUTPUT_DIR = "results/tsg_run_002"

def update_manifest():
    sha_lines = []
    for root, _, files in os.walk(OUTPUT_DIR):
        for file in sorted(files):
            if file == "SHA256SUMS.txt":
                continue
            path = os.path.join(root, file)
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                hasher.update(f.read())
            rel_path = os.path.relpath(path, OUTPUT_DIR)
            sha_lines.append(f"{hasher.hexdigest()}  {rel_path}")
            
    sha_path = os.path.join(OUTPUT_DIR, "SHA256SUMS.txt")
    with open(sha_path, "w") as f:
        f.write("\n".join(sha_lines) + "\n")
    print(f"Updated SHA256SUMS.txt with {len(sha_lines)} artifact signatures.")

if __name__ == "__main__":
    update_manifest()
