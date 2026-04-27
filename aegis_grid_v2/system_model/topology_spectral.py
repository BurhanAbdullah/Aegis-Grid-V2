"""
Topology spectral resilience metric

L = D - A
lambda_2(L) = algebraic connectivity
"""

import numpy as np


class SpectralResilience:

    def __init__(self, adjacency):
        self.A = adjacency

    def laplacian(self):
        D = np.diag(self.A.sum(axis=1))
        return D - self.A

    def algebraic_connectivity(self):
        L = self.laplacian()
        eigvals = np.sort(np.real(np.linalg.eigvals(L)))
        return eigvals[1]
