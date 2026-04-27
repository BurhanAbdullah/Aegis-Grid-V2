"""
Adaptive threshold estimator

gamma(k+1) = alpha*gamma(k) + (1-alpha)*metric
"""


class AdaptiveThreshold:

    def __init__(self, gamma0=5.0, alpha=0.95):
        self.gamma = gamma0
        self.alpha = alpha

    def update(self, metric):
        self.gamma = self.alpha * self.gamma + (1 - self.alpha) * metric
        return self.gamma
