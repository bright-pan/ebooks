# -*- coding: utf-8 -*-
import scrapy


class EboookSpider(scrapy.Spider):
    name = "eboook"
    allowed_domains = ["eboook.net"]
    start_urls = (
        'http://www.eboook.net/',
    )

    def parse(self, response):
        pass
