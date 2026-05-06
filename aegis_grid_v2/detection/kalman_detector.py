import numpy as np
from scipy.stats import chi2

class KalmanAnomalyDetector:
    def __init__(self, n=4, alpha=0.01):
        self.n = n
        self.gamma = chi2.ppf(1 - alpha, df=n)
        self.A = np.eye(n) * 0.98
        self.C = np.eye(n)
        self.Q = np.eye(n) * 1e-4
        self.R = np.eye(n) * 1e-2
        self.x_hat = np.zeros(n)
        self.P = np.eye(n)

    def update(self, z):
        z = np.asarray(z, dtype=float)
        x_pred = self.A @ self.x_hat
        P_pred = self.A @ self.P @ self.A.T + self.Q
        S = self.C @ P_pred @ self.C.T + self.R
        e = z - self.C @ x_pred
        nis = float(e @ np.linalg.solve(S, e))
        K = P_pred @ self.C.T @ np.linalg.inv(S)
        self.x_hat = x_pred + K @ e
        self.P = (np.eye(self.n) - K @ self.C) @ P_pred
        return {"nis": round(nis,4), "threshold": round(self.gamma,4),
                "anomaly": bool(nis > self.gamma), "innovation": e.tolist()}
