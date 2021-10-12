import requests
from bs4 import BeautifulSoup
import csv
import json


class ParserMgr:
    def __init__(self, url=None, encoding="euc-kr"):
        self.url = url
        self.encoding = encoding
        self.soup_html = ""

    def get_response(self):
        # Get response using rest api
        response = requests.get(self.url)
        # Change encoding to utf-8 for Korean language
        response.encoding = self.encoding
        return response

    def get_html(self):
        res = self.get_response()
        if res.status_code != 200:
            print("[Fail] request status_code : {0}", res.status_code)
            return -1
        html = res.text
        self.soup_html = BeautifulSoup(html, "html.parser")
        return 0

    def get_target_data(self, target_url, encoding="euc-kr"):
        self.url = target_url
        self.encoding = encoding
        ret = self.get_html()
        if ret < 0:
            print("Fail to get response (err code : {0})", ret)
            return -1
        return 0
