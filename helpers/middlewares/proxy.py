import time
import sys

from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware

from helpers.restart_service import kill_service, start_service
from helpers.proxy import change_proxy

from scrapy.http import Request
from scrapy.conf import settings
from scrapy import log


MAX_RETRIES = 10  # restart 10 times max
MAX_TIME_SECONDS = 30  # seconds
class TorProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('HTTP_PROXY')

        # proxy_user_pass = "%s:%s" % (settings.get('HTTP_PROXY_USER'),settings.get('HTTP_PROXY_PASS'))
        # encoded_user_pass = base64.encodestring(proxy_user_pass)
        # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass

    def process_response(self, request, response, spider):
        def _change_proxy_and_resend_request(meta_key, message):
            log.msg("%s" % message, log.INFO)
            change_proxy(log_msg=True)
            log.msg("PROXY CHANGED", log.INFO)
            log.msg("GEO_LOCATION: %s" % request.meta.get('geo_location'), log.INFO)

            meta_value = request.meta.get(meta_key, 0)
            request.meta.update({meta_key: meta_value + 1})

            if not request.meta.get('%s_time' % meta_key, None):
                request.meta.update({'%s_time' % meta_key: time.time()})
            return Request(
                url=request.url,
                meta=request.meta,
                dont_filter=True,
            )

        if response.status == 504 or\
                response.status == 503 or\
                response.status == 502 or\
                response.status == 403 or\
                response.status == 400 or\
                response.status == 402:
            handled = False
            body = response.body.lower()

            if "polipo" in body:  # 504
                # stop the crawler if we max out on tries or in time
                if request.meta.get('polipo_restarted') >= MAX_RETRIES or \
                        time.time() - request.meta.get('polipo_restarted_time', time.time()) > MAX_TIME_SECONDS:
                    print >> sys.stderr, "POLIPO RESTARTED TOO MANY TIMES"
                    spider.crawler.stop()

                if 'host unreachable' in response.body:  # dont restart polipo if host unreachable
                    print >> sys.stderr, '[%s] Unreachable Host Found' % spider.name
                else:
                    kill_service('polipo')
                    start_service('polipo')
                    return _change_proxy_and_resend_request('polipo_restarted', "RESTARTED POLIPO")
                handled = True

            # handle google(and any other pages) with captcha; change proxy
            if "captcha" in body:  # 503, 403
                return _change_proxy_and_resend_request('captcha_found', "CAPTCHA FOUND")

            # handle craigslist.org IP blocked
            if "blocked" in body:  # 403
                return _change_proxy_and_resend_request('ip_blocked', "IP BLOCKED")

            # handle google sorry, automated queries
            if "sorry" in body and 'automated' in body:
                return _change_proxy_and_resend_request('automation_found', 'AUTOMATION FOUND')

            if "access denied" in body:
                return _change_proxy_and_resend_request('access_denied', 'ACCESS DENIED')

            if not handled:
                print >> sys.stderr, response.body
            return response
        else:
            return response


def _retry_proxy(self, request, reason, spider):
    change_proxy(log_msg=True)
    # time.sleep(1)
    return RetryMiddleware._retry(self, request, reason, spider)


class AutoChangeTorProxyMiddleware(RetryMiddleware):
    def process_spider_output(self, response, result, spider):
        if response.status == 503:
            print 'CHANGE PROXY'
            yield _retry_proxy(self, response.request, '%s CHANGE PROXY' % response.status, spider)
        else:
            for r in result:
                yield r


class RetryChangeTorProxyMiddleware(RetryMiddleware):
    def _retry(self, request, reason, spider):
        print 'CHANGE PROXY'
        return _retry_proxy(self, request, reason, spider)