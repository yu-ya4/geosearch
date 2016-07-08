#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from cabocha_matcher import CaboChaMatcher
from chiebukuro import Chiebukuro
import numpy as np

class GeoMatrix():
    def __init__(self):
        self.geo_matrix = self.read_divided_matrix()
        self.geos = self.read_geoclass_list()
        self.acts = self.read_natural_actions()
        self.chie = Chiebukuro()

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
    print(len(geomat.geo_matrix))

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
