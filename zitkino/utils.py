# -*- coding: utf-8 -*-


import urllib

from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url


def absolutize_url(url, response):
    """Takes URL and makes it absolute."""
    if url.startswith('http'):
        return url
    return urljoin_rfc(get_base_url(response), url)


def serialize_form(selector):
    data = []
    for field in selector.xpath(".//input"):
        data.append((
            field.xpath('./@name').extract()[0].encode('utf-8'),
            field.xpath('./@value').extract()[0].encode('utf-8'),
        ))
    return urllib.urlencode(data)
