# -*- coding: utf-8 -*-
from scrapy.item import Item, Field


# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


class WebsiteItem(Item):
    url = Field()
    html = Field()
