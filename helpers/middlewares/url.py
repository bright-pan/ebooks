# A spider middleware to canonicalize the urls of all requests generated from a spider.

from scrapy.http import Request
from scrapy.utils.url import canonicalize_url

class UrlCanonicalizerMiddleware(object):
    def process_spider_output(self, response, result, spider):
        for r in result:
            if isinstance(r, Request):
                curl = canonicalize_url(r.url)
                if curl != r.url:
                    r = r.replace(url=curl)
            yield r


# A downloader middleware automatically to redirect pages containing a rel=canonical in their contents to the canonical url (if the page itself is not the canonical one),

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.url import url_is_from_spider
from scrapy.http import HtmlResponse
from scrapy import log


class RelCanonicalMiddleware(object):
    _extractor = SgmlLinkExtractor(restrict_xpaths=['//head/link[@rel="canonical"]'], tags=['link'], attrs=['href'])

    def process_response(self, request, response, spider):
        if isinstance(response, HtmlResponse) and response.body and getattr(spider, 'follow_canonical_links', False):
            rel_canonical = self._extractor.extract_links(response)
            if rel_canonical:
                rel_canonical = rel_canonical[0].url
                if rel_canonical != request.url and url_is_from_spider(rel_canonical, spider):
                    log.msg("Redirecting (rel=\"canonical\") to %s from %s" % (rel_canonical, request), level=log.DEBUG, spider=spider)
                    return request.replace(url=rel_canonical, callback=lambda r: r if r.status == 200 else response)
        return response

class CleanUrl(object):
    seen_urls = {}
    def process_request(self, request, spider):
        url = spider.clean_url(request.url)
        if url in self.seen_urls:
              raise IgnoreRequest()
        else:
            self.seen_urls.add(url)
        return request.replace(url=url)