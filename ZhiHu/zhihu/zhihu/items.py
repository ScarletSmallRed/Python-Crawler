# -*- coding= utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in=
# https=//doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like=
    # name = scrapy.Field()
    id = Field()
    url_token = Field()
    name = Field()
    use_default_avatar = Field()
    avatar_url = Field()
    avatar_url_template = Field()
    is_org = Field()
    type = Field()
    url = Field()
    user_type = Field()
    headline = Field()
    gender = Field()
    is_advertiser = Field()
