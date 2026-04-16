import subprocess

def run_case(case="case9"):
    cmd = f"octave --quiet --eval \"runpf('{case}')\""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout


def converged(output):
    return "PF successful" in output


if __name__ == "__main__":
    output = run_case("case9")

    print(output)

    if converged(output):
        print("Grid stable")
    else:
        print("Grid unstable")
