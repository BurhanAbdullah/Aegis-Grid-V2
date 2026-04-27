"""
Residual detector

r = z − h(x)
"""

import numpy as np


def residual(z, hx):

    return np.linalg.norm(np.array(z) - np.array(hx))


def residual_alarm(r, gamma=0.02):

    return r > gamma
