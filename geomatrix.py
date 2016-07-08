#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from cabocha_matcher import CaboChaMatcher
from chiebukuro import Chiebukuro

class GeoMatrix():
    def __init__(self):
        self.geo_matrix = 0
        self.geos = self.read_geoclass_list()
        self.acts = self.read_natural_actions()
        self.chie = Chiebukuro()


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

if __name__ == '__main__':
    geo_matrix = GeoMatrix()
    geo_matrix.read_natural_matrix()
    print(geo_matrix.acts)
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
