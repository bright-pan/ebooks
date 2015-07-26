# -*- coding: utf-8 -*-
import scrapy

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy import Item, Field, Request

import urllib2
import urlparse
import os.path


class BookItem(Item):
    url = Field()
    name = Field()
    description = Field()
    publisher = Field()
    author = Field()
    isbn13 = Field()
    year = Field()
    pages = Field()
    language = Field()
    size = Field()
    format = Field()
    download_url = Field()
    buy = Field()
    related = Field()
    filename = Field()
    image_url = Field()


DOMAIN = 'it-ebooks.info'
START_BOOK_ID = 1
END_BOOK_ID = 9999
CURRENT_BOOK_ID = 0
DOMAIN_URL = 'http://%s' % DOMAIN
BOOK_URL = '%s/book' % DOMAIN_URL


# scrapy parse --spider=it-ebooks.info -c parse -d 1 -v http://it-ebooks.info/book/345/

# scrapy crawl it-ebooks.info -o it-ebooks.info.csv -t csv -a download=1

class IncrementalSpider(scrapy.Spider):
    name = "it-ebooks.info"
    allowed_domains = []
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(IncrementalSpider, self).__init__(*args, **kwargs)
        self.allowed_domains.append(DOMAIN)

        for book_id in range(START_BOOK_ID, END_BOOK_ID):
            self.start_urls.append('%s/%s/' % (BOOK_URL, book_id))

        if 'download' in kwargs.keys():
            self.download_files = True
        else:
            self.download_files = False

    def parse(self, response):
        if '%s/404' % DOMAIN_URL not in response.url:
            item = BookItem()
            loader = ItemLoader(response=response)

            name_path = '//h1/text()|//h3/text()'  # h1
            item['name'] = " ".join(loader.get_xpath(name_path))

            item['url'] = response.url

            description_path = '//*[@itemprop="description"]'  # span
            item['description'] = "".join(loader.get_xpath('%s/text()|%s/*/text()' % (description_path, description_path)))

            publisher_path = '//*[@itemprop="publisher"]/text()'  # a
            item['publisher'] = loader.get_xpath(publisher_path, TakeFirst())

            by_path = '//*[@itemprop="author"]/text()'  # b
            item['author'] = loader.get_xpath(by_path, TakeFirst())

            isbn_path = '//*[@itemprop="isbn"]/text()'  # b
            item['isbn13'] = loader.get_xpath(isbn_path, TakeFirst())

            year_path = '//*[@itemprop="datePublished"]/text()'  # b
            item['year'] = loader.get_xpath(year_path, TakeFirst())

            pages_path = '//*[@itemprop="numberOfPages"]/text()'  # b
            item['pages'] = loader.get_xpath(pages_path, TakeFirst())

            language_path = '//*[@itemprop="inLanguage"]/text()'  # b
            item['language'] = loader.get_xpath(language_path, TakeFirst())

            format_path = '//*[@itemprop="bookFormat"]/text()'  # b
            item['format'] = loader.get_xpath(format_path, TakeFirst())

            url_path = '//a[contains(@href, "http://file")]/@href'
            item['download_url'] = loader.get_xpath(url_path, TakeFirst())

            buy_path = '//a[contains(@href, "http://isbn")]/@href'
            item['buy'] = loader.get_xpath(buy_path, TakeFirst())

            size_path = '//*[contains(text(), "size")]//following-sibling::*'
            item['size'] = loader.get_xpath('%s/*/text()' % size_path, TakeFirst())

            image_path = '//img[contains(@itemprop, "image")]'
            item['image_url'] = loader.get_xpath('%s/@src' % image_path, TakeFirst())

            related_path = '//td[contains(@width, "166")]/a'
            item['related'] = {
                'name': loader.get_xpath('%s/@title' % related_path, TakeFirst()),
                'url': urlparse.urljoin(response.url, loader.get_xpath('%s/@href' % related_path, TakeFirst())),
            }
            pdf_url = item['download_url']
            pdf_filename = './books/' + \
                item['name'].replace(',', '_').replace('/', '\/').replace(' ', '_') + \
                '-' + item['author'].replace(',', '').replace(' ', '_') + \
                '-' + item['isbn13'].replace('-', '') + \
                '.pdf'.replace('__', '_')

            item['filename'] = pdf_filename

            if self.download_files:
                self.download_file(pdf_url, pdf_filename, response.url)
            print response.url, item['image_url']
            image_url = urlparse.urljoin(response.url, item['image_url'])
            self.download_file(image_url, './%s' % item['image_url'].strip('/'), response.url)

            yield item

    def download_file(self, url, filename, referer=''):
        basedir = filename.replace(os.path.basename(filename), '')
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        if not os.path.exists(filename):
            req = urllib2.Request(url)
            req.add_header('Referer', '%s' % referer)
            r = urllib2.urlopen(req)

            with open(filename, 'wb') as out:
                out.write(r.read())
