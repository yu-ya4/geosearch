#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from elasticsearch import Elasticsearch
from cabocha_matcher import CaboChaMatcher

class Chiebukuro():
    def __init__(self):
        self.es = Elasticsearch(host='192.168.20.44', port=9200, timeout=10000)
        self.index = 'chie'

    def search_questions(self, query):
        '''
        search for questions and get json response

        Args:
            query: str
                検索クエリ
        Returns:
            list[dict[str, str or int]]
            questionのlist
            json形式
        '''
        json = {"size": 120000,"query":{"query_string":{"analyzer": "ngram_analyzer","query": "\"場所\"", "fields" : ["body", "title"]}}}

        res = self.es.search(index=self.index, doc_type='questions', body=json)

        questions = res['hits']['hits']

        return questions

    def extract_action(self, que_body):
        '''
        extract actions from questions

        Args:
            que_body: str
                質問文
        Returns:
            list[list[str, str, list[str,...]]]
            action
        '''
        res = []
        pattern_num = 23
        except_verbs = ['行く', 'いく', '来る', 'くる', '着く', 'つく', '訪れる', 'できる', '有る', '在る',
                        'ある', 'なる', 'いる', '住む', '言う', 'いう', '聞く', 'きく', 'する', '思う', '出る']

        matcher = CaboChaMatcher()
        pat = []
        pattern = []
        texts = self.text_split(que_body)

        for i in range(0, pattern_num):
            file_name = "pattern/get_act/qa/act_qa_" + str(i) + ".txt"
            with open(file_name) as f:
                pat.append(f.read())
            pattern.append(matcher.parse_pat(pat[i]))

        for text in texts:
            sentence = matcher.parse(text)

            extracted = 0
            for i in range(0, pattern_num):#パターンとのマッチング

                if extracted: #抽出されたらその時点で終了
                    break
                else:

                    results = matcher.match(sentence, pattern[i]) # list[[Token, Token],...]で返したい
                    #print(results)

                    if results != None:

                        act = []
                        for result in results:

                            v_tid = -1
                            o_tid = -1
                            o_cid = -1
                            if len(result) == 2:
                                #動作の対象に'場所'を抽出した場合は無視
                                if result[0][0].dictform == '場所':
                                    continue
                                elif i == 8 or i == 9:
                                    act.append(result[0][0].dictform + result[1][0].dictform)#対象
                                    act.append('する') #動作
                                    o_tid = result[0][0].tid
                                elif result[1][0].dictform in except_verbs:
                                    continue
                                else:
                                    act.append(result[0][0].dictform) #対象
                                    act.append(result[1][0].dictform) #動作
                                    o_tid = result[0][0].tid
                            elif len(result) == 1:
                                if i == 2 or i == 3:
                                    act.append(result[0][0].dictform)#対象
                                    act.append('みる') #動作
                                    o_tid = result[0][0].tid
                                elif result[0][0].pos == '名詞' and result[0][0].detailed_pos[0] == '一般':
                                    ''' [名詞]する場所，[名詞]できる場所，[名詞]ができる場所 パターンの処理'''
                                    act.append(result[0][0].dictform)#対象
                                    act.append('する') #動作
                                    v_tid = result[0][0].tid
                                elif result[0][0].dictform in except_verbs:
                                    continue
                                else:
                                    act.append(None)#対象
                                    act.append(result[0][0].dictform) #動作
                                    v_tid = result[0][0].tid

                            adverbs = []
                            paths = sentence.breakup()

                            if v_tid != -1:
                                v_cid = sentence.get_cnk_has_tok(v_tid)
                                for cnk in sentence.cnks:
                                    if cnk.link == v_cid:
                                        adverbs.append(cnk)

                            if o_tid != -1: #0,1,8,9
                                o_cid = sentence.get_cnk_has_tok(o_tid)
                                v_cid = sentence.get_cnk(o_cid).link

                                for cnk in sentence.cnks:
                                    if cnk.link == v_cid and cnk.cid != o_cid:
                                        adverbs.append(cnk)

                            str_adverbs = []
                            for adverb in adverbs:
                                str_adverb = ''
                                for tok in adverb.toks:
                                    str_adverb += tok.surface
                                str_adverbs.append(str_adverb)

                            str_adverbs = sorted(str_adverbs) #副詞の順をソート
                            act.append(str_adverbs)

                            res.append(act)

                            extracted = 1
                            '''
                            print( self.text)
                            print('\n')
                            for ans in self.ans:
                                print(ans.text)
                                print('\n')
                            print(act)
                            print('---------------------------------------\n')
                            '''

                            break


        return res

    def text_split(self, text):
        '''
        一部の表現をマッチングしやすくする
        記号で区切り， "場所"という単語を含む文を判定
        Args:
            text: str
        Returns:
            list[str]
        '''
        res = []
        syms = ['.', '。', ',', '，', '、', '?', '？', '!', '！']
        text = text.replace("おすすめの", "")
        text = text.replace("オススメの", "")
        text = text.replace("お勧めの", "")
        text = text.replace("お薦めの", "")

        #text = text.replace("いい場所", "場所")
        #text = text.replace("良い場所", "場所")
        #text = text.replace("適した場所", "場所")
        text = text.replace("見える", "みれる")
        text = text.replace("観れる", "みれる")
        text = text.replace("見れる", "みれる")
        text = text.replace("出来る", "できる")

        for sym in syms:
            text = text.replace(sym, " ")

        texts = text.split()

        for text in texts:
            if '場所' in text:
                res.append(text)

        return res




    def get_answers(self, question_ids):
        '''
        Args:
            question_ids: list[int]
        Returns:
            list[dict[str, str or int]]
            answerのlist
            json形式

            ないやつ指定した際の処理もおk
        '''
        ids = ''
        for question_id in question_ids:
            ids += str(question_id)
            ids += ' '
        json = {"query":{"query_string":{"query": "","default_field" : "question_id"}}}
        json['query']['query_string']['query'] = ids

        res = self.es.search(index=self.index, doc_type='answers', body=json)

        answers = res['hits']['hits']

        return answers



    def make_action_dict(self, questions):
        '''
        Args:
            questions: list[dict[str, str or int]]
        Returns:
            dict[str, list[int]]

        '''
        action_dict = {}
        for question in questions:
            body = question
            question_id = question['_source']['question_id']
            title = question['_source']['title']
            body = question['_source']['body']

            if title != body:
                body = title + body

            # print(str(question_id) + ': ' + str(body))
            actions = []
            actions = self.extract_action(body)

            for action in actions:
                adverbs = ''
                for adverb in action[2]:
                    adverbs += ' '
                    adverbs += adverb
                if action[0] != None:
                    index = action[0] + ' ' + action[1] + '/' + adverbs
                else:
                    index = action[1] + '/' + adverbs
                if index in action_dict:
                    action_dict[index].append(question_id)
                else:
                    action_dict[index] = [question_id]
        return action_dict

    def write_action_dict(self, action_dict):
        fw = open('action_dict.txt', 'w')
        for action, q_ids in action_dict.items():
            question_ids = ''
            for q_id in q_ids:
                question_ids += str(q_id)
                question_ids += ' '
            fw.write(action + '/' +  question_ids + '\n')
        fw.close()


if __name__ == '__main__':

    # test = Chiebukuro()
    # action_dict = test.make_action_dict(['京都で寝る場所','京都で花見することができる場所','京都で遊ぶことができる場所','こどもが京都で着物を体験できる場所','BBQをできる場所','京都で着物の体験ができる場所','綺麗に星を見られる場所','星の綺麗に見える場所','京都でこどもが着物を体験することができる場所','みんなでフグを食べることができる場所','上手にみんなで海中水泳ができる場所', 'みんなで遊ぶ場所', 'ある場所'])
    # print(action_dict)

    chie = Chiebukuro()

    dic = {'話せる/ 静かに': [1430285049, 5463456, 535554], '置く/ （サーバーが': [109803840], '英語 教える/ 親切に': [11129676326], 'コスメ 販売/': [1049368820]}
    chie.write_action_dict(dic)

    exit()
    questions = chie.search_questions("場所")
    action_dict = chie.make_action_dict(questions)
    print(action_dict)
