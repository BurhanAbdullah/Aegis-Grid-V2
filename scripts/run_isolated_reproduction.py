#!/usr/bin/env python3
"""
Isolated Reproduction Driver for XMON-Grid Experiment Pipeline
Target Output: results/tsg_run_001/

This script orchestrates the authoritative reproduction pipeline into an isolated
output directory without modifying any existing production/paper files.
"""

import sys
import os
import shutil
import subprocess
import time
import datetime
import tempfile
import platform
import json

# Required metadata parameters
GIT_COMMIT = "f7cfbb2"
RANDOM_SEED = 42
DATASET_SIZE = 960
CASES = ["case9", "case14", "case30", "case118"]
ATTACKS = ["baseline", "branch1_out", "branch2_out", "branch3_out"]
SAMPLES_PER_COMBO = 60
K1_DEF = "OR Quorum (votes >= 1)"
K2_DEF = "Strict Majority Quorum (votes >= 2)"

def get_git_info(repo_dir):
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_dir, text=True).strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir, text=True).strip()
        return commit, branch
    except Exception:
        return GIT_COMMIT, "unknown"

def get_pkg_versions():
    pkgs = {}
    for pkg_name in ["numpy", "pandas", "sklearn", "matplotlib"]:
        try:
            mod = __import__(pkg_name)
            pkgs[pkg_name] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pkgs[pkg_name] = "not installed"
    return pkgs

def build_metadata(repo_dir, output_dir, commands_executed):
    commit, branch = get_git_info(repo_dir)
    pkgs = get_pkg_versions()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    lines = [
        "=================================================================",
        "XMON-GRID EXPERIMENT REPRODUCTION METADATA",
        "=================================================================",
        f"Timestamp (UTC)       : {timestamp}",
        f"Git Commit Hash       : {commit}",
        f"Git Branch            : {branch}",
        f"Python Version        : {platform.python_version()} ({sys.executable})",
        f"OS Platform           : {platform.platform()}",
        "-----------------------------------------------------------------",
        "DEPENDENCY VERSIONS",
        "-----------------------------------------------------------------",
        f"numpy                 : {pkgs.get('numpy')}",
        f"pandas                : {pkgs.get('pandas')}",
        f"scikit-learn          : {pkgs.get('sklearn')}",
        f"matplotlib            : {pkgs.get('matplotlib')}",
        "-----------------------------------------------------------------",
        "EXPERIMENTAL CONFIGURATION",
        "-----------------------------------------------------------------",
        f"Random Seed           : {RANDOM_SEED}",
        f"Total Dataset Rows    : {DATASET_SIZE}",
        f"Power Grid Cases ({len(CASES)})  : {', '.join(CASES)}",
        f"Attack Scenarios ({len(ATTACKS)}) : {', '.join(ATTACKS)}",
        f"Samples per Combo     : {SAMPLES_PER_COMBO}",
        f"K=1 Definition        : {K1_DEF}",
        f"K=2 Definition        : {K2_DEF}",
        "-----------------------------------------------------------------",
        "COMMANDS EXECUTED",
        "-----------------------------------------------------------------",
    ]
    for idx, cmd in enumerate(commands_executed, 1):
        lines.append(f"{idx}. {cmd}")
    lines.append("=================================================================")
    return "\n".join(lines)

def run_pipeline(dry_run=False, output_base="results/tsg_run_001"):
    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.abspath(os.path.join(repo_dir, output_base))
    
    raw_dir = os.path.join(out_dir, "raw")
    metrics_dir = os.path.join(out_dir, "metrics")
    tables_dir = os.path.join(out_dir, "tables")
    figures_dir = os.path.join(out_dir, "figures")
    temp_exec_dir = os.path.join(out_dir, "temp_exec")
    metadata_file = os.path.join(out_dir, "run_metadata.txt")

    pipeline_steps = [
        {
            "step": "1. Dataset Generation",
            "cmd": f"{sys.executable} scripts/generate_realistic_dataset.py {os.path.relpath(os.path.join(raw_dir, 'full_experiment_table.csv'), repo_dir)}",
            "script": "scripts/generate_realistic_dataset.py",
            "cwd": repo_dir,
            "inputs": ["Seed=42", "Cases=4", "Attacks=4", "Samples/combo=60"],
            "outputs": [os.path.join(raw_dir, "full_experiment_table.csv")]
        },
        {
            "step": "2. Stage Raw Dataset for Evaluation",
            "cmd": f"cp {os.path.relpath(os.path.join(raw_dir, 'full_experiment_table.csv'), repo_dir)} {os.path.relpath(os.path.join(metrics_dir, 'final_dataset.csv'), repo_dir)}",
            "script": "internal_copy",
            "cwd": repo_dir,
            "inputs": [os.path.join(raw_dir, "full_experiment_table.csv")],
            "outputs": [os.path.join(metrics_dir, "final_dataset.csv")]
        },
        {
            "step": "3. Export Metrics & Paper Tables (K=1 & K=2)",
            "cmd": f"{sys.executable} scripts/export_paper_data.py {os.path.relpath(temp_exec_dir, repo_dir)} {os.path.relpath(os.path.join(metrics_dir, 'final_dataset.csv'), repo_dir)}",
            "script": "scripts/export_paper_data.py",
            "cwd": repo_dir,
            "inputs": [os.path.join(metrics_dir, "final_dataset.csv")],
            "outputs": [
                os.path.join(metrics_dir, "final_dataset_labeled.csv"),
                os.path.join(tables_dir, "main_results.csv"),
                os.path.join(tables_dir, "confusion_matrix_k2.csv"),
                os.path.join(tables_dir, "confusion_matrix_k1.csv"),
                os.path.join(tables_dir, "confusion_matrix.csv")
            ]
        },
        {
            "step": "4. Sequential Physics Accumulator",
            "cmd": f"{sys.executable} scripts/add_sequential_physics.py",
            "script": "scripts/add_sequential_physics.py",
            "cwd": temp_exec_dir,
            "inputs": [os.path.join(metrics_dir, "final_dataset.csv")],
            "outputs": [os.path.join(metrics_dir, "sequential_physics.csv")]
        },
        {
            "step": "5. Sequential Physics Threshold Calibration",
            "cmd": f"{sys.executable} scripts/fix_sequential_threshold.py",
            "script": "scripts/fix_sequential_threshold.py",
            "cwd": temp_exec_dir,
            "inputs": [os.path.join(metrics_dir, "sequential_physics.csv")],
            "outputs": [
                os.path.join(metrics_dir, "sequential_physics.csv"),
                os.path.join(tables_dir, "sequential_threshold.txt")
            ]
        },
        {
            "step": "6. Prepare Plotting CSV Data for Figures",
            "cmd": f"{sys.executable} scripts/generate_roc_data.py && {sys.executable} scripts/generate_sensitivity_data.py && {sys.executable} scripts/generate_comparison_table.py && {sys.executable} scripts/generate_heatmap_data.py && {sys.executable} scripts/multi_run_eval.py {os.path.relpath(temp_exec_dir, repo_dir)}",
            "script": "plotting_data generators",
            "cwd": temp_exec_dir,
            "inputs": [os.path.join(raw_dir, "full_experiment_table.csv")],
            "outputs": [os.path.join(temp_exec_dir, "plotting_data", "*.csv")]
        },
        {
            "step": "7. IEEE Figure Generation",
            "cmd": f"{sys.executable} scripts/generate_ieee_figures.py",
            "script": "scripts/generate_ieee_figures.py",
            "cwd": temp_exec_dir,
            "inputs": [os.path.join(temp_exec_dir, "plotting_data", "*.csv")],
            "outputs": [
                os.path.join(figures_dir, "fig_roc.png"),
                os.path.join(figures_dir, "fig_sensitivity.png"),
                os.path.join(figures_dir, "fig_comparison.png"),
                os.path.join(figures_dir, "fig_stability.png"),
                os.path.join(figures_dir, "fig_heatmap.png")
            ]
        }
    ]

    print("=================================================================")
    print("XMON-GRID ISOLATED REPRODUCTION DRIVER")
    print(f"Target Output Directory : {out_dir}")
    print(f"Execution Mode          : {'DRY-RUN (No execution)' if dry_run else 'REAL EXECUTION'}")
    print("=================================================================\n")

    if dry_run:
        print("[DRY-RUN VALIDATION TRACE]")
        print("Safety Check: Verifying that all target outputs are isolated within target directory...")
        for s in pipeline_steps:
            print(f"\n--- {s['step']} ---")
            print(f"  Command    : {s['cmd']}")
            print(f"  Working Dir: {s['cwd']}")
            print(f"  Inputs     : {', '.join(s['inputs'])}")
            print("  Outputs    :")
            for out in s['outputs']:
                print(f"    - {out}")
                # Verify that out path is inside out_dir or temp_exec_dir
                rel = os.path.relpath(out, out_dir)
                if rel.startswith(".."):
                    raise RuntimeError(f"SAFETY VIOLATION: Output path {out} escapes target output directory {out_dir}!")
        
        print("\n-----------------------------------------------------------------")
        print("DRY-RUN SAFETY CHECK PASSED: All outputs are 100% isolated to:")
        print(f"  {out_dir}")
        print("Root directories paper/, data/, results/ (canonical), and figures/ will NOT be modified.")
        print("-----------------------------------------------------------------")
        return

    # Real execution mode (only executed when dry_run=False)
    print("Creating isolated output directory structure...")
    for d in [raw_dir, metrics_dir, tables_dir, figures_dir, temp_exec_dir]:
        os.makedirs(d, exist_ok=True)

    # Setup temp execution staging environment
    os.makedirs(os.path.join(temp_exec_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(temp_exec_dir, "results"), exist_ok=True)
    os.makedirs(os.path.join(temp_exec_dir, "paper", "data"), exist_ok=True)
    os.makedirs(os.path.join(temp_exec_dir, "paper", "tables"), exist_ok=True)
    os.makedirs(os.path.join(temp_exec_dir, "plotting_data"), exist_ok=True)
    os.makedirs(os.path.join(temp_exec_dir, "figures"), exist_ok=True)
    os.makedirs(os.path.join(temp_exec_dir, "scripts"), exist_ok=True)

    # Copy script files into temp_exec_dir/scripts for isolated execution
    for script_file in os.listdir(os.path.join(repo_dir, "scripts")):
        if script_file.endswith(".py"):
            shutil.copy2(os.path.join(repo_dir, "scripts", script_file), os.path.join(temp_exec_dir, "scripts", script_file))

    cmds_log = []

    # Step 1: Generate realistic dataset directly into raw_dir
    cmd1 = [sys.executable, "scripts/generate_realistic_dataset.py", os.path.join(raw_dir, "full_experiment_table.csv")]
    cmds_log.append(" ".join(cmd1))
    subprocess.run(cmd1, cwd=repo_dir, check=True)

    # Copy to metrics and temp_exec_dir
    shutil.copy2(os.path.join(raw_dir, "full_experiment_table.csv"), os.path.join(metrics_dir, "final_dataset.csv"))
    shutil.copy2(os.path.join(raw_dir, "full_experiment_table.csv"), os.path.join(temp_exec_dir, "data", "full_experiment_table.csv"))
    shutil.copy2(os.path.join(raw_dir, "full_experiment_table.csv"), os.path.join(temp_exec_dir, "results", "final_dataset.csv"))

    # Step 2: Export paper data
    cmd2 = [sys.executable, "scripts/export_paper_data.py", temp_exec_dir, os.path.join(metrics_dir, "final_dataset.csv")]
    cmds_log.append(" ".join(cmd2))
    subprocess.run(cmd2, cwd=repo_dir, check=True)

    # Collect export_paper_data outputs
    shutil.copy2(os.path.join(temp_exec_dir, "paper", "data", "final_dataset_labeled.csv"), os.path.join(metrics_dir, "final_dataset_labeled.csv"))
    for t_file in ["main_results.csv", "confusion_matrix_k2.csv", "confusion_matrix_k1.csv", "confusion_matrix.csv"]:
        if os.path.exists(os.path.join(temp_exec_dir, "paper", "tables", t_file)):
            shutil.copy2(os.path.join(temp_exec_dir, "paper", "tables", t_file), os.path.join(tables_dir, t_file))

    # Step 3: Sequential physics
    cmd3 = [sys.executable, "scripts/add_sequential_physics.py"]
    cmds_log.append(" ".join(cmd3) + " (cwd=temp_exec)")
    subprocess.run(cmd3, cwd=temp_exec_dir, check=True)

    cmd4 = [sys.executable, "scripts/fix_sequential_threshold.py"]
    cmds_log.append(" ".join(cmd4) + " (cwd=temp_exec)")
    subprocess.run(cmd4, cwd=temp_exec_dir, check=True)

    shutil.copy2(os.path.join(temp_exec_dir, "paper", "data", "sequential_physics.csv"), os.path.join(metrics_dir, "sequential_physics.csv"))
    shutil.copy2(os.path.join(temp_exec_dir, "paper", "tables", "sequential_threshold.txt"), os.path.join(tables_dir, "sequential_threshold.txt"))

    # Step 4: Plotting data & figures
    for p_script in ["generate_roc_data.py", "generate_sensitivity_data.py", "generate_comparison_table.py", "generate_heatmap_data.py"]:
        c = [sys.executable, f"scripts/{p_script}"]
        cmds_log.append(" ".join(c) + " (cwd=temp_exec)")
        subprocess.run(c, cwd=temp_exec_dir, check=True)

    c_multi = [sys.executable, "scripts/multi_run_eval.py", temp_exec_dir]
    cmds_log.append(" ".join(c_multi) + " (cwd=temp_exec)")
    subprocess.run(c_multi, cwd=temp_exec_dir, check=True)

    cmd_fig = [sys.executable, "scripts/generate_ieee_figures.py"]
    cmds_log.append(" ".join(cmd_fig) + " (cwd=temp_exec)")
    subprocess.run(cmd_fig, cwd=temp_exec_dir, check=True)

    # Copy figures to target figures_dir
    for fig_file in os.listdir(os.path.join(temp_exec_dir, "figures")):
        if fig_file.endswith(".png"):
            shutil.copy2(os.path.join(temp_exec_dir, "figures", fig_file), os.path.join(figures_dir, fig_file))

    # Cleanup temp_exec_dir
    shutil.rmtree(temp_exec_dir, ignore_errors=True)

    # Write run_metadata.txt
    meta_content = build_metadata(repo_dir, out_dir, cmds_log)
    with open(metadata_file, "w") as f:
        f.write(meta_content)

    print("\n=================================================================")
    print("ISOLATED REPRODUCTION COMPLETE")
    print(f"Results saved to : {out_dir}")
    print(f"Metadata file    : {metadata_file}")
    print("=================================================================")

if __name__ == "__main__":
    dry_run_flag = "--dry-run" in sys.argv or "-n" in sys.argv
    run_pipeline(dry_run=dry_run_flag)
