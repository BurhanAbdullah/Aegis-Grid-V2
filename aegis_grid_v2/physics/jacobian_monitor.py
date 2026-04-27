"""
Jacobian condition monitoring for voltage stability precursor detection.

Tracks:
  cond(J)      — condition number
  lambda_min(J) — smallest singular value

Used as early-warning indicator before power flow divergence.
"""

import numpy as np


class JacobianMonitor:

    def __init__(self, cond_threshold=1e6):
        self.cond_threshold = cond_threshold
        self.history = []

    def evaluate(self, J):
        cond = np.linalg.cond(J)
        sv = np.linalg.svd(J, compute_uv=False)
        lambda_min = sv[-1]
        self.history.append({"cond": cond, "lambda_min": lambda_min})
        return cond, lambda_min

    def is_unstable(self, J):
        cond, _ = self.evaluate(J)
        return cond > self.cond_threshold
