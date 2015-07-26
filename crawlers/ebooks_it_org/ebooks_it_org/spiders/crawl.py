# -*- coding: utf-8 -*-
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy import Item, Field, Request

import urlparse
import urllib2
from datetime import datetime

DOMAIN = 'ebooks-it.org'
DOMAIN_URL = 'https://%s' % DOMAIN

START_YEAR = 1966
END_YEAR = datetime.now().year


class BookItem(Item):
    url = Field()
    name = Field()
    description = Field()
    publisher = Field()
    series = Field()
    author = Field()
    isbn10 = Field()
    isbn13 = Field()
    edition = Field()
    year = Field()
    pages = Field()
    language = Field()
    size = Field()
    format = Field()
    download_url = Field()
    related = Field()
    filename = Field()


# scrapy parse --spider=ebooks-it.org -c parse -d 10 -v https://ebooks-it.org/


class BookSpider(CrawlSpider):
    name = "ebooks-it.org"
    allowed_domains = []
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(BookSpider, self).__init__(*args, **kwargs)

        if 'download' in kwargs.keys():
            self.download_files = True
        else:
            self.download_files = False

        self.allowed_domains.append(DOMAIN)

        self.start_urls.append('%s/' % (DOMAIN_URL))
        self.start_urls.append('%s/new-ebooks.htm' % (DOMAIN_URL))

        for year in range(START_YEAR, END_YEAR+1):
            self.start_urls.append('%s/search-engine.htm?bform=bpubyear&page=1&query=%s' % (DOMAIN_URL, year))

    def parse(self, response):
        loader = ItemLoader(response=response)

        xpaths = [
            '//a[contains(text(), "Next")]',
            '//a[contains(@href, "-ebook.htm")]/@href'
        ]
        for xpath in xpaths:
            for href in loader.get_xpath(xpath):
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    callback=self.parse,
                    meta=response.meta,
                    dont_filter=True
                )

        if '-ebook.htm' in response.url:
            item = BookItem()

            name_path = '//*[@itemprop="name"]/text()'  # h1
            item['name'] = loader.get_xpath(name_path, TakeFirst())

            item['url'] = response.url

            description_path = '//div[contains(text(), ".")]/text()'  # span
            item['description'] = loader.get_xpath(description_path, TakeFirst())

            publisher_path = '//*[@itemprop="publisher"]/text()'  # a
            item['publisher'] = loader.get_xpath(publisher_path, TakeFirst())

            by_path = '//*[@itemprop="author"]/text()'  # b
            item['author'] = loader.get_xpath(by_path, TakeFirst())

            isbn_path = '//*[@itemprop="isbn"]/text()'  # b
            item['isbn10'] = loader.get_xpath(isbn_path, TakeFirst())
            item['isbn13'] = loader.get_xpath(isbn_path).pop()

            year_path = '//*[@itemprop="datePublished"]/text()'  # b
            item['year'] = loader.get_xpath(year_path, TakeFirst())

            pages_path = '//*[@itemprop="numberOfPages"]/text()'  # b
            item['pages'] = loader.get_xpath(pages_path, TakeFirst())

            language_path = '//*[@itemprop="inLanguage"]/text()'  # b
            item['language'] = loader.get_xpath(language_path, TakeFirst())

            format_path = '//*[@itemprop="bookFormat"]/text()'  # b
            item['format'] = loader.get_xpath(format_path, TakeFirst())

            edition_path = '//*[@itemprop="bookEdition"]/text()'  # b
            item['edition'] = loader.get_xpath(edition_path, TakeFirst())

            series_path = '//*[contains(text(), "Series")]//following-sibling::*'
            item['series'] = ", ".join(loader.get_xpath('%s/*/text()' % series_path)).strip()

            size_path = '//*[contains(text(), "Book size")]//following-sibling::*'
            item['size'] = loader.get_xpath('%s/text()' % size_path, TakeFirst())

            related_url_path = '//h4/a/@href'
            related_name_path = '//h4/a/text()'
            item['related'] = {
                'name': loader.get_xpath(related_name_path, TakeFirst()),
                'url': urlparse.urljoin(response.url, loader.get_xpath(related_url_path, TakeFirst())),
            }

            url_path = '//div[contains(@id, "dl")]/script'
            script = loader.get_xpath(url_path, TakeFirst())

            download_url = script.split('href="')[1].split('" onclick')[0]
            item['download_url'] = urlparse.urljoin(response.url, download_url)

            pdf_url = item['download_url']
            pdf_filename = './books_/' + item['name'] + ' - ' + item['author'] + ' - ' + item['isbn13'] + '.pdf'

            item['filename'] = pdf_filename

            if self.download_files:
                # req = urllib2.Request(pdf_url)
                # req.add_header('Referer', '%s' % response.url)
                # r = urllib2.urlopen(req)
                # r = r.read()
                # with open(pdf_filename, 'wb') as out:
                #     print r
                #     out.write(r)
                from socket import socket

                host = DOMAIN
                port = 80
                path = response.url.replace(DOMAIN_URL, '')
                xmlmessage = "<port>0</port>"

                s = socket()
                s.connect((host, port))
                s.send("GET %s HTTP/1.1\r\n" % path)
                s.send("Host: %s\r\n" % host)
                s.send("Content-Type: text/html\r\n")

                for line in s.makefile():
                    print line,
                s.close()

            yield item

            for href in loader.get_xpath('//td/a/@href'):
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    callback=self.parse,
                    meta=response.meta,
                    dont_filter=True
                )

        else:
            for href in loader.get_xpath('//a[contains(@href, "-ebooks-")]/@href'):
                yield Request(
                    url=urlparse.urljoin(response.url, href),
                    callback=self.parse,
                    meta=response.meta,
                    dont_filter=True
                )