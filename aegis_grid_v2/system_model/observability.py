"""
Observability rank test
"""

import numpy as np


def observability_matrix(A, C):

    n = A.shape[0]

    O = C

    for i in range(1, n):

        O = np.vstack((O, C @ np.linalg.matrix_power(A, i)))

    return O


def is_observable(A, C):

    O = observability_matrix(A, C)

    return np.linalg.matrix_rank(O) == A.shape[0]
