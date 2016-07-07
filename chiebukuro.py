#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

class Chiebukuro():
    def __init__(self):
        self.q_url = '192.168.20.44:9200/chie/questions/_search?pretty'
        self.a_url = '192.168.20.44:9200/chie/answers/_search?pretty'
        # self.q_url = 'loclhost:9200/chie/questions/_search?pretty'
        # self.a_url = 'localhost:9200/chie/answers/_search?pretty'



    def search_questions(self, query):
        '''
        search for questions and get json response

        Args:
            query: str
                検索クエリ
        Returns:

        '''
        json = '{"size": 10,"query":{"query_string":{"analyzer": "ngram_analyzer","query": "\"' + query + '\"","fields" : ["body", "title"]}}}'
        u = 'http://192.168.20.44:9200/chie/questions/_search?pretty -d ' + json

        # res = requests.get('http://192.168.20.44:9200')
        res = requests.get(u)
        questions = res.json()['hits']['hits']

        return questions

        # print(res.json()['hits']['hits'][0]['_source']['body'])

    def extract_action(self, question):
        '''
        extract actions from questions

        Args:
            question: str
                質問文
        Returns:
            action
        '''




if __name__ == '__main__':
    chie = Chiebukuro()
    questions = chie.search_questions("場所")

    for question in questions:
        question_id = question['_source']['question_id']
        title = question['_source']['title']
        body = question['_source']['body']

        if title != body:
            body = title + body

        print(str(question_id) + ': ' + str(body))

        action = chie.extract_action(body)
