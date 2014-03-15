# -*- coding: utf-8 -*-


import re

from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from scrapy.selector import Selector as BaseSelector, SelectorList


def absolute_url(url, response):
    if url.startswith('http'):
        return url
    return urljoin_rfc(get_base_url(response), url)


class Selector(BaseSelector):

    def _query_one_or_many(self, meth, queries):
        if isinstance(queries, basestring):
            queries = [queries]
        results = []
        for query in queries:
            results.extend(meth(query))
        return SelectorList(results)

    def xpath(self, queries):
        return self._query_one_or_many(
            super(Selector, self).xpath,
            queries,
        )

    def css(self, queries):
        return self._query_one_or_many(
            super(Selector, self).css,
            queries,
        )

    def re(self, queries):
        return self._query_one_or_many(
            super(Selector, self).re,
            queries,
        )


class NormalizeSpace(object):

    _whitespace_re = re.compile(
        ur'[{0}\s\xa0]+'.format(
            re.escape(''.join(map(unichr, range(0, 32) + range(127, 160))))
        )
    )

    def __call__(self, values):
        for value in values:
            if isinstance(value, basestring):
                yield self._whitespace_re.sub(' ', value).strip()
            else:
                yield value


class Unique(object):

    def __call__(self, values):
        return list(frozenset(v for v in values if v))
