import sys
import os
import subprocess
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from aegis_v2.agents.adaptive_agent import AegisAgentV2


MATPOWER_PATH = os.path.join(PROJECT_ROOT, "matpower")

if not os.path.exists(MATPOWER_PATH):
    raise RuntimeError("MATPOWER directory missing")


# --------------------------------------------------
# Expanded IEEE validation cases
# --------------------------------------------------

CASES = ["case9", "case14", "case30", "case118"]


# --------------------------------------------------
# Attack scenarios
# --------------------------------------------------

ATTACK_SCENARIOS = {

    "remove_branch_1":
        "mpc.branch(1, BR_STATUS) = 0;",

    "remove_branch_2":
        "mpc.branch(2, BR_STATUS) = 0;",

    "remove_branch_3":
        "mpc.branch(3, BR_STATUS) = 0;"
}


# --------------------------------------------------
# MATPOWER execution
# --------------------------------------------------

def run_matpower_case(case, attack_code=None):

    if attack_code:

        script = f"""
        addpath(genpath('{MATPOWER_PATH}'));
        addpath(genpath(fullfile('{MATPOWER_PATH}','data')));
        define_constants;

        mpc = loadcase('{case}');
        {attack_code}

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

    success = (
        "SUCCESS" in result.stdout
        or "PF successful" in result.stdout
        or "Newton's method converged" in result.stdout
    )

    return success, latency


# --------------------------------------------------
# Experiment runner
# --------------------------------------------------

def run_experiment():

    agent = AegisAgentV2()

    print("\nRunning expanded topology-attack validation...\n")

    results = []

    for case in CASES:

        print(f"\nBASELINE TEST → {case}")

        baseline_success, _ = run_matpower_case(case)

        for attack_name, attack_code in ATTACK_SCENARIOS.items():

            print(f"ATTACK TEST → {case} | {attack_name}")

            attack_success, latency = run_matpower_case(
                case,
                attack_code
            )

            mitigation_triggered = False

            if not attack_success:

                agent.is_locked = True
                mitigation_triggered = True

            results.append({

                "case": case,
                "attack_type": attack_name,
                "baseline": baseline_success,
                "attack_success": attack_success,
                "mitigation_triggered": mitigation_triggered,
                "latency": round(latency, 3)

            })

    return results


# --------------------------------------------------
# Result printer
# --------------------------------------------------

def print_results(results):

    print("\n=== EXPERIMENT RESULTS ===\n")

    for r in results:

        print(
            f"{r['case']} | "
            f"{r['attack_type']} | "
            f"baseline={r['baseline']} | "
            f"attack={r['attack_success']} | "
            f"mitigation={r['mitigation_triggered']} | "
            f"latency={r['latency']}s"
        )


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    results = run_experiment()

    print_results(results)
