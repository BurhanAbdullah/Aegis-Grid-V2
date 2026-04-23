import sys, os, csv, json, random
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from matpower_voltage_parser import run_with_voltages
from aegis_grid_v2.detection.kalman_detector import KalmanAnomalyDetector
from aegis_grid_v2.detection.cusum_detector import CUSUMDetector
from v3_fabric.core.jitter_detector import JitterDetector
from v4_hive.core.hive_consensus import HiveConsensus

CASES = ["case9", "case14", "case30", "case118"]
ATTACKS = {
    "baseline":    "",
    "branch1_out": "mpc.branch(1, BR_STATUS) = 0;",
    "branch2_out": "mpc.branch(2, BR_STATUS) = 0;",
    "branch3_out": "mpc.branch(3, BR_STATUS) = 0;",
}
SCADA_CYCLES = 5   # simulate 5 scan cycles per scenario
WARMUP_STEPS = 20  # Kalman warmup on nominal

os.makedirs("experiments/results", exist_ok=True)
rows = []
print("\n" + "="*72)
print("  MACPR Full Experiment Pipeline  (v2 - fixed)")
print("="*72)

for case in CASES:
    print(f"\n--- {case} ---")
    rng = random.Random(42)   # one RNG per case, not reset per attack

    # Get nominal voltages for Kalman warmup
    base = run_with_voltages(case)
    n_feat = min(4, len(base["voltages"])) if base["voltages"] else 4
    nominal_z = (base["voltages"] + [1.0]*n_feat)[:n_feat]

    for attack_name, attack_code in ATTACKS.items():
        is_atk = (attack_name != "baseline")

        # Fresh detectors per scenario
        kalman = KalmanAnomalyDetector(n=n_feat)
        cusum  = CUSUMDetector(mu0=200.0, delta=400.0, h=5.0)
        # Calibrate jitter: baseline IAT = 4ms +/- 0.5ms
        jitter = JitterDetector(mu=0.004, sigma=0.0005, eta_sigma=3.5, eta_mu=2.0, W=20)
        hive   = HiveConsensus(persistence=3)

        # Warm up Kalman on nominal (20 steps)
        for _ in range(WARMUP_STEPS):
            noise = [rng.gauss(0, 0.001) for _ in range(n_feat)]
            kalman.update([v + n for v, n in zip(nominal_z, noise)])

        # Run MATPOWER once to get physical ground truth
        r = run_with_voltages(case, attack_code)
        pf_div  = not r["success"]
        delta_v = None if pf_div else r["delta_v"]
        lat_pf  = r["latency"]

        if r["voltages"]:
            atk_z = (r["voltages"] + [1.0]*n_feat)[:n_feat]
        else:
            atk_z = [0.0]*n_feat  # total loss on divergence

        # Simulate SCADA_CYCLES observation cycles
        cycle_rows = []
        for cycle in range(SCADA_CYCLES):
            # Physical measurement with noise
            meas_noise = [rng.gauss(0, 0.001) for _ in range(n_feat)]
            z_meas = [v + n for v, n in zip(atk_z, meas_noise)]
            kal = kalman.update(z_meas)

            # Network observables: attack raises pkt_rate and jitter
            if is_atk:
                pkt_rate = rng.gauss(1800, 80)
                delta_t  = rng.gauss(0.004, 0.006)  # sigma >> baseline -> z>>3.5
                traffic_ent = 1.2
            else:
                pkt_rate = rng.gauss(200, 20)
                delta_t  = rng.gauss(0.004, 0.0004)
                traffic_ent = 3.8

            cus = cusum.update(pkt_rate)
            jit = jitter.update(delta_t)
            brk = 1 if pf_div else 0

            h = hive.step(
                nis=kal["nis"], state_dev=(delta_v or 0.0),
                timing_det=jit["detected"], brk_hamming=brk,
                cusum_stat=cus["C_pos"], traffic_ent=traffic_ent,
                pf_diverged=pf_div,
            )
            cycle_rows.append((kal, cus, jit, h))

        # Use final cycle for reporting
        kal, cus, jit, h = cycle_rows[-1]
        mitigated = bool(h["mitigation"])

        recovery_dv = None
        if mitigated and is_atk:
            rec = run_with_voltages(case, "")
            recovery_dv = rec["delta_v"]

        row = {
            "case": case, "attack": attack_name,
            "pf_success": r["success"],
            "delta_v": delta_v,
            "nis": kal["nis"], "kalman_anomaly": kal["anomaly"],
            "cusum_stat": cus["C_pos"], "cusum_alarm": cus["alarm"],
            "jitter_z": jit["z_score"], "jitter_detected": jit["detected"],
            "v_p": h["v_p"], "v_a": h["v_a"], "v_m": h["v_m"],
            "consensus": h["consensus"], "mitigation": mitigated,
            "level": h["level"], "threat_score": h["threat_score"],
            "latency_pf_s": lat_pf, "recovery_dv": recovery_dv,
            "n_cycles": SCADA_CYCLES,
        }
        rows.append(row)

        tag = "MITIGATE" if mitigated else ("ATTACK" if is_atk else "OK")
        dv_str = f"{delta_v:.4f}" if delta_v is not None else "DIVERG"
        print(f"  {attack_name:14s} | pf={str(r['success']):5s} | dV={dv_str} | "
              f"NIS={kal['nis']:8.3f} | C+={cus['C_pos']:7.2f} | "
              f"jz={jit['z_score']:.2f} | vP={h['v_p']} vA={h['v_a']} vM={h['v_m']} "
              f"| [{tag}]")

csv_path  = "experiments/results/macpr_results.csv"
json_path = "experiments/results/macpr_results.json"
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
with open(json_path, "w") as f:
    json.dump(rows, f, indent=2)

print("\n" + "="*72)
print(f"  Saved: {csv_path}")
print(f"  Saved: {json_path}")
print("="*72 + "\n")
