#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from cabocha_matcher import CaboChaMatcher
from chiebukuro import Chiebukuro

class GeoMatrix():
    def __init__(self):
        self.geo_matrix  = 0
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

if __name__ == '__main__':
    geo_matrix = GeoMatrix()
    # geotypes = geo_matrix.read_geoclass_list()
    # print(geotypes)
    geo_matrix.make_natural_matrix()
