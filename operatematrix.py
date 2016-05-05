#!/usr/local/bin/python3
# -*- coding: utf-8

import math
import numpy as np
from scipy import linalg

def svd(mat):
    """
    行列を特異値分解(SVD)する

    Args:
        mat: 行列

    Returns:
        特異値分解された行列3つ
        特異値はリストで返される
    """
    mat = np.matrix(mat)

    rank = np.linalg.matrix_rank(mat)
    print(rank)

    U, s, V = np.linalg.svd(mat, full_matrices=False)

    return [U, s, V]


def lsa(mat, k):
    """
    行列にLSAを適用する

    Args:
        mat: LSAを適用する行列
        k: 圧縮する次元数

    Returns:
        LSAを適用した結果
    """
    U, s, V = svd(mat)

    #print("ランクk=%d 累積寄与率=%f" % (k, sum(s[:k]) / sum(s)))
    S = np.zeros((len(s),len(s)))
    S[:k, :k] = np.diag(s[:k]) #上から個の特異値のみを使用

    lsa_mat = np.dot(U, np.dot(S, V))

    return lsa_mat


def read_act_geoclass_matrix():
    """
    テキストファイルから行動地物クラス行列を読み込み返す

    Returns:
        行動地物クラス行列
    """
    act_geoclass_mat = [] #行動-地物クラス行列
    f = open('./act-geoclass-matrix.txt', 'r')
    for line in f:
        line = line.replace('\n', '')
        line = line.split(' ')
        #print(line)
        act_geoclass_mat.append(line)
        if line == '':
            break
    f.close()

    return act_geoclass_mat


def get_top_k_column_index(mat, row, k):
    """
    指定した行の上位k件のインデックス番号を配列で返す

    Args:
        mat: 行列
        row: 行番号
        l: 取得するインデックス件数

    Returns:
        指定した行の上位k件のインデックス番号からなる配列
    """


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


def get_lsi_matrix(act):
    '''
    行動地物クラスマトリックスにLSIを適用する

    Retrun:
        LSIを適用したマトリックス
    '''

    acts = {} #食事楽しめる: 278
    f = open('./act-list.txt', 'r') #行動辞書を読み込む
    i = 0
    for line in f:
        line = line.replace('\n', '')
        line = line.replace(':', '')
        acts[line] = i
        i += 1
    f.close()

    geoclasses = []
    f = open('./geoclass-list.txt', 'r') #地物クラスリストを読み込む
    for line in f:
        geo = line.replace('\n', '')
        geos.append(geo)
    f.close()

    act_geo_mat = []
    f = open('../svd_new_result.txt', 'r') #SVDした結果のマトリックスを読み込む
    for line in f:
        line = line.replace('\n', '')
        line = line.split(' ')
        for i in range(len(line)):
            if line[i] == '':
                del line[i]
                continue
            line[i] = line[i]
        act_geo_mat.append(line)
    f.close()

    act_index = int(acts[act])
    geos_num = len(geos)

    vec = {} #地物id: スコア
    for i in range(0, geos_num):
        g = act_geo_mat[act_index]
        vec[i] = float(g[i])

    res = {}
    #count = 0
    for geo_id, score in sorted(vec.items(), key = lambda x:x[1], reverse = True):
        #if count ==20:
            #break
        geo = geos[geo_id]
        res[geo] = score
        if score >= 1:
            print(geo + ':' + str(score))
        #count += 1

    return res

if __name__ == '__main__':

    mat = [[1, 2, 3], [1, 2, 0], [2, 4, 6], [1, 1, 0]]
    lsa_mat = lsa(mat, 3)

    act_geoclass_mat = read_act_geoclass_matrix()

    print(len(act_geoclass_mat[1]))
