# -*- coding: utf-8 -*-

# Scrapy settings for google_com project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'google_com'

SPIDER_MODULES = ['google_com.spiders']
NEWSPIDER_MODULE = 'google_com.spiders'

ITEM_PIPELINES = {
    'scrapylib.constraints.pipeline.ConstraintsPipeline': 350,
    BOT_NAME + '.pipelines.DeleteEmptyFieldsPipeline': 400,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 1,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    BOT_NAME + '.middlewares.RandomUserAgentMiddleware': 400,
    BOT_NAME + '.middlewares.SeleniumDownloaderMiddleware': 600,
}

SPIDER_MIDDLEWARES = {

}

USER_AGENT_LIST = [
    # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
    # 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36',

    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Googlebot/2.1 (+http://www.googlebot.com/bot.html)',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
]

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'

# LOG_ENABLED = True
# LOG_FILE = 'tmp/logs'
# LOG_LEVEL = 'DEBUG'

DOWNLOAD_TIMEOUT = 90

DUPEFILTER_CLASS = 'scrapy.dupefilter.RFPDupeFilter'

AJAXCRAWL_ENABLED = False
DEPTH_LIMIT = 0

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

ITEMS_BUCKET_NAME = ""
IMAGES_BUCKET_NAME = ""

FEED_FORMAT = "jsonlines"

FEED_URI = "s3://%(bucket_name)s/data/%%(name)s/%%(time)s.jl" % {'bucket_name': ITEMS_BUCKET_NAME}
IMAGES_STORE = "s3://%(bucket_name)s/images/" % {'bucket_name': IMAGES_BUCKET_NAME}

ITEMS_STORE = "s3://%(bucket_name)s/items/" % {'bucket_name': ITEMS_BUCKET_NAME}


AUTOTHROTTLE_ENABLED = False
REFERER_ENABLED = True

RETRY_ENABLED = False
RETRY_TIMES = 1
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 407, 408]

CONCURRENT_REQUESTS = 300

#spider_api port_range
TELNETCONSOLE_PORT = [6023, 6073]

SELENIUM_WEBDRIVER = 'Chrome'

TOR_PROXY_HOST = 'localhost'
TOR_PROXY_PORT = 9051
TOR_PROXY_PASS = 'tor-password'