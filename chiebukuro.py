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
        u = 'http://192.168.20.44:9200/chie/answers/_search?pretty -d ' + json


        # res = requests.get('http://192.168.20.44:9200')
        res = requests.get(u)

        print(res.json()['hits']['hits'][0])

if __name__ == '__main__':
    chie = Chiebukuro()
    chie.search_questions("場所")
