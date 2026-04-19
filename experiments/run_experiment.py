import sys
import os
import subprocess
import time


# --------------------------------------------------
# Ensure project root is visible for imports
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)


# --------------------------------------------------
# Import Aegis agent
# --------------------------------------------------

from aegis_v2.agents.adaptive_agent import AegisAgentV2


# --------------------------------------------------
# Detect MATPOWER directory automatically
# --------------------------------------------------

MATPOWER_PATH = os.path.join(PROJECT_ROOT, "matpower")

if not os.path.exists(MATPOWER_PATH):
    raise RuntimeError(
        f"MATPOWER directory not found:\n{MATPOWER_PATH}"
    )


# --------------------------------------------------
# IEEE benchmark systems
# --------------------------------------------------

CASES = ["case9", "case14", "case30"]


# --------------------------------------------------
# Run MATPOWER power-flow simulation
# --------------------------------------------------

def run_matpower_case(case, attack=False):

    if attack:

        script = f"""
        addpath(genpath('{MATPOWER_PATH}'));
        addpath(genpath(fullfile('{MATPOWER_PATH}','data')));
        define_constants;

        mpc = loadcase('{case}');
        mpc.branch(1, BR_STATUS) = 0;

        results = runpf(mpc);

        if results.success
            disp("SUCCESS");
        else
            disp("FAILED");
        end
        """

    else:

        script = f"""
        addpath(genpath('{MATPOWER_PATH}'));
        addpath(genpath(fullfile('{MATPOWER_PATH}','data')));
        define_constants;

        mpc = loadcase('{case}');
        results = runpf(mpc);

        if results.success
            disp("SUCCESS");
        else
            disp("FAILED");
        end
        """

    cmd = f'octave --quiet --eval "{script}"'

    start = time.time()

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    latency = time.time() - start

    # Detect convergence robustly
    success = (
        "SUCCESS" in result.stdout
        or "PF successful" in result.stdout
        or "Newton's method converged" in result.stdout
    )

    return success, latency


# --------------------------------------------------
# Experiment pipeline
# --------------------------------------------------

def run_experiment():

    agent = AegisAgentV2()

    results_table = []

    print("\nRunning cyber-physical resilience experiment...\n")

    for case in CASES:

        print(f"Running baseline: {case}")

        baseline_success, baseline_latency = run_matpower_case(case)

        print(f"Running topology attack: {case}")

        attack_success, attack_latency = run_matpower_case(case, attack=True)

        mitigation_triggered = False

        if not attack_success:

            agent.is_locked = True
            mitigation_triggered = True

        results_table.append({

            "case": case,
            "baseline": baseline_success,
            "attack": attack_success,
            "mitigation_triggered": mitigation_triggered,
            "latency_seconds": round(attack_latency, 3)

        })

    return results_table


# --------------------------------------------------
# Print results
# --------------------------------------------------

def print_results(results):

    print("\n=== EXPERIMENT RESULTS ===\n")

    for r in results:

        print(
            f"{r['case']} | "
            f"baseline={r['baseline']} | "
            f"attack={r['attack']} | "
            f"mitigation_triggered={r['mitigation_triggered']} | "
            f"latency={r['latency_seconds']}s"
        )


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    results = run_experiment()

    print_results(results)
