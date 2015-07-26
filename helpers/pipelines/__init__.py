from helpers.pipelines.image_downloader_pipeline import ImagesDownloaderPipeline
from helpers.pipelines.json_writer_pipeline import JsonWriterPipeline


class DeleteEmptyFieldsPipeline(object):
    def process_item(self, item, spider):
        for k, v in item.items():
            if not v:
                del item[k]

        return item


from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):
    def __init__(self):
        self.urls_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.urls_seen:
            raise DropItem("Duplicate item found: %s" % item['url'])
        else:
            self.urls_seen.add(item['url'])
            return item


