class CUSUMDetector:
    def __init__(self, mu0=200.0, delta=400.0, h=5.0):
        self.mu0 = mu0
        self.kappa = delta / 2.0
        self.h = h
        self.C_pos = 0.0

    def update(self, packet_rate):
        self.C_pos = max(0.0, self.C_pos + packet_rate - self.mu0 - self.kappa)
        return {"C_pos": round(self.C_pos,4), "h": self.h,
                "alarm": bool(self.C_pos > self.h), "rate": packet_rate}

    def reset(self):
        self.C_pos = 0.0
