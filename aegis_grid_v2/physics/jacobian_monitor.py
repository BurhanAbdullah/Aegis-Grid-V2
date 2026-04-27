"""
Jacobian condition monitoring for voltage stability precursor detection.

Tracks:
cond(J)
lambda_min(J)

Used as early-warning indicator before PF divergence.
"""

import numpy as np


class JacobianMonitor:

    def __init__(self):
        pass


    def condition_number(self, J):

        return np.linalg.cond(J)


    def smallest_eigenvalue(self, J):

        eigvals = np.linalg.eigvals(J)

        return np.min(np.real(eigvals))


    def instability_alarm(self, J, cond_threshold=1e6):

        cond = self.condition_number(J)

        return cond > cond_threshold
