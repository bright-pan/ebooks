# -*- coding: utf-8 -*-
import scrapy

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy import Item, Field, Request

import urllib2
import urlparse
import os.path


class PdfItem(Item):
    url = Field()
    title = Field()
    description = Field()

DOMAIN = 'google.com'
DOMAIN_URL = 'https://www.%s' % DOMAIN
SEARCH_PATH = "search"
QUERY_TYPE = 'type%A3pdf'
SEARCH_TERM = 'cooking'
DOWNLOAD_DIR = 'documents'

ENGINE_URL = '%s/%s?q=%s+%s' % \
    (DOMAIN_URL, SEARCH_PATH, QUERY_TYPE, SEARCH_TERM)


class PdfSpider(scrapy.Spider):
    name = "pdf"
    allowed_domains = [DOMAIN]
    start_urls = [ENGINE_URL]
    use_selenium = True

    def __init__(self, *args, **kwargs):
        super(PdfSpider, self).__init__(*args, **kwargs)
        if 'download' in kwargs.keys():
            self.download_files = True
        else:
            self.download_files = False

    def parse(self, response):

        item = PdfItem()
        loader = ItemLoader(response=response)

        pdf_path = '//*[contains(text(), "[PDF]")]'
        pdf_url_path = '%s//following-sibling::*' % pdf_path

        item['url'] = loader.get_xpath('%s' % pdf_url_path)
        item['title'] = loader.get_xpath('%s/text()' % pdf_url_path, TakeFirst())

        summary_path = '%s//parent::*//parent::*/*[@class="s"]/*' % pdf_url_path
        description_path = '%s/*[@class="st"]/*' % summary_path

        item['description'] = loader.get_xpath('%s/text()|%s/*/text()' % (description_path, description_path))

        similar_path = '%s/*[contains(@class, "f")]//a[contains(@href, "q=related:")]' % summary_path

        # similar_url = loader.get_xpath('%s/@href' % similar_path, TakeFirst())
        # yield Request(
        #     url=urlparse.urljoin(response.url, similar_url),
        #     callback=self.parse,
        #     meta=response.meta,
        #     dont_filter=True
        # )
        #
        # next_path = '//*[@class="pn"]'
        # next_url = loader.get_xpath('%s/@href' % next_path, TakeFirst())
        # yield Request(
        #     url=urlparse.urljoin(response.url, next_url),
        #     callback=self.parse,
        #     meta=response.meta,
        #     dont_filter=True
        # )

        pdf_url = item['url']
        print item
        if pdf_url:
            pdf_filename = os.path.basename(pdf_url)
            pdf_filepath = '%s/%s/%s' % (DOWNLOAD_DIR, SEARCH_TERM, pdf_filename)

            if self.download_files:
                self.download_file(pdf_url, pdf_filepath, response.url)

            yield item

    def download_file(self, url, filename, referer=''):
        basedir = filename.replace(os.path.basename(filename), '')
        if basedir is not '' and not os.path.exists(basedir):
            os.makedirs(basedir)

        if not os.path.exists(filename):
            req = urllib2.Request(url)
            req.add_header('Referer', '%s' % referer)
            r = urllib2.urlopen(req)

            with open(filename, 'wb') as out:
                out.write(r.read())
