#!/usr/bin/env python3
"""Compute paper-ready confidence intervals and paired McNemar tests from frozen CSV."""
import csv, os, sys
import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import precision_score, recall_score, f1_score

out=sys.argv[1] if len(sys.argv)>1 else "results/real_validation_run"
assert os.path.isfile(os.path.join(out,"FINAL_VALIDATION_PASSED"))
rows=list(csv.DictReader(open(os.path.join(out,"metrics","detector_outputs.csv"))))
y=np.array([int(r["y_true"]) for r in rows]); rng=np.random.RandomState(42)
methods={"XMON_K2":"d_k2","XMON_K1":"d_k1","NIS":"a_nis","CUSUM":"a_cusum","Jitter":"a_jitter","Sequential":"a_seq"}
summary=[]
for name,col in methods.items():
    pred=np.array([int(r[col]) for r in rows]); vals=[]
    for _ in range(2000):
        idx=rng.randint(0,len(y),len(y)); yy=y[idx]; pp=pred[idx]
        vals.append((precision_score(yy,pp,zero_division=0),recall_score(yy,pp,zero_division=0),f1_score(yy,pp,zero_division=0)))
    a=np.asarray(vals); summary.append({"method":name,"precision":precision_score(y,pred,zero_division=0),"precision_ci_low":np.percentile(a[:,0],2.5),"precision_ci_high":np.percentile(a[:,0],97.5),"recall":recall_score(y,pred,zero_division=0),"recall_ci_low":np.percentile(a[:,1],2.5),"recall_ci_high":np.percentile(a[:,1],97.5),"f1":f1_score(y,pred,zero_division=0),"f1_ci_low":np.percentile(a[:,2],2.5),"f1_ci_high":np.percentile(a[:,2],97.5)})
with open(os.path.join(out,"tables","confidence_intervals.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)

comparisons=[]
base=np.array([int(r["d_k2"]) for r in rows])
for name,col in (("NIS","a_nis"),("CUSUM","a_cusum"),("Sequential","a_seq"),("K1","d_k1")):
    other=np.array([int(r[col]) for r in rows]); b=int(np.sum((base==y)&(other!=y))); c=int(np.sum((base!=y)&(other==y)))
    p=1.0 if b+c==0 else float(binomtest(min(b,c),n=b+c,p=0.5).pvalue)
    comparisons.append({"comparison":f"XMON_K2_vs_{name}","b_xmon_correct_other_wrong":b,"c_xmon_wrong_other_correct":c,"exact_mcnemar_p":p})
with open(os.path.join(out,"tables","mcnemar_comparisons.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(comparisons[0].keys())); w.writeheader(); w.writerows(comparisons)
print("STATISTICAL POSTPROCESSING COMPLETE")
