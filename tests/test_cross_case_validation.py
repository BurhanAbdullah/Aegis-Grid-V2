#!/usr/bin/env python3
import unittest, numpy as np
from core.data_pipeline import generate_physical_dataset
from core.grid_topology import build_ybus, compute_h_x, compute_jacobian_H, get_ieee_case_data
from core.xmon_model import PowerSystemStateEstimator, QuorumLogic
CASES=("case9","case14","case30","case118")
class TestCrossCaseScientificContract(unittest.TestCase):
 def test_all_case_jacobians_match_finite_difference(self):
  for name in CASES:
   c=get_ieee_case_data(name); _,G,B=build_ybus(c); n=c["num_buses"]; r=np.random.RandomState(1000+n)
   x=np.r_[r.normal(0,.02,n-1),1+r.normal(0,.005,n)]; H=compute_jacobian_H(x,G,B); fd=np.zeros_like(H); e=1e-6
   for j in range(x.size):
    xp,xm=x.copy(),x.copy(); xp[j]+=e; xm[j]-=e; fd[:,j]=(compute_h_x(xp,G,B)-compute_h_x(xm,G,B))/(2*e)
   self.assertLess(float(np.max(np.abs(H-fd))),1e-5,name)
 def test_all_case_seeded_generation_is_reproducible(self):
  for name in CASES:
   a=generate_physical_dataset(name,12,6,seed=12345); b=generate_physical_dataset(name,12,6,seed=12345)
   for block,key in (("calibration","z"),("calibration","iat"),("test","z"),("test","iat")): np.testing.assert_array_equal(a[block][key],b[block][key],err_msg=name)
 def test_all_case_estimator_outputs_are_finite(self):
  for name in CASES:
   d=generate_physical_dataset(name,3,seed=2222); e=PowerSystemStateEstimator(name)
   for z in d["calibration"]["z"]:
    o=e.step(z); self.assertTrue(np.isfinite(o["nis"]),name); self.assertGreaterEqual(o["nis"],0,name)
   self.assertGreaterEqual(float(np.linalg.eigvalsh(e.P).min()),-1e-12,name)
 def test_quorum_truth_table(self):
  for n in (0,1):
   for c in (0,1):
    for j in (0,1):
     r=QuorumLogic.evaluate(bool(n),bool(c),bool(j)); v=n+c+j; self.assertEqual(r["d_k2"],v>=2); self.assertEqual(r["d_k1"],v>=1)
if __name__=="__main__": unittest.main()
