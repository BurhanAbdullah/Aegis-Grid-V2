"""
Smart-grid stochastic state-space system model

x(k+1) = A x(k) + B u(k) + w(k)
z(k)   = C x(k) + v(k)
"""

import numpy as np


class StateSpaceModel:

    def __init__(self, n):

        self.n = n

        self.A = np.eye(n) * 0.98
        self.B = np.eye(n)
        self.C = np.eye(n)

    def step(self, x, u):

        noise = np.random.normal(0, 0.001, size=self.n)

        return self.A @ x + self.B @ u + noise
