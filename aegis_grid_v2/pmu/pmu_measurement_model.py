"""
PMU measurement vector

z_pmu = [V, I]
"""

import numpy as np


class PMUModel:

    def __init__(self):
        pass

    def measure(self, V, I):
        return np.concatenate([V, I])
