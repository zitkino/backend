# -*- coding: utf-8 -*-


import execjs
import lxml.html
from scrapy.selector import Selector


class JavaScript(object):

    def __init__(self, code='', selector=None):
        self.code = code
        self.selector = selector

    def append(self, code):
        self.code += '\n' + code

    def append_xpath(self, xpath):
        self.append(' '.join(self.selector.xpath(xpath).extract()))

    def _call(self, code, fn):
        return execjs.compile(code).call(fn)

    def call(self, fn):
        return self._call(self.code, fn)

    def capture(self):
        code = '\n'.join([
            "function __runtime__() {"
            "    var __output__ = [];",
            "    var document = {write: function(s) { __output__.push(s) } };",
            self.code,
            "    return __output__;",
            "}"
        ])
        return ''.join(self._call(code, '__runtime__'))

    def capture_as_dom(self):
        return lxml.html.fromstring(self.capture())

    def capture_as_selector(self):
        return Selector(text=self.capture())
