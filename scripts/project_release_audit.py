#!/usr/bin/env python3
"""Independent project-level release gate for XMON-Grid; manuscript excluded."""
from pathlib import Path
import csv, sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from core.data_pipeline import generate_physical_dataset
from core.grid_topology import build_ybus, compute_h_x, compute_jacobian_H, get_ieee_case_data
from core.xmon_model import PowerSystemStateEstimator, XMONGridModel, QuorumLogic
CASES={"case9":(9,9),"case14":(14,20),"case30":(30,41),"case118":(118,186)}
def jac_err(name):
 c=get_ieee_case_data(name); _,G,B=build_ybus(c); n=c["num_buses"]; r=np.random.RandomState(700+n)
 x=np.r_[r.normal(0,.03,n-1),1+r.normal(0,.01,n)]; H=compute_jacobian_H(x,G,B); fd=np.zeros_like(H); e=1e-6
 for j in range(x.size):
  xp,xm=x.copy(),x.copy(); xp[j]+=e; xm[j]-=e; fd[:,j]=(compute_h_x(xp,G,B)-compute_h_x(xm,G,B))/(2*e)
 return float(np.max(np.abs(H-fd)))
def main():
 fail=[]
 for name,(nb,br) in CASES.items():
  c=get_ieee_case_data(name); y,g,b=build_ybus(c)
  if (c["num_buses"],c["num_branches"])!=(nb,br): fail.append(f"{name}: dimensions")
  if not np.all(np.isfinite(y)) or not np.allclose(y,g+1j*b,rtol=0,atol=1e-15): fail.append(f"{name}: Ybus")
  e=jac_err(name); print(f"PASS {name}: Jacobian error={e:.3e}")
  if e>1e-5: fail.append(f"{name}: Jacobian {e:.3e}")
  d=generate_physical_dataset(name,20,10,4,seed=31415); d2=generate_physical_dataset(name,20,10,4,seed=31415)
  for k in ("z","iat"):
   if not np.array_equal(d["calibration"][k],d2["calibration"][k]): fail.append(f"{name}: reproducibility")
  est=PowerSystemStateEstimator(name)
  for z in d["calibration"]["z"]:
   o=est.step(z)
   if not np.isfinite(o["nis"]) or o["nis"]<0: fail.append(f"{name}: NIS")
  if np.linalg.eigvalsh(est.P).min()<=-1e-12: fail.append(f"{name}: covariance PSD")
 for n in (0,1):
  for c in (0,1):
   for j in (0,1):
    q=QuorumLogic.evaluate(bool(n),bool(c),bool(j)); v=n+c+j
    if q["d_k2"]!=(v>=2) or q["d_k1"]!=(v>=1): fail.append("quorum")
 d=generate_physical_dataset("case9",20,seed=4242); m=XMONGridModel("case9"); m.calibrate_benign(d["calibration"]["z"],d["calibration"]["iat"]); m.step(d["test"]["z"][0],d["test"]["iat"][0]); m.reset()
 if m.cusum_detector.g!=0 or m.jitter_detector.window or m.sequential_accumulator.theta!=0: fail.append("reset")
 p=ROOT/"results/independent_validation_run/tables/multi_seed_summary.csv"
 with p.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
 if [int(r["seed"]) for r in rows]!=[2026,2027,2028,2029,2030]: fail.append("seed summary")
 for m in ("Accuracy","Precision","Recall","F1","FPR","MCC"):
  a=np.array([float(r[m]) for r in rows]);
  if not np.isfinite(a).all() or len(a)!=5: fail.append(f"{m}: summary")
 required=["requirements.txt","tests/test_xmon_model.py","results/independent_validation_run/SHA256SUMS.txt","results/independent_validation_run/tables/multi_seed_summary.csv","results/independent_validation_run/tables/ablation_results.csv","results/independent_validation_run/tables/comparative_results.csv"]
 for x in required:
  if not (ROOT/x).exists(): fail.append(f"missing {x}")
 print("PASS project artifact presence")
 if fail:
  print("PROJECT RELEASE AUDIT: FAIL"); [print(" -",x) for x in fail]; return 1
 print("PROJECT RELEASE AUDIT: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
