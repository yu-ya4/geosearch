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

        Args:
            mat: numpy.matrix
                SVDする行列

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

        Args:
            mat: numpy.matrix
                LSAを適用する行列
            k: int
                圧縮する次元数

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

        Args:
            mat: numpy.matrix
                PMFを適用する行列
        Returns:
            適用結果
        """

    def factorization_machine(self):
        """
        行列にFactorization Machineを適用する

        Args:
            mat: numpy.matrix

        Returns:
            適用結果
        """
