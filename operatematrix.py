#!/usr/local/bin/python3
# -*- coding: utf-8

import copy
import math
import numpy as np
from scipy import linalg
from collaborativefilterng import CollaborativeFiltering

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
    入力行動についてスコアが高い上位k件の地物クラスについて再現率と適合率，F値を計算する
    ただし，スコアが1以上のもののみ正解とする

    Args:
        act: 行動(ex."暇:潰せる")
        mat: 対象とする行動地物クラス行列
        k: 取得する地物クラス件数

    Returns:
        [再現率，適合率，F値]
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

    try:
        f_measure = 2 * recall * precision/(recall + precision)
    except ZeroDivisionError as e:
        f_measure = "ZeroDivisionError"

    return [recall, precision]



if __name__ == '__main__':


    # R = np.array([
    #         [5, 3, 0, 1],
    #         [4, 0, 0, 1],
    #         [1, 1, 0, 5],
    #         [1, 0, 0, 4],
    #         [0, 1, 5, 4],
    #         ]
    #     )
    # R = np.matrix(R)
    # cf = CollaborativeFiltering(R)
    #
    # nP, nQ = cf.matrix_factorization(2)
    # nR = np.dot(nP.T, nQ)
    # print(nR)

    # lsa_mat = cf.lsa(2)
    #
    # print(lsa_mat)




    act_geoclass_mat = read_act_geoclass_matrix()
    act_geoclass_mat = np.matrix(act_geoclass_mat)
    cf = CollaborativeFiltering(act_geoclass_mat)

    #lsa_mat = cf.lsa(30)
    nP, nQ = cf.matrix_factorization(3)
    mf_mat = np.dot(nP.T, nQ)

    f1 = open('mf-matrix.txt', 'w')
    nR = np.array(mf_mat)
    for i in range(len(nR)):
        line = ""
        for j in range(len(nR[i])):
            value = nR[i][j]
            if j == (len(nR[i]) - 1):
                line += str(value) + "\n"
                break
            line += str(value) + " "
        #print(line)
        # for qid in qids:
        #     line = line + ' ' + qid
        # line += '\n'
        f1.write(line)
    f1.close()
    exit()

    #recall = evaluate_geoclass("デート:する", lsa_mat, 1000)
    #print(recall)
    # recall = evaluate_geoclass("デート:する", mf_mat, 1000)
    # print(recall)



    """
    評価用
    k = input()
    k = int(k)

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

    """
