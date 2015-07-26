from scrapy.http import HtmlResponse
from scrapy.conf import settings

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.phantomjs.service import Service as PhantomJSService

# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(800, 600))
# display.start()

selenium_grid_url = "http://172.17.0.2:4444/wd/hub"

reuseable_driver = None

phantomjs_path = '/usr/bin/phantomjs'

import os
os.environ['PATH'] = '.:' + os.environ.get('PATH')

class WebDriverProxy():
    def chrome_driver(self):
        pass

    def firefox_driver(self):
        pass

    def phantomjs_driver(self):
        # monkey patch Service temporarily to include desired args
        class NewService(PhantomJSService):
            def __init__(self, *args, **kwargs):
                service_args = kwargs.get('service_args', list())
                proxy = '--proxy=127.0.0.1:9050'
                proxytype = '--proxy-type=socks5'
                if service_args is not None:
                    service_args += [
                        proxy,
                        proxytype,
                    ]
                else:
                    service_args = [
                        proxy,
                        proxytype,
                    ]
                super(NewService, self).__init__(*args, **kwargs)
        webdriver.phantomjs.webdriver.Service = NewService
        # init the webdriver
        driver = webdriver.PhantomJS(phantomjs_path)
        # undo monkey patch
        webdriver.phantomjs.webdriver.Service = PhantomJSService
        return driver


def get_driver(driver_type=None, implicitly_wait=10):
    if reuseable_driver is not None:
        driver = reuseable_driver
    else:
        if driver_type:
            driver = None

            # capabilities = DesiredCapabilities.FIREFOX.copy()

            if not driver and 'phantomjs' in driver_type.lower():
                driver = WebDriverProxy().phantomjs_driver()
                # driver = webdriver.PhantomJS()
                # capabilities = DesiredCapabilities.PHANTOMJS.copy()
            if not driver and 'firefox' in driver_type.lower():
                driver = webdriver.Firefox()
                # capabilities = DesiredCapabilities.FIREFOX.copy()
            if not driver and 'chrome' in driver_type.lower():
                driver = webdriver.Chrome()
                # capabilities = DesiredCapabilities.CHROME.copy()
            if not driver:
                driver = webdriver.PhantomJS()

            # driver = webdriver.Remote(desired_capabilities=capabilities, command_executor=selenium_grid_url)
        else:
            driver = webdriver.PhantomJS()

        driver.implicitly_wait(implicitly_wait)

    return driver


def ajax_complete(driver):
    try:
        return 0 == driver.execute_script("return jQuery.active")
    except WebDriverException:
        pass


def driver_wait(driver, itime, callback):
    #wait for ajax items to load
    WebDriverWait(driver, itime).until(callback,)

    assert "ajax loaded string" in driver.page_source


class SeleniumDownloaderMiddleware(object):
    def process_request(self, request, spider):
        if hasattr(spider, 'use_selenium') and spider.use_selenium:
            #check if spider has driver defined if not just use from settings
            if hasattr(spider, 'selenium_driver'):
                driver_type = getattr(spider, 'selenium_driver', settings.get('SELENIUM_WEBDRIVER'))
            else:
                driver_type = settings.get('SELENIUM_WEBDRIVER')

            print driver_type
            driver = get_driver(driver_type=driver_type)

            driver.get(request.url)

            #set that this request was made with selenium driver
            request.meta['is_selenium'] = True

            html = driver.execute_script('return document.documentElement.innerHTML;')
            if '</pre></body>' in html:
                if 'head><body><pre' in html:
                    if '<head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">' in html[0:78]:
                        html = html.replace('<head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', '')
                    elif '</head><body><pre>' in html:
                        html = html.split('</head><body><pre>')[1]
                if '</pre></body>' in html[-13:]:
                    html = html.replace('</pre></body>', '')

            url = driver.execute_script('return window.location.href;')

            response = HtmlResponse(
                url=url,
                encoding='utf-8',
                body=html.encode('utf-8'),
                request=request,
            )
            #close browser if we say in spider to close it
            if hasattr(spider, 'selenium_close_driver') and\
                    getattr(spider, 'selenium_close_driver') is True:
                reuseable_driver = None
                driver.close()

            return response
        return None