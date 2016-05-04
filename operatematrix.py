#!/usr/local/bin/python3
# -*- coding: utf-8

import math
import numpy as np
from scipy import linalg

def svd(mat):
    mat = np.matrix(mat)
    #print(mat)

    #rank = np.linalg.matrix_rank(mat)
    #print(rank)

    U, s, V = np.linalg.svd(mat, full_matrices=False)
    S = np.diag(s)
    #print(U)
    #print(S)
    #print(V)
    #mat_svd = np.dot(np.dot(U, S), V)
    #print(mat_svd)

    k = 200
    #print("ランクk=%d 累積寄与率=%f" % (k, sum(s[:k]) / sum(s)))
    S = np.zeros((len(s),len(s)))
    S[:k, :k] = np.diag(s[:k])

    mat_rank = np.dot(U, np.dot(S, V))
    #print(mat_rank)
    return mat_rank

def get_svd_sim(act):
    acts = []
    #行動のリストを読み込む
    f = open('../acts_new_list.txt', 'r')
    for line in f:
        line = line.replace('\n', '')
        line = line.split(':')
        ac = line[0] + line[1]
        acts.append(ac)
    act_num = len(acts)

    act_id = acts.index(act)

    svd_mat = []
    f = open('../svd_new_result.txt', 'r')
    for line in f:
        line = line.replace('\n', '')
        line = line.split(' ')
        for i in range(len(line)):
            if line[i] == '':
                del line[i]
                continue
            line[i] = float(line[i])
        svd_mat.append(line)

    in_vec = svd_mat[act_id]
    res = {}
    for i in range(0, act_num):
        if i == act_id:
            continue
        sim = cos(in_vec, svd_mat[i])
        act = acts[i]
        res[act] = float(sim)

    r = {}
    count = 0
    for ac, score in sorted(res.items(), key = lambda x:x[1], reverse = True):
        if count == 5:
            break
        r[ac] = score
        #print(ac + ':' + str(score))
        count +=1

    return r
