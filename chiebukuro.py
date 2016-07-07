#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from elasticsearch import Elasticsearch

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
        json = {"size": 10,"query":{"query_string":{"analyzer": "ngram_analyzer","query": "\"場所\"", "fields" : ["body", "title"]}}}

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

        return que_body

    def get_answers(self, question_ids):
        '''
        Args:
            question_ids: list[int]
        Returns:
            list[dict[str, str or int]]
            answerのlist
            json形式
        '''
        ids = ''
        for question_id in question_ids:
            ids += str(question_id)
            #ids += ' '
        json = '{"query":{"query_string":{"query": "148926454 OR 148926564","default_field" : "question_id"}}}'

        #json = '{query":{"query_string":{query": "' + ids + '","default_field" : "question_id"}}}'

        print(json)
        u = 'http://192.168.20.44:9200/chie/answers/_search?pretty -d ' + json

        # print(u)
        # exit()

        res = requests.get(u)
        answers = res.json()

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
            action = self.extract_action(body)
            if action in action_dict:
                action_dict[action].append(question_id)
            else:
                action_dict[action] = [question_id]

        return action_dict



if __name__ == '__main__':
    chie = Chiebukuro()
    # print(chie.get_answers([18]))
    # exit()
    questions = chie.search_questions("場所")
    action_dict = chie.make_action_dict(questions)
    print(action_dict)
