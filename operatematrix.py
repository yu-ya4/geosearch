#!/usr/local/bin/python3
# -*- coding: utf-8

import copy
import math
import numpy as np
from scipy import linalg

def svd(mat):
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
    U, s, V = np.linalg.svd(mat, full_matrices=0)
    #print(s)

    return [U, s, V]


def lsa(mat, k):
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
    rank = np.linalg.matrix_rank(mat)
    # ランク以上の次元数を指定した場合は，ランク数分の特徴量を使用
    #npの仕様上，ランク以上分の特徴量を算出してるっぽい？
    # 負の値が入力された場合はk = 0 とする
    U, s, V = svd(mat)
    if k > rank:
        k = rank
    if k < 0:
        k = 0

    #print("ランクk=%d 累積寄与率=%f" % (k, sum(s[:k]) / sum(s)))
    S = np.zeros((len(s),len(s)))
    S[:k, :k] = np.diag(s[:k]) #上からk個の特異値のみを使用

    lsa_mat = np.dot(U, np.dot(S, V))

    return lsa_mat

def probalistic_matrix_factorization(mat):
    """
    行列にProbalistic Matrix Factorizationを適用する

    Args:
        mat: numpy.matrix
            PMFを適用する行列
    Returns:
        適用結果
    """

def factorization_machine(mat):
    """
    行列にFactorization Machineを適用する

    Args:
        mat: numpy.matrix

    Returns:
        適用結果
    """



def read_act_geoclass_matrix():
    """
    テキストファイル("act-geoclass-matrix.txt")から行動地物クラス行列を読み込み返す

    Returns:
        List<List<float>>
        行動地物クラス行列
    """
    act_geoclass_mat = [] #行動-地物クラス行列
    f = open('./act-geoclass-matrix.txt', 'r')
    for line in f:
        line = line.replace('\n', '')
        line = line.split(' ')
        for i in range(len(line)):
            #行末の空白対策
            if line[i] == "":
                del line[i]
                continue
            line[i] = float(line[i])

        act_geoclass_mat.append(line)
        if line == '':
            break
    f.close()

    return act_geoclass_mat

def read_act_list():
    """
    テキストファイル("act-list.txt")から行動のリストを読み込み返す

    Returns:
        List<string>
        行動のリスト
    """
    act_list = []

    f = open('./act-list.txt', 'r')
    for line in f:
        line = line.replace('\n', '')
        act_list.append(line)
    f.close()

    return act_list

def read_geoclass_list():
    """
    テキストファイル(geoclass-list.txt)から地物クラスのリストを読み込み返す

    Returns:
        List<string>
        地物クラスのリスト
    """
    geoclass_list = []
    f = open('./geoclass-list.txt', 'r') #地物クラスリストを読み込む
    for line in f:
        geoclass = line.replace('\n', '')
        geoclass_list.append(geoclass)
    f.close()

    return geoclass_list


def get_topk_column_index(mat, row, k):
    """
    指定した行の上位k件のインデックス番号をリストで返す

    Args:
        mat: 行列
        row: 行番号
        k: 取得するインデックス件数

    Returns:
        指定した行の上位k件のインデックス番号からなるリスト
    """
    matrix = copy.deepcopy(mat)
    topk_index = []
    column = matrix[row]

    while k > 0:
        #print(column)
        max_index = np.nanargmax(column)
        topk_index.append(max_index)
        column[0, max_index] = -10000
        #column[0, max_index] = float("num") nanargmaxが正しく動いてくれてない？
        k -= 1

    return topk_index


def get_topk_geoclass(act, mat, k):
    """
    入力行動についてスコアが高い上位k件の地物クラスとそのスコアからからなる2次元リストを返す

    Args:
        act: 行動(ex."暇:潰せる")
        mat: 対象とする行動地物クラス行列
        k: 取得する地物クラス件数

    Returns:
        地物クラスとそのスコアの辞書(ex. [["駅", 11], ["カフェ", 8], ...])
    """

    act_list = read_act_list()
    act_index = act_list.index(act)

    topk_index = get_topk_column_index(mat, act_index, k)
    geoclass_list = read_geoclass_list()

    result = []

    for i in range(k):
        geoclass = geoclass_list[topk_index[i]]
        score = mat[act_index, topk_index[i]]
        if score <= 0.0:
            break
        if score < 1.0:
            geoclass = "*" + geoclass
        result.append([geoclass, score])
    return result

def read_geoclass_true_list(act):
    """
    テキストファイルから行動ごとの地物クラスの正誤表リストを読み込み返す

    Args:
        行動(ex. "デート:する")
    Returns:
        地物クラスの正誤表のリスト
    """
    act_list = read_act_list()
    act_index = act_list.index(act)

    filename = str(act_index) + "-true-list.txt"

    true_list = []
    f = open('./geoclass_true_list/' + filename, 'r')
    for line in f:
        line = int(line.replace('\n', ''))
        true_list.append(line)
    f.close()
    return true_list


def evaluate_geoclass(act, mat, k):
    """
    入力行動についてスコアが高い上位k件の地物クラスについて再現率と適合率を計算する
    ただし，スコアが1以上のもののみ正解とする

    Args:
        act: 行動(ex."暇:潰せる")
        mat: 対象とする行動地物クラス行列
        k: 取得する地物クラス件数

    Returns:
        [再現率，適合率]
    """
    true_list = read_geoclass_true_list(act)
    all_true_count = true_list.count(1)
    #print(all_true_count)

    act_list = read_act_list()
    act_index = act_list.index(act)

    topk_index = get_topk_column_index(mat, act_index, k)
    geoclass_list = read_geoclass_list()

    true_count = 0
    """
    評価をするために取得する地物クラスの数はkで指定しているが，
    取得できるよりも大きい数を指定していた時のために
    取得地物クラス数をカウントする
    """
    geoclass_count = 0

    for i in range(k):
        score = mat[act_index, topk_index[i]]
        if score < 1.0:
            break
        if true_list[topk_index[i]] == 1:
            true_count += 1
        geoclass_count += 1

    try:
        recall = float(true_count/all_true_count)
    except ZeroDivisionError as e:
        recall = "ZeroDivisionError"
    try:
        precision = float(true_count/geoclass_count)
    except ZeroDivisionError as e:
        precision = "ZeroDivisionError"

    return [recall, precision]



if __name__ == '__main__':

    # mat = [[5, 0, 0, 0],
    #         [3, 4, 0, 0],
    #         [2, 0, 1, 0],
    #         [2, 4, 0, 3],
    #         [0, 5, 0, 4],
    #         [0, 0, 0, 5]]
    #
    #
    # # print(type(mat))
    # mat = np.matrix(mat)
    # #t = mat.T
    # #print(t)
    # # print(type(mat))
    # lsa_mat = lsa(mat, 2)
    #
    # #print(lsa_mat)
    #
    # #lsa_matt = lsa(t, 2)
    #
    # #print(lsa_matt)
    # exit()

    act_geoclass_mat = read_act_geoclass_matrix()
    act_geoclass_mat = np.matrix(act_geoclass_mat)

    k = input()
    k = int(k)
    """
    評価用
    """

    for k in range(24):
        lsa_mat = lsa(act_geoclass_mat, k*20)
        recall = evaluate_geoclass("デート:する", lsa_mat, 1000)
        print(recall)
    exit()

    lsa_mat = lsa(act_geoclass_mat, k)
    # topk_index = get_topk_column_index(mat, 2, 2)
    # print(topk_index)
    # topk_index = get_topk_column_index(act_geoclass_mat, 1434, 5)
    # print(topk_index)


    # recall = calc_geoclass_recall("時間:潰せる", lsa_mat, 1000)
    # print(recall)
    #
    #
    # exit()

    act = "星:見える"
    result = get_topk_geoclass(act, lsa_mat, 10)

    for i in range(len(result)):
        geoclass = result[i][0]
        print(geoclass)
        # score = str(result[i][1])
        # print(geoclass + ":" +score)
