#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from cabocha_matcher import CaboChaMatcher
from chiebukuro import Chiebukuro
from scipy import linalg
import numpy as np
import math
import copy

class GeoMatrix():
    def __init__(self):
        self.geo_matrix = self.read_divided_matrix()
        self.geos = self.read_geoclass_list()
        self.acts = self.read_divided_actions()
        self.chie = Chiebukuro()
        self.rank = 0

    def get_topk_geotype_index(self, mat, row, k):
        """
        指定した行の上位k件のインデックス番号をリストで返す

        Args:
            mat: 行列
            row: 行番号
            k: 取得するインデックス件数

        Returns:
            指定した行の上位k件のインデックス番号からなるリスト
        """
        mat = np.matrix(self.geo_matrix)
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

    def ppmi(self, matrix):

        #行数，列数を取得
        row_num = matrix.shape[0]
        column_num = matrix.shape[1]

        result_matrix = np.zeros((row_num, column_num), dtype='float')
        # print(result_matrix)

        for i in range(row_num):
            for j in range(column_num):
                log_ij = np.log(matrix[i, j])
                log_ij_sum = np.log(matrix.mean() * row_num * column_num)
                log_i_sum = np.log(matrix.sum(axis=1)[i,0])
                log_j_sum = np.log(matrix.sum(axis=0)[0,j])

                temp = log_ij + log_ij_sum - log_i_sum - log_j_sum
                res = max(0, temp)

                result_matrix[i,j] = res

        self.geo_matrix = result_matrix

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
        mat = np.matrix(self.geo_matrix)
        U, s, V = np.linalg.svd(mat, full_matrices=0)
        #print(s)

        return [U, s, V]

    def lsa(self, k):
        """
        行列にLSAを適用する

        Returns:
            numpy.matrix
            LSAを適用した結果
        """
        mat = np.matrix(self.geo_matrix)
        rank = np.linalg.matrix_rank(mat)
        print(rank)
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

        self.geo_matrix = lsa_mat



    def make_divide_action_dic(self):
        '''
        "natural_actions.txt"をもとに
        1つのactionを[object(0 or 1), verb(1), modify(0or 1)]と
        した行動の辞書を作成する"divided_action_dict.txt"
        '''
        # self.acts = self.read_natural_actions()
        divided_actions = {} # {divided_action: [i]}
        for i in range(len(self.acts)):
            natural_action = self.acts[i]
            d_act = [natural_action[0], natural_action[1]]
            index =  d_act[0] + ' ' + d_act[1]
            if index in divided_actions:
                divided_actions[index].append(i)
            else:
                divided_actions[index] = [i]

            for k in range(len(natural_action[2])):
                d_act = [natural_action[0], natural_action[1], natural_action[2][k]]
                index = d_act[0] + ' ' + d_act[1] + ' ' + d_act[2]
                if index in divided_actions:
                    divided_actions[index].append(i)
                else:
                    divided_actions[index] = [i]

        fw = open('./divided_action_dict.txt', 'w')
        for action, i_list in divided_actions.items():
            i_s = ''
            for i in i_list:
                i_s += str(i)
                i_s += ' '
            fw.write(action + '/' + i_s + '\n')
        fw.close()

    def make_divided_matrix(self):
        '''
        "divided_action_dict.txt"と"natural_matrix.txt"をもとに，
        1つのactionを[object(0 or 1), verb(1), modify(0or 1)]とした行列を作成し，
        "divided_matrix.txt"に書き込む．
        また同時に，modifyを分割した行動のリストも作成する"divided_actions.txt"
        '''
        # self.geo_matrix = self.read_natural_matrix


        f = open('./divided_action_dict.txt', 'r')
        fa = open('./divided_actions.txt', 'w')
        fd = open('./divided_matrix.txt', 'w')
        for line in f:
            divided_action = line.split('/')[0]
            i_s = line.split('/')[1]
            i_list = i_s.split(' ')
            i_list.pop()

            fa.write(divided_action + '\n')

            action_vec = np.array(len(self.geos)*[0])
            for i in i_list:
                action_vec = action_vec + np.array(self.geo_matrix[int(i)])

            action_vec = action_vec.tolist()
            it = 1
            scores = ''
            for score in action_vec:
                scores += str(score)
                if it < len(action_vec):
                    scores += ' '
                    it += 1
                else:
                    scores += '\n'
            fd.write(scores)
        fd.close()
        fa.close()
        f.close()



    def make_natural_matrix(self):
        """
        テキストファイル(action_dict.txt)から行動の辞書を読み込み，
        ナチュラルな(modifyを分割したりしていない)geographic action matrixを作成し，
        (natural_matrix.txt)に書き込む
        また同時に，ナチュラルな行動のリストも作成する(natural_actions.txt)

        Returns:
            dict[str, list[int]]
            行動の辞書, qidを値に
        """
        action_dict = {}
        types = self.read_geoclass_list()
        f = open('./action_dict.txt', 'r') #地物クラスリストを読み込む
        fa = open('./natural_actions.txt', 'w')
        fn = open('./natural_matrix.txt', 'w')
        for line in f:
            line = line.replace('\n', '')
            line = line.split('/')
            # o_v = line[0].split(' ')
            # # if len(o_v) == 2:
            # #     o = o_v[0]
            # #     v = o_v[1]
            # # else:
            # #     o = ''
            # #     v = o_v[0]
            # ms = line[1].split(' ')
            # ms.pop(0)
            qids = line[2].split(' ')
            qids.pop()

            action = line[0] + '/' + line[1] + '\n'
            fa.write(action)
            answers = self.chie.get_answers(qids)
            action_vec = self.chie.extract_geo_type(answers, types)

            i = 1
            scores = ''
            for score in action_vec:
                scores += str(score)
                if i < len(action_vec):
                    scores += ' '
                    i += 1
                else:
                    scores += '\n'
            fn.write(scores)
        fn.close()
        fa.close()
        f.close()

        return action_dict
    def read_geoclass_list(self):
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

    def read_natural_actions(self):
        '''
        テキストファイル("natural_actions.txt")からactionのリストを読み込む
        1つのアクションは[object, verb, [modifiers]]の形式

        Return:
            list[[str, str, list[str]]]
        '''

        act_list = []

        f = open('./natural_actions.txt', 'r')
        for line in f:
            line = line.replace('\n', '')
            line = line.split('/')
            o_v = line[0].split(' ')
            if len(o_v) == 2:
                o = o_v[0]
                v = o_v[1]
            else:
                o = ''
                v = o_v[0]
            ms = line[1].split(' ')
            ms.pop(0)
            act_list.append([o, v, ms])

        return act_list

    def read_divided_actions(self):
        '''
        テキストファイル("divided_actions.txt")からactionのリストを読み込む
        1つのアクションは[object, verb, modify]の形式

        Return:
            list[str, str, str]
        '''
        act_list = []

        f = open('./divided_actions.txt', 'r')
        for line in f:
            line = line.replace('\n', '')
            action = line.split(' ')
            if len(action) == 2:
                action.append('')
            act_list.append(action)

        return act_list

    def read_natural_matrix(self):
        """
        テキストファイル("natural_matrix.txt")から行列を読み込み

        Returns:
            List<List<float>>
            行動地物クラス行列
        """
        natural_mat = [] #行動-地物クラス行列
        f = open('./natural_matrix.txt', 'r')
        for line in f:
            line = line.replace('\n', '')
            line = line.split(' ')
            for i in range(len(line)):
                #行末の空白対策
                if line[i] == "":
                    del line[i]
                    continue
                line[i] = float(line[i])

            natural_mat.append(line)
            if line == '':
                break
        f.close()

        return natural_mat

    def read_divided_matrix(self):
        """
        テキストファイル("divided_matrix.txt")から行列を読み込み

        Returns:
            List<List<float>>
            行動地物クラス行列
        """

        divided_mat = [] #行動-地物クラス行列
        f = open('./divided_matrix.txt', 'r')
        for line in f:
            line = line.replace('\n', '')
            line = line.split(' ')
            for i in range(len(line)):
                #行末の空白対策
                if line[i] == "":
                    del line[i]
                    continue
                line[i] = float(line[i])

            divided_mat.append(line)
            if line == '':
                break
        f.close()

        return divided_mat


if __name__ == '__main__':
    geomat = GeoMatrix()
    # i = 0
    # count = 0
    # actions = {} #acts: freq
    # for row in geomat.geo_matrix:
    #     if sum(row) != 0:
    #         action = geomat.acts[i]
    #         index = action[0] + ' ' + action[1] + ' '+ action[2]+ ':' + str(i)
    #         actions[index] = sum(row)
    #         count += 1
    #     i += 1
    #
    # f = open('./act_fre.txt', 'w')
    # for index, v in sorted(actions.items(), key=lambda x:x[1]):
    #     rank = index + ': ' + str(v) + '\n'
    #     f.write(rank)
    # f.close()
    # exit()
    #
    # geomat.lsa(100)
    # print(geomat.geo_matrix)

    # geotypes = geo_matrix.read_geoclass_list()
    # print(geotypes)

    # action_dict = {}
    # f = open('./action_dict.txt', 'r') #地物クラスリストを読み込む
    # i = 1
    # for line in f:
    #     line = line.replace('\n', '')
    #     line = line.split('/')
    #
    #     if len(line) > 3:
    #         print(i)
    #     i += 1
    #
    # f.close()
