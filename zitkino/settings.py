# -*- coding: utf-8 -*-


LOG_LEVEL = 'DEBUG'

BOT_NAME = 'zitkino'
SPIDER_MODULES = ['zitkino.spiders']

USER_AGENT = 'zitkino/3.0 (+http://zitkino.cz)'
DEFAULT_REQUEST_HEADERS = {'Accept-Language': 'cs'}
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'zitkino.pipelines.DropIncompletePipeline': 100,
}
