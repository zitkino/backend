# -*- coding: utf-8 -*-


import re
import functools

import lxml.html
from scrapy.selector import Selector, SelectorList

from .crawler import Crawler
from .utils import tag_name, absolutize_url
from .loaders import TagLoader, RequestLoader
from .processors import NormalizeSpace, AbsolutizeUrls


class BaseParser(object):

    def __call__(self, selector, response):
        raise NotImplementedError


class BaseTagParser(BaseParser):

    def __call__(self, selector, response):
        loader = TagLoader(selector=selector, response=response)
        self.load(loader)

        header = self.parse_column_header(selector, response)
        if header:
            loader.add_value('type', header.get('name'))
            loader.add_value('url', header.get('url'))
        yield loader.load_item()

    def parse_column_header(self, selector, response):
        td = selector.xpath("./ancestor-or-self::td[1]")
        header = selector.xpath("./ancestor-or-self::table[1]//tr[th]")
        if not td or not header:
            return None

        position = len(td.xpath("./preceding-sibling::td"))
        th = header.xpath('th[{}]'.format(position + 1))

        parser = TagParser()
        try:
            return next(parser(selector=th, response=response))
        except StopIteration:
            return None

    def load(self, loader):
        raise NotImplementedError


class TagParser(BaseTagParser):

    def __call__(self, selector, response):
        loader = TagLoader(selector=selector, response=response)
        for item in self.parse_items(selector, response):
            loader.add_value('name', item.get('name'))
            loader.add_value('code', item.get('code'))
            loader.add_value('url', item.get('url'))
            loader.add_value('type', item.get('type'))
        yield loader.load_item()

    def parse_items(self, selector, response):
        jobs = []
        if selector.xpath("./self::img"):
            jobs.append((selector, ImageTagParser))
            link = selector.xpath("./parent::a")
            if link:
                jobs.append((link, LinkTagParser))

        elif selector.xpath("./self::a"):
            jobs.append((selector, LinkTagParser))
            img = selector.xpath("./descendant::img")
            if img:
                jobs.append((img, ImageTagParser))

        else:
            jobs.append((selector, TextTagParser))

        for sel, parser in jobs:
            for item in parser()(selector=sel, response=response):
                yield item


class TextTagParser(BaseTagParser):

    def load(self, loader):
        name = loader.lookup_legend('.//text()')
        if name:
            loader.add_value('name', name)
            loader.add_xpath('code', "./@title")

        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', ".//text()")
        loader.add_xpath('code', ".//text()")


class LinkTagParser(BaseTagParser):

    def load(self, loader):
        name = loader.lookup_legend('./@href', processor=AbsolutizeUrls())
        if name:
            loader.add_value('name', name)
            loader.add_xpath('code', "./@title")

        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', ".//text()")
        loader.add_xpath('code', ".//text()")
        loader.add_xpath('url', "./@href")


class ImageTagParser(BaseTagParser):

    def load(self, loader):
        name = loader.lookup_legend('./@src', processor=AbsolutizeUrls())
        if name:
            loader.add_value('name', name)
            loader.add_xpath('code', "./@title")
            loader.add_xpath('code', "./@alt")

        loader.add_xpath('name', "./@title")
        loader.add_xpath('name', "./@alt")
        loader.add_xpath('code', "./@src")


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


class TabLabelParser(BaseParser):

    def __call__(self, selector, response):
        if not isinstance(selector, SelectorList):
            selector = SelectorList([selector])

        for tab_sel in selector:
            if tag_name(tab_sel):
                ids = tab_sel.xpath('./@id').extract()
            else:
                ids = tab_sel.extract()

            for tab_id in ids:
                xpath = "//a[@href='#{}']//text()".format(tab_id)

                for value in Selector(response).xpath(xpath).extract():
                    yield value


class LegendParser(BaseParser):

    key_tags = ['br', 'strong', 'img']

    def __init__(self, item_sep=',', mapping_sep='-', key_tags=None,
                 stopwords=None):
        self.item_sep = item_sep
        self.mapping_sep = mapping_sep

        stopwords = stopwords or []
        self.stopwords = stopwords
        self.stopwords_re = re.compile(r'|'.join([
            stopword for stopword in stopwords
        ]), re.U | re.I)

        key_tags = (key_tags or self.key_tags)
        self.key_tags = key_tags
        self.key_tags_re = [
            re.compile(r'<{}[^>]*>'.format(re.escape(tag_name)))
            for tag_name in key_tags
        ]

    def _replace_tag(self, match, response):
        el = lxml.html.fromstring(match.group(0))
        link = el.get('src', el.get('href'))
        if link:
            repl = absolutize_url(link, response)
        else:
            repl = el.get('title', el.get('alt', el.text_content()))
        return '{} {} '.format(self.item_sep, repl)

    def clean_html(self, html, response):
        # replace tags representing keys of the legend mapping
        for tag_re in self.key_tags_re:
            html = tag_re.sub(
                functools.partial(self._replace_tag, response=response),
                html
            )

        # remove text nodes with stopwords
        root = lxml.html.fromstring(html)
        elements = [root] + list(root.iterdescendants())

        for element in elements:
            if element.text:
                element.text = self.stopwords_re.sub('', element.text)
            if element.tail:
                element.tail = self.stopwords_re.sub('', element.tail)
        return lxml.html.tostring(root)

    def clean_text(self, text):
        return next(NormalizeSpace()([text]))

    def __call__(self, selector, response):
        inner_html = ''.join(selector.xpath("./child::node()").extract())
        inner_html = self.clean_html(inner_html, response)

        text = ''.join(Selector(text=inner_html).xpath(".//text()").extract())
        text = self.clean_text(text)

        raw_legend = [
            tuple([part.strip() for part in item.split(self.mapping_sep)])
            for item in text.split(self.item_sep)
        ]
        return {
            item[0]: item[1] for item in raw_legend
            if len(item) == 2 and item[0] and item[1]
        }
