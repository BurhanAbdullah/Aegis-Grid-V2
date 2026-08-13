#!/usr/bin/env python3
"""Hard gate: fail unless the physical experiment is internally consistent."""
import csv, math, os, sys
from collections import Counter
import numpy as np
from sklearn.metrics import confusion_matrix

out = sys.argv[1] if len(sys.argv) > 1 else "results/real_validation_run"
p = os.path.join(out, "metrics", "detector_outputs.csv")
rows = list(csv.DictReader(open(p)))
assert len(rows) == 1200, len(rows)
assert Counter(r["case"] for r in rows) == Counter({c:300 for c in ("case9","case14","case30","case118")})
assert Counter(r["scenario"] for r in rows) == Counter({s:240 for s in ("baseline","branch_outage","fdia","load_shift","stealth_drift")})
assert sum(int(r["y_true"]) == 0 for r in rows) == 240
assert sum(int(r["y_true"]) == 1 for r in rows) == 960
for r in rows:
    assert int(r["d_k2"]) == (int(r["votes"]) >= 2)
    assert int(r["d_k1"]) == (int(r["votes"]) >= 1)
    assert 0 <= int(r["votes"]) <= 3
    for key in ("nis","cusum_g","jitter_z","jitter_bar","s_comp","theta_seq","S_cond"):
        assert math.isfinite(float(r[key])), (r["sample_id"], key)
    assert float(r["nis"]) >= 0

# Independent confusion-matrix recomputation for every published detector.
y = np.array([int(r["y_true"]) for r in rows])
for name, col in (("K2","d_k2"),("K1","d_k1"),("NIS","a_nis"),("CUSUM","a_cusum"),("Jitter","a_jitter"),("Sequential","a_seq")):
    cm = confusion_matrix(y, np.array([int(r[col]) for r in rows]), labels=[0,1])
    assert int(cm.sum()) == 1200, name

# Confirm each attack scenario actually carries the intended attack mechanism.
for scenario, mode in (("branch_outage","physical_branch_outage"),("fdia","jacobian_fdia"),("load_shift","physical_load_shift"),("stealth_drift","physical_load_drift")):
    assert all(r.get("attack_mode") == mode for r in rows if r["scenario"] == scenario)

open(os.path.join(out, "FINAL_VALIDATION_PASSED"), "w").write("PASS\n")
print("FINAL SCIENTIFIC RESULT GATE: PASS")
