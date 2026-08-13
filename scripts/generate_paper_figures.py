#!/usr/bin/env python3
"""Generate publication figures only after FINAL_VALIDATION_PASSED exists."""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2
from sklearn.metrics import precision_score, recall_score, f1_score, roc_curve, auc, precision_recall_curve

out = sys.argv[1] if len(sys.argv) > 1 else "results/real_validation_run"
assert os.path.isfile(os.path.join(out, "FINAL_VALIDATION_PASSED")), "Scientific gate has not passed; figures are blocked."
rows = list(csv.DictReader(open(os.path.join(out, "metrics", "detector_outputs.csv"))))
figdir = os.path.join(out, "figures"); os.makedirs(figdir, exist_ok=True)
y = np.array([int(r["y_true"]) for r in rows])

# 1. Continuous composite ROC.
s = np.array([float(r["s_comp"]) for r in rows]); fpr, tpr, _ = roc_curve(y, s)
plt.figure(figsize=(6,5), dpi=300); plt.plot(fpr,tpr,lw=2,label=f"Composite score (AUC={auc(fpr,tpr):.4f})"); plt.plot([0,1],[0,1],"--",lw=1)
plt.xlabel("False positive rate"); plt.ylabel("True positive rate"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(figdir,"fig1_roc_curve.png")); plt.close()

# 2. Precision-recall.
p,r,_ = precision_recall_curve(y,s)
plt.figure(figsize=(6,5), dpi=300); plt.plot(r,p,lw=2,label=f"Composite score (PR-AUC={auc(r,p):.4f})"); plt.xlabel("Recall"); plt.ylabel("Precision"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(figdir,"fig2_pr_curve.png")); plt.close()

# 3. Detector comparison.
names=["K=2","K=1","NIS","CUSUM","Jitter","Sequential"]; cols=["d_k2","d_k1","a_nis","a_cusum","a_jitter","a_seq"]
metrics=[[precision_score(y,[int(r[c]) for r in rows],zero_division=0), recall_score(y,[int(r[c]) for r in rows],zero_division=0), f1_score(y,[int(r[c]) for r in rows],zero_division=0)] for c in cols]
x=np.arange(len(names)); w=.25
plt.figure(figsize=(9,5),dpi=300)
for j,label in enumerate(["Precision","Recall","F1"]): plt.bar(x+(j-1)*w,[m[j] for m in metrics],w,label=label)
plt.xticks(x,names); plt.ylim(0,1.05); plt.ylabel("Score"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(figdir,"fig3_detector_comparison.png")); plt.close()

# 4. Case-wise K=2 F1.
cases=["case9","case14","case30","case118"]; vals=[]
for c in cases:
    rr=[r for r in rows if r["case"]==c]; yy=[int(r["y_true"]) for r in rr]; pp=[int(r["d_k2"]) for r in rr]
    vals.append(f1_score(yy,pp,zero_division=0))
plt.figure(figsize=(7,5),dpi=300); plt.bar(cases,vals); plt.ylim(0,1.05); plt.ylabel("K=2 F1-score"); plt.tight_layout(); plt.savefig(os.path.join(figdir,"fig4_casewise_f1.png")); plt.close()

# 5. Scenario-wise K=2 recall.
scenarios=["baseline","branch_outage","fdia","load_shift","stealth_drift"]; vals=[]
for sc in scenarios:
    rr=[r for r in rows if r["scenario"]==sc]; yy=[int(r["y_true"]) for r in rr]; pp=[int(r["d_k2"]) for r in rr]
    vals.append(recall_score(yy,pp,zero_division=0))
plt.figure(figsize=(8,5),dpi=300); plt.bar(scenarios,vals); plt.ylim(0,1.05); plt.ylabel("K=2 recall"); plt.xticks(rotation=15); plt.tight_layout(); plt.savefig(os.path.join(figdir,"fig5_scenario_recall.png")); plt.close()

# 6. Case9 benign NIS against the theoretical chi-square reference.
nis=np.array([float(r["nis"]) for r in rows if r["case"]=="case9" and r["scenario"]=="baseline"]); grid=np.linspace(0,max(70,float(nis.max())*1.1),250)
plt.figure(figsize=(7,5),dpi=300); plt.hist(nis,bins=30,density=True,alpha=.6,label="Empirical benign NIS"); plt.plot(grid,chi2.pdf(grid,df=27),lw=2,label="Chi-square reference (df=27)"); plt.axvline(chi2.ppf(.99,df=27),ls="--",label="99% threshold")
plt.xlabel("NIS"); plt.ylabel("Probability density"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(figdir,"fig6_nis_distribution.png")); plt.close()
print("PUBLICATION FIGURES GENERATED AFTER SCIENTIFIC GATE")
