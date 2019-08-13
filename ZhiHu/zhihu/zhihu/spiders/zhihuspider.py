# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from zhihu.items import ZhihuItem


class ZhihuspiderSpider(scrapy.Spider):
    name = 'zhihuspider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    follower_url = "https://www.zhihu.com/api/v4/members/{user}/followers?offset={offset}&limit={limit}"
    start_user = "beansprout"
    limit = 20
    offset = 0

    def start_requests(self):
        yield Request(self.follower_url.format(user=self.start_user, offset=self.offset, limit=self.limit), callback=self.parse)

    def parse(self, response):
        results = json.loads(response.text)
        followers = results["data"]
        item = ZhihuItem()

        for follower in followers:
            for field in item.fields:
                if field in follower.keys():
                    item[field] = follower.get(field)
            yield item
        
        if 'paging' in results.keys() and results.get('paging').get('is_end') is False:
            self.offset += 20
            yield Request(self.follower_url.format(user=self.start_user, offset=self.offset, limit=self.limit), callback=self.parse)


