class StartUrlReferrerMiddleware(object):
    def process_request(self, request, spider):
        request.headers.setdefault('Referer', request.url)