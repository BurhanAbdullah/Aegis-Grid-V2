import numpy as np

class JitterDetector:
    def __init__(self, threshold=2.5):
        self.threshold = threshold

    def detect(self, x):
        z = abs(x)
        return z > self.threshold
