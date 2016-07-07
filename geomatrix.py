#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GeoMatrix():
    def __init__(self):
        self.geo_matrix  = 0


    def read_action_dict(self):
        """
        テキストファイル(action_dict.txt)から行動の辞書を読み込

        Returns:
            dict[str, list[int]]
            行動の辞書, qidを値に
        """
        action_dict = {}
        f = open('./action_dict_test.txt', 'r') #地物クラスリストを読み込む
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

            index = line[0] + '/' + line[1]


            action_dict[index] = qids
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
    action_dict = geo_matrix.read_action_dict()
    print(action_dict)
