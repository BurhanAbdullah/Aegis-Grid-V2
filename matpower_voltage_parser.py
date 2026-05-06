import subprocess
import re
import time
import os

MATPOWER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "matpower"
)

def run_with_voltages(case, attack_code="", matpower_path=None):

    mp = matpower_path or MATPOWER_PATH

    lines = [
        f"addpath(genpath('{mp}'));",
        f"addpath('{mp}/lib');",

"warning('off','all');",

        "if exist('runpf','file') ~= 2;",
        "  disp('RUNPF_MISSING');",
        "  quit(1);",
        "end;",

        f"mpc = loadcase('{case}');",
    ]

    if attack_code:
        lines.append(attack_code)

    lines += [

        "results = runpf(mpc);",

        "if results.success;",

        "  disp('PF_SUCCESS');",

        "  V = results.bus(:,8);",

        "  fprintf('VOLTAGES: ');",
        "  fprintf('%.6f ', V);",
        "  fprintf('\\n');",

        "else;",
        "  disp('PF_FAILED');",
        "end;",
    ]

    script = "\n".join(lines)

    cmd = [
        "octave",
        "--quiet",
        "--eval",
        script
    ]

    t0 = time.time()

    try:

        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        latency = time.time() - t0

        out = r.stdout + "\n" + r.stderr

    except Exception as e:

        return {
            "success": False,
            "voltages": [],
            "delta_v": 0.0,
            "latency": 0.0,
            "error": str(e)
        }

    if "RUNPF_MISSING" in out:
        return {
            "success": False,
            "voltages": [],
            "delta_v": 0.0,
            "latency": round(latency,3),
            "error": "MATPOWER runpf() not found",
            "raw_output": out
        }

    if "PF_FAILED" in out:
        return {
            "success": False,
            "voltages": [],
            "delta_v": 0.0,
            "latency": round(latency,3),
            "error": "Power flow did not converge",
            "raw_output": out
        }

    success = "PF_SUCCESS" in out

    voltages = []

    m = re.search(r"VOLTAGES:\s*([\d\.\s\-eE]+)", out)

    if m:
        try:
            voltages = [
                float(v)
                for v in m.group(1).split()
                if v
            ]
        except:
            voltages = []

    delta_v = (
        sum(abs(v - 1.0) for v in voltages) / len(voltages)
        if voltages else 0.0
    )

    return {
        "success": success,
        "voltages": voltages,
        "delta_v": round(delta_v, 6),
        "latency": round(latency, 3),
        "raw_output": out
    }


if __name__ == "__main__":

    for c in ["case9", "case14", "case30", "case118"]:

        print("\n==============================")
        print("CASE:", c)
        print("==============================")

        r = run_with_voltages(c)

        print(r)
