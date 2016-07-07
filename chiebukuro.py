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
            list[dict[str, str or int]]
            questionのlist
            json形式
        '''
        json = '{"size": 10,"query":{"query_string":{"analyzer": "ngram_analyzer","query": "\"' + query + '\"","fields" : ["body", "title"]}}}'
        u = 'http://192.168.20.44:9200/chie/questions/_search?pretty -d ' + json

        # res = requests.get('http://192.168.20.44:9200')
        res = requests.get(u)
        questions = res.json()['hits']['hits']

        return questions

        # print(res.json()['hits']['hits'][0]['_source']['body'])

    def extract_action(self, que_body):
        '''
        extract actions from questions

        Args:
            que_body: str
                質問文
        Returns:
            action
        '''

        return que_body[0:2]

    def get_answers(self, question_ids):
        '''
        Args:
            question_ids: list[int]
        Returns:
            list[str]
            answerのbodyのリスト
        '''

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
    questions = chie.search_questions("場所")
    action_dict = chie.make_action_dict(questions)
    print(action_dict)
