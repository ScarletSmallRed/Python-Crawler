#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2019-07-17 22:07:00
# Project: HKSTP

from pyspider.libs.base_handler import *
import re
import string
import pymongo

MONGO_URI = 'localhost'
MONGO_DB = 'HKSTP'

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v226'
    }
    
    def __init__(self):
        self.base_url = 'https://www.hkstp.org/zh-cn/reach-us/company-directory/?i=&t=All&c=-1&s=-1&s=-1&k=&page='
        self.page_num = 1
        self.total_num = 46

    @every(minutes=24 * 60)
    def on_start(self):
        while self.page_num <= self.total_num:
            url = self.base_url + str(self.page_num)
            self.crawl(url, callback=self.index_page)
            self.page_num += 1
        
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('#companyList > ul div div > a').items():
            self.crawl(each.attr.href, callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        info_list = response.doc('.main-body-content')
        info_list = str(info_list)
        name = response.doc('.content-sub-title').text()
        phone_pattern = re.compile('<span>联系电话</span>.*?<p>(.*?)</p>', re.S)
        phone = 'None'
        if re.findall(phone_pattern, info_list):
            phone = re.findall(phone_pattern, info_list)[0]
        email_pattern = re.compile('<span>电子邮件</span>.*?<p><a.*?>(.*?)</a>', re.S)
        email = 'None'
        if re.findall(email_pattern, info_list):
            email = re.findall(email_pattern, info_list)[0]
        address_pattern = re.compile('<span>地址</span>.*?<p>(.*?)</p>', re.S)
        address = 'None'
        if re.findall(address_pattern, info_list):
            address = re.findall(address_pattern, info_list)[0].strip()
        introduction_pattern = re.compile('<span>简介</span>.*?<p>(.*?)</p>', re.S)
        introduction = 'None'
        if re.findall(introduction_pattern, info_list):
            introduction = re.findall(introduction_pattern, info_list)[0].strip()
        
        
        return {
            "name": name,
            "url": response.url,
            "phone": phone,
            "email": email,
            "address": address,
            "introduction": introduction
        }
    
    def on_result(self, result):
        #print("result: ", result)
        if result:
            super(Handler, self).on_result(result)
            self.save_to_mongo(result)


    def save_to_mongo(self, data):
        if db['details1'].update({'name': data['name']}, {'$set': data}, True):
            print('Saved to Mongo', data['name'])
        else:
            print('Saved to Mongo Failed', data['name'])
