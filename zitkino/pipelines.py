# -*- coding: utf-8 -*-


from scrapy.exceptions import DropItem


class DropIncompletePipeline(object):

    def process_item(self, item, spider):
        if not item.get('title'):
            raise DropItem("Missing title.")
        return item
