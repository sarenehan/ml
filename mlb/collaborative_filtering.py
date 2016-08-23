"""
tutorial:
http://bugra.github.io/work/notes/2014-04-19/alternating-least-squares-method-
for-collaborative-filtering/
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
import math


def load_data():
    return pd.DataFrame(np.load('mlb/reccomendation_system_data'))


def changes_nulls_to_zeros(data):
    return np.nan_to_num(data)


def factorize_matrix(matrix):
    model = NMF(n_components=2, init='random', random_state=0)
    model.fit(matrix)
    import pdb
    pdb.set_trace()
    model.components_


######
import numpy


def matrix_factorization(R, P, Q, K, steps=5000, alpha=0.0002, beta=0.02):
    """
    tutorial: http://www.quuxlabs.com/blog/2010/09/matrix-factorization-a
    -simple-tutorial-and-implementation-in-python/
    """
    Q = Q.T
    for step in range(steps):
        print('Iteration {} of {}'.format(step, steps))
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - numpy.dot(P[i, :], Q[:, j])
                    for k in range(K):
                        P[i][k] = P[i][k] + alpha * \
                            (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * \
                            (2 * eij * P[i][k] - beta * Q[k][j])
        # eR = numpy.dot(P, Q)
        e = 0
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - numpy.dot(P[i, :], Q[:, j]), 2)
                    for k in range(K):
                        e = e + (beta / 2) * \
                            (pow(P[i][k], 2) + pow(Q[k][j], 2))
        print('Error: {}'.format(e))
        if e < 0.001:
            break
    return P, Q.T

######

if __name__ == '__main__':
    data = load_data()
    R = changes_nulls_to_zeros(data)
    # factorize_matrix(data)
    # get_cosine_similarities(data)
    N = len(R)
    M = len(R[0])
    K = 2
    P = numpy.random.rand(N, K)
    Q = numpy.random.rand(M, K)
    nP, nQ = matrix_factorization(R, P, Q, K)
    nR = numpy.dot(nP, nQ.T)
    import pdb
    pdb.set_trace()
