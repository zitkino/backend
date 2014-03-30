# -*- coding: utf-8 -*-


import times
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url


def absolutize_url(url, response):
    """Takes URL and makes it absolute."""
    if url.startswith('http'):
        return url
    return urljoin_rfc(get_base_url(response), url)


def tag_name(selector):
    try:
        return selector.xpath("name(.)").extract()[0]
    except IndexError:
        return None


def now():
    return times.to_local(times.now(), 'Europe/Prague')
