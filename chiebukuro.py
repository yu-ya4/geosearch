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
        json = {"size": 1000,"query":{"query_string":{"analyzer": "ngram_analyzer","query": "\"場所\"", "fields" : ["body", "title"]}}}

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
            action
        '''
        res = []
        pattern_num = 23
        except_verbs = ['行く', 'いく', '来る', 'くる', '着く', 'つく', '訪れる', 'できる', '有る', '在る',
                        'ある', 'なる', 'いる', '住む', '言う', 'いう', '聞く', 'きく', 'する', '思う']

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

            exacted = 0
            for i in range(0, pattern_num):#パターンとのマッチング

                if exacted: #抽出されたらその時点で終了
                    break
                else:

                    results = matcher.match(sentence, pattern[i])

                    if results != None:
                        act = []
                        for result in results:
                            if len(result) == 2:
                                #動作の対象に'場所'を抽出した場合は無視
                                if result[0][0].dictform == '場所':
                                    continue
                                elif i == 8 or i == 9:
                                    act.append(result[0][0].dictform + result[1][0].dictform)#対象
                                    act.append('する') #動作
                                elif result[1][0].dictform in except_verbs:
                                    continue
                                else:
                                    act.append(result[0][0].dictform) #対象
                                    act.append(result[1][0].dictform) #動作
                            elif len(result) == 1:
                                if i == 2 or i == 3:
                                    act.append(result[0][0].dictform)#対象
                                    act.append('みる') #動作
                                elif result[0][0].pos == '名詞' and result[0][0].detailed_pos[0] == '一般':
                                    ''' [名詞]する場所，[名詞]できる場所，[名詞]ができる場所 パターンの処理'''
                                    act.append(result[0][0].dictform)#対象
                                    act.append('する') #動作
                                elif result[0][0].dictform in except_verbs:
                                    continue
                                else:
                                    act.append(None)#対象
                                    act.append(result[0][0].dictform) #動作
                            act.append(self.qid)
                            res.append(act)

                            exacted = 1
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

        print(text)
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
            question_id = question['_source']['question_id']
            title = question['_source']['title']
            body = question['_source']['body']

            if title != body:
                body = title + body

            # print(str(question_id) + ': ' + str(body))
            actions = []
            actions = self.extract_action(body)
            for action in actions:
                if action in action_dict:
                    action_dict[action].append(question_id)
                else:
                    action_dict[action] = [question_id]
        return action_dict



if __name__ == '__main__':
    chie = Chiebukuro()
    questions = chie.search_questions("場所")
    action_dict = chie.make_action_dict(questions)
    print(action_dict)
