import numpy as np
from collections import deque

class JitterDetector:
    def __init__(self, mu=0.004, sigma=0.001, eta_sigma=3.5, eta_mu=2.0, W=50):
        self.mu = mu
        self.sigma = sigma
        self.eta_sigma = eta_sigma
        self.eta_mu = eta_mu
        self.window = deque(maxlen=W)

    def calibrate(self, samples):
        arr = np.array(samples)
        self.mu = float(arr.mean())
        self.sigma = float(arr.std()) + 1e-9

    def update(self, delta_t):
        jitter = delta_t - self.mu
        z = abs(jitter) / self.sigma
        self.window.append(z)
        wm = float(np.mean(self.window))
        detected = bool(z > self.eta_sigma and wm > self.eta_mu)
        return {"delta_t": round(delta_t,9), "jitter": round(jitter,9),
                "z_score": round(z,4), "window_mean_z": round(wm,4),
                "detected": detected}
