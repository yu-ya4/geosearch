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



    def get_questions(self, query):
        '''
        質問を検索
        '''

        res = requests.get('http://192.168.20.44:9200')
        print(res.json())
