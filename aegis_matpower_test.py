from aegis_v2.agents.adaptive_agent import AegisAgentV2
from matpower_bridge import run_case, converged


def simulate_attack():
    output = run_case("case9")

    agent = AegisAgentV2()

    if not converged(output):
        agent.is_locked = True
        print("LOCKDOWN TRIGGERED")
    else:
        print("GRID STABLE")


if __name__ == "__main__":
    simulate_attack()
