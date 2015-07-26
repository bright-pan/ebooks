import random
from scrapy.conf import settings


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua = random.choice(settings.get('USER_AGENT_LIST'))
        settings.set('USER_AGENT', ua)
        if ua:
            request.headers.setdefault('User-Agent', ua)