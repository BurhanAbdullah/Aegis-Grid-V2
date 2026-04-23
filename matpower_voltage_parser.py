import subprocess, re, time, os

MATPOWER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matpower")

def run_with_voltages(case, attack_code="", matpower_path=None):
    mp = matpower_path or MATPOWER_PATH
    lines = [
        "addpath(genpath('" + mp + "'));",
        "addpath(genpath(fullfile('" + mp + "','data')));",
        "define_constants;",
        "mpc = loadcase('" + case + "');",
    ]
    if attack_code:
        lines.append(attack_code)
    lines += [
        "results = runpf(mpc);",
        "if results.success",
        "  disp('PF_SUCCESS');",
        "  V = results.bus(:,8);",
        "  fprintf('VOLTAGES: ');",
        "  fprintf('%.6f ', V);",
        "  fprintf('\\n');",
        "else",
        "  disp('PF_FAILED');",
        "end",
    ]
    script = " ".join(lines)
    cmd = ["octave", "--quiet", "--eval", script]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    latency = time.time() - t0
    out = r.stdout + r.stderr
    success = "PF_SUCCESS" in out
    voltages = []
    m = re.search(r"VOLTAGES:\s*([\d\.\s]+)", out)
    if m:
        voltages = [float(v) for v in m.group(1).split() if v]
    delta_v = (sum(abs(v-1.0) for v in voltages)/len(voltages)) if voltages else 0.0
    return {"success": success, "voltages": voltages,
            "delta_v": round(delta_v,6), "latency": round(latency,3)}
