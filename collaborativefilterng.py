#!/usr/local/bin/python3
# -*- coding: utf-8

import copy
import math
import numpy as np
from scipy import linalg


class CollaborativeFiltering:

    def __init__(self, matrix):
        """
        Args:
            matrix: numpy.matrix
        """
        self.matrix = matrix

    def svd(self):
        """
        行列を特異値分解(SVD)する

        Returns:
            List<numpy.matrix>
            特異値分解された行列3つ
            特異値はリストで返される
        """
        #mat = np.matrix(mat)

        """
        full_matrices:
            1: UとVが正方行列に(次元が合わずに死ぬ??)
            0: UとVのかたちをいい感じに(とりあえずこれでなんとかしてる)
        """
        U, s, V = np.linalg.svd(self.matrix, full_matrices=0)
        #print(s)

        return [U, s, V]


    def lsa(self, k):
        """
        行列にLSAを適用する

        Returns:
            numpy.matrix
            LSAを適用した結果
        """
        rank = np.linalg.matrix_rank(self.matrix)
        # ランク以上の次元数を指定した場合は，ランク数分の特徴量を使用
        #npの仕様上，ランク以上分の特徴量を算出してるっぽい？
        # 負の値が入力された場合はk = 0 とする
        U, s, V = self.svd()
        if k > rank:
            k = rank
        if k < 0:
            k = 0

        #print("ランクk=%d 累積寄与率=%f" % (k, sum(s[:k]) / sum(s)))
        S = np.zeros((len(s),len(s)))
        S[:k, :k] = np.diag(s[:k]) #上からk個の特異値のみを使用

        lsa_mat = np.dot(U, np.dot(S, V))

        return lsa_mat

    def probabilistic_matrix_factorization(self):
        """
        行列にProbabilistic Matrix Factorizationを適用する

        Returns:
            適用結果
        """

    def factorization_machines(self):
        """
        行列にFactorization Machinesを適用する

        Returns:
            適用結果
        """
    def get_rating_error(self, r, p, q):
        return r - np.dot(p, q)


    def get_error(self, R, P, Q, beta):
        error = 0.0
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] == 0:
                    continue
                error += pow(self.get_rating_error(R[i][j], P[:,i], Q[:,j]), 2)
        error += beta/2.0 * (np.linalg.norm(P) + np.linalg.norm(Q))
        return error

    def matrix_factorization(self, K, steps=5000, alpha=0.0002, beta=0.02, threshold=0.001):
        """
        行列にMatrix Factorizationを適用する

        Args:
            K: the number of latent features
            steps: the maximum number of steps to perform the optimisation
            alfha: the learning rate
            beta: the regularization parameter,  avoid overfitting
            threshold: when error is under threshold, break

        """
        R = np.array(self.matrix)
        P = np.random.rand(K, len(R))
        Q = np.random.rand(K, len(R[0]))

        for step in range(steps):
            print(step)
            for i in range(len(R)):
                for j in range(len(R[i])):
                    if R[i][j] == 0:
                        continue
                    err = self.get_rating_error(R[i][j], P[:, i], Q[:, j])
                    for k in range(K):
                        P[k][i] += alpha * (2 * err * Q[k][j])
                        Q[k][j] += alpha * (2 * err * P[k][i])
            error = self.get_error(R, P, Q, beta)
            if error < threshold:
                break
        return np.matrix(P), np.matrix(Q)
