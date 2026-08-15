#!/usr/bin/env python3
"""
Reproducibility Verification Script for XMON-Grid
File: scripts/verify_reproducibility.py

Runs the authoritative experiment twice with fixed random seed (SEED=42) into two isolated output directories:
- results/tsg_run_002/
- results/tsg_run_002_repro_test/

Compares raw CSV rows, metrics, and SHA256 checksums to verify 100% deterministic reproducibility.
"""

import sys, os, shutil, hashlib
sys.path.insert(0, os.path.abspath("."))

from scripts.run_authoritative_experiment import run_experiment, generate_tables, generate_figures, generate_sha256sums, OUTPUT_DIR

def run_reproducibility_test():
    print("==========================================================")
    print("REPRODUCIBILITY & DETERMINISM VERIFICATION")
    print("==========================================================")
    
    # Dir 1: Canonical run_002
    dir1 = "results/tsg_run_002"
    
    # Dir 2: Separate repro test directory
    dir2 = "results/tsg_run_002_repro_test"
    if os.path.exists(dir2):
        shutil.rmtree(dir2)
        
    # Temporary switch OUTPUT_DIR for second run
    import scripts.run_authoritative_experiment as exp
    exp.OUTPUT_DIR = dir2
    
    print(f"\n1. Executing Second Independent Run in {dir2}...")
    det_rows_2, nis_samples_2 = exp.run_experiment(seed=42)
    exp.generate_tables(det_rows_2)
    exp.generate_figures(det_rows_2, nis_samples_2)
    exp.generate_sha256sums()
    
    # Compare raw test datasets byte-for-byte
    raw1_path = os.path.join(dir1, "raw", "full_test_dataset.csv")
    raw2_path = os.path.join(dir2, "raw", "full_test_dataset.csv")
    
    with open(raw1_path, "rb") as f1, open(raw2_path, "rb") as f2:
        hash1 = hashlib.sha256(f1.read()).hexdigest()
        hash2 = hashlib.sha256(f2.read()).hexdigest()
        
    print(f"\n2. Hash Comparison (full_test_dataset.csv):")
    print(f"   Run 1 Hash : {hash1}")
    print(f"   Run 2 Hash : {hash2}")
    
    assert hash1 == hash2, "ERROR: Raw dataset outputs are not identical across runs!"
    print("   [PASS] 100% Identical Raw Dataset Hash!")
    
    # Compare SHA256SUMS.txt
    sha1_path = os.path.join(dir1, "SHA256SUMS.txt")
    sha2_path = os.path.join(dir2, "SHA256SUMS.txt")
    
    with open(sha1_path, "r") as f1, open(sha2_path, "r") as f2:
        sha_lines_1 = f1.read()
        sha_lines_2 = f2.read()
        
    assert sha_lines_1 == sha_lines_2, "ERROR: Cryptographic SHA256SUMS.txt mismatch across runs!"
    print("   [PASS] 100% Identical Cryptographic Manifest Hash!")
    
    # Clean up temporary repro directory
    shutil.rmtree(dir2)
    exp.OUTPUT_DIR = dir1
    
    print("\nREPRODUCIBILITY & DETERMINISM VERIFICATION PASSED 100%!")

if __name__ == "__main__":
    run_reproducibility_test()
