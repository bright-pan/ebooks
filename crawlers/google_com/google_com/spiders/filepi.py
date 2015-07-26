# -*- coding: utf-8 -*-
import scrapy


class FilepiSpider(scrapy.Spider):
    name = "filepi"
    allowed_domains = ["google.com"]
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(FilepiSpider, self).__init__(*args, **kwargs)
        self.search_url = 'https://www.google.com/?q=filetype%3Apdf+site%3Afilepi.com#q=pdf+site:filepi.com&start=0'
    def parse(self, response):

        pdf_path = '//*[contains(text(), "[PDF]")]'

