# -*- coding: utf-8 -*-


import re

from .crawler import Crawler
from .loaders import TagLoader, RequestLoader


class BaseParser(object):

    def __call__(self, selector, response):
        raise NotImplementedError


class TextTagParser(BaseParser):

    def __call__(self, selector, response):
        loader = TagLoader(selector=selector, response=response)
        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', ".//text()")
        loader.add_xpath('code', ".//text()")
        yield loader.load_item()


class LinkTagParser(BaseParser):

    def __call__(self, selector, response):
        loader = TagLoader(selector=selector, response=response)
        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', ".//text()")
        loader.add_xpath('code', ".//text()")
        loader.add_xpath('url', "./@href")
        yield loader.load_item()


class ImageTagParser(BaseParser):

    def __call__(self, selector, response):
        loader = TagLoader(selector=selector, response=response)
        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', "./@alt")
        loader.add_xpath('code', "./@src")
        yield loader.load_item()


class RequestParser(BaseParser):

    def __call__(self, selector, response):
        loader = RequestLoader()
        crawler = Crawler(selector)
        for request in crawler.requests(response):
            loader.add_value('url', request.url)
            loader.add_value('method', request.method)
            loader.add_value('data', request.body)
            break
        yield loader.load_item()


class SwitchParser(BaseParser):

    def __init__(self, rules):
        self.rules = [
            (
                xpath,
                re.compile(regexp) if regexp else None,
                (lambda *a, **kw: [f]) if isinstance(f, basestring) else f
            )
            for (xpath, regexp, f) in rules
        ]

    def __call__(self, selector, response):
        for xpath, regexp, f in self.rules:
            results = selector.xpath(xpath).extract()
            if isinstance(results, basestring):
                results = [results]
            for result in results:
                if regexp is None or regexp.search(result):
                    parser_context = {
                        'selector': selector,
                        'response': response,
                        'xpath': xpath,
                        'regexp': regexp,
                    }
                    return f(parser_context)
        return []
