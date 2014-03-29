# -*- coding: utf-8 -*-


from .crawler import Crawler
from .loaders import TagLoader, RequestLoader


class BaseParser(object):

    def __init__(self, selector, **kwargs):
        self.selector = selector
        self.response = kwargs.pop('response', None)
        self.context = kwargs

    def __call__(self):
        raise NotImplementedError


class TextTagParser(BaseParser):

    def __call__(self):
        loader = TagLoader(selector=self.selector, response=self.response)
        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', ".//text()")
        loader.add_xpath('code', ".//text()")
        return loader.load_item()


class LinkTagParser(BaseParser):

    def __call__(self):
        loader = TagLoader(selector=self.selector, response=self.response)
        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', ".//text()")
        loader.add_xpath('code', ".//text()")
        loader.add_xpath('url', "./@href")
        return loader.load_item()


class ImageTagParser(BaseParser):

    def __call__(self):
        loader = TagLoader(selector=self.selector, response=self.response)
        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', "./@alt")
        loader.add_xpath('code', "./@src")
        return loader.load_item()


class RequestParser(BaseParser):

    def __call__(self):
        loader = RequestLoader()
        crawler = Crawler(self.selector)
        for request in crawler.requests(self.response):
            loader.add_value('url', request.url)
            loader.add_value('method', request.method)
            loader.add_value('data', request.body)
            break
        return loader.load_item()
