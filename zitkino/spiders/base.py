# -*- coding: utf-8 -*-


from scrapy.http import Request
from scrapy.spider import Spider

from ..utils import Selector, absolute_url
from ..loaders import ShowtimeLoader, TagLoader


class CinemaSpider(Spider):

    name = None
    allowed_domains = []
    start_urls = []

    calendar_max_pages = 10
    calendar_element = "//body"  # XPath
    calendar_next_link = []  # XPath

    calendar_showtime_element = []  # XPath
    calendar_showtime = {
        # 'title_original': []  # XPath
        # ...
    }
    calendar_showtime_tag_loaders = []

    film = {
        # 'title_original': []  # XPath
        # ...
    }
    film_tag_loaders = []

    subcalendar_element = []  # XPath
    subcalendar_showtime_element = []  # XPath
    subcalendar_showtime = {
        # 'title_original': []  # XPath
        # ...
    }
    subcalendar_showtime_tag_loaders = []

    def __init__(self, *args, **kwargs):
        super(CinemaSpider, self).__init__(*args, **kwargs)
        self.calendar_pages = 1

    def parse(self, resp):
        for rv in self.parse_calendar(resp):
            yield rv
        for rv in self.follow_next_link(resp):
            yield rv

    def follow_next_link(self, resp):
        if not self.calendar_next_link:
            return
        limit = self.calendar_max_pages - self.calendar_pages

        next_urls = Selector(resp).xpath(self.calendar_next_link).extract()
        next_urls = list(frozenset(next_urls))[:limit]
        self.calendar_pages += len(next_urls)

        return self.subrequests(next_urls, resp, self.parse)

    def parse_calendar(self, resp):
        calendars = Selector(resp).xpath(self.calendar_element)
        showtimes = calendars.xpath(self.calendar_showtime_element)

        for showtime in showtimes:
            loader = ShowtimeLoader(selector=showtime, response=resp)
            loader.add_value('calendar_url', resp.url)
            loader.add_tags(self.calendar_showtime_tag_loaders)
            loader.add_attrs(self.calendar_showtime)

            for rv in self.follow_film_url(resp, showtime, loader):
                yield rv

    def follow_film_url(self, resp, showtime, loader):
        film_url_xpath = self.calendar_showtime.get('film_url')
        if film_url_xpath:
            film_urls = showtime.xpath(film_url_xpath).extract()
            subreqs = self.subrequests(film_urls, resp, self.parse_film,
                                       meta={'loader': loader})
            for subreq in subreqs:
                yield subreq
        else:
            yield loader.load_item()

    def parse_film(self, resp):
        loader = resp.meta['loader']
        loader.add_tags(self.film_tag_loaders)
        loader.add_attrs(self.film)
        yield loader.load_item()

        for showtime in self.parse_subcalendar(resp):
            yield showtime

    def parse_subcalendar(self, resp):
        subcalendars = Selector(resp).xpath(self.subcalendar_element)
        showtimes = subcalendars.xpath(self.subcalendar_showtime_element)

        for showtime in showtimes:
            loader = ShowtimeLoader(selector=showtime, response=resp)
            loader.add_value('calendar_url', resp.url)
            loader.add_tags(self.subcalendar_showtime_tag_loaders)
            loader.add_attrs(self.subcalendar_showtime)
            yield loader.load_item()

    def subrequests(self, urls, resp, callback, meta=None):
        for url in urls:
            subreq = Request(absolute_url(url, resp), callback=callback)
            subreq.meta.update(meta or {})
            yield subreq


class TextTagLoader(TagLoader):

    def __init__(self, *args, **kwargs):
        super(TextTagLoader, self).__init__(*args, **kwargs)
        self.add_xpath('name', "./text()")


class LinkTagLoader(TagLoader):

    def __init__(self, *args, **kwargs):
        super(LinkTagLoader, self).__init__(*args, **kwargs)
        self.add_xpath('name', "./@title")
        self.add_xpath('code', "./text()")
        self.add_xpath('url', "./@href")


class ImageTagLoader(TagLoader):

    def __init__(self, *args, **kwargs):
        super(ImageTagLoader, self).__init__(*args, **kwargs)
        self.add_xpath('name', "./@title")
        self.add_xpath('name', "./@alt")
        self.add_xpath('code', "./@src")
