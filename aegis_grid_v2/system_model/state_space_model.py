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

    def predict(self, x, u):
        noise = np.random.multivariate_normal(np.zeros(self.n), np.eye(self.n))
        return self.A @ x + self.B @ u + noise

    def observe(self, x):
        noise = np.random.multivariate_normal(np.zeros(self.n), np.eye(self.n))
        return self.C @ x + noise
