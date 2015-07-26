# -*- coding: utf-8 -*-


from scrapy import log
from scrapy.contrib.downloadermiddleware.retry \
    import RetryMiddleware


class RetryRecordMiddleware(RetryMiddleware):

    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)

    def record_failed(self, path, request, exception, failed_meta):
        retries = request.meta.get('retry_times', 0) + 1
        log.msg('retries time is %s %d' % (retries, retries))
        log.msg('max_retry_times is %d' % self.max_retry_times)
        if retries > self.max_retry_times:
            failed_list = request.meta.get(failed_meta, [])
            failed_list = [x.strip() for x in failed_list]
            log.msg('recording failed list %s' % '\t'.join(failed_list))
            of = open(path, 'a')
            of.write('%s\n' % '\t'.join(failed_list))
            of.close()

    def process_exception(self, request, exception, spider):
        to_return = RetryMiddleware.process_exception(
            self, request, exception, spider)
        # customize retry middleware by modifying this
        request.meta['url'] = request.url
        self.record_failed('failed.txt', request, exception, 'url')
        return to_return