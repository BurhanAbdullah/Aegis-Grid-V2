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

    def connectivity(self):

        eigvals = np.linalg.eigvals(self.laplacian())

        eigvals = sorted(np.real(eigvals))

        return eigvals[1]
