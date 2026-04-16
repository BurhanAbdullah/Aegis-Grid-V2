import subprocess

from aegis_v2.agents.adaptive_agent import AegisAgentV2


def run_attack_case():

    cmd = "octave --quiet matpower_attack_case.m"

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout


def main():

    agent = AegisAgentV2()

    output = run_attack_case()

    print(output)

    if "PF failed" in output:
        agent.is_locked = True
        print("⚠ GRID INSTABILITY DETECTED")
        print("🔒 LOCKDOWN TRIGGERED")
    else:
        print("GRID STABLE")


if __name__ == "__main__":
    main()
