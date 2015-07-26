import urlparse
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from twisted.internet import defer

from scrapy.core.downloader.handlers.http import HttpDownloadHandler
from scrapy.http import HtmlResponse
from scrapy import log


class SeleniumDownloadHandler(HttpDownloadHandler):

    def download_request(self, request, spider):
        if 'selenium' in request.meta:
            driver = self._get_driver()
            driver.get(request.url)
            url = driver.execute_script('return window.location.href;')
            html = driver.execute_script('return document.documentElement.innerHTML;')
            return HtmlResponse(url, encoding='utf-8', body=html.encode('utf-8'))
        else:
            return super(SeleniumDownloadHandler, self).download_request(request, spider)

    def _get_driver(self):
        binary = FirefoxBinary('/home/ubuntu/firefox/firefox-bin')
        driver = webdriver.Firefox(firefox_binary=binary)
        driver.implicitly_wait(10)
        return driver
