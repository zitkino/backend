# -*- coding: utf-8 -*-


from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url
from scrapy.selector import Selector as BaseSelector, SelectorList


def absolutize_url(url, response):
    """Takes URL and makes it absolute."""
    if url.startswith('http'):
        return url
    return urljoin_rfc(get_base_url(response), url)


class Selector(BaseSelector):
    """
    Enhanced selector.

    Its methods accept also lists of XPath/CSS/RE expressions. If list of
    expressions is given, their results are combined and returned as only one
    :class:`SelectorList`.
    """

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
