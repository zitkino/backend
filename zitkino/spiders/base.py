# -*- coding: utf-8 -*-


from scrapy.http import Request
from scrapy.spider import Spider

from ..loaders import ShowtimeLoader
from ..utils import Selector, absolutize_url


class BaseCinemaSpider(Spider):
    """
    Generic cinema calendar spider.

    Does all the hard work - the only thing one needs to do in order to
    write a new cinema spider is to inherit from this class and declare
    XPath expressions.
    """

    # TODO parsovat texty jako
    # (Attila Marcel) Režie: Sylvain Chomet, F, 2013,
    # francouzsky / české titulky, 102 min

    # General settings
    name = None
    allowed_domains = []
    start_urls = []

    # Main calendar element and links to following days/weeks/months...
    calendar_max_pages = 10
    calendar_element = "//body"  # XPath expression
    calendar_next_link = []  # XPath expression (or list of them)

    # Main calendar's showtimes and their attributes
    calendar_showtime_element = []  # XPath expression (or list of them)
    calendar_showtime = {
        # 'title_original': []  # XPath expression (or list of them)
        # ...
    }
    calendar_showtime_tag_loaders = []

    # Information on film's detail page
    film = {
        # 'title_original': []  # XPath expression (or list of them)
        # ...
    }
    film_tag_loaders = []

    # Possible subcalendar on film's detail page
    subcalendar_element = []  # XPath expression (or list of them)
    subcalendar_showtime_element = []  # XPath expression (or list of them)
    subcalendar_showtime = {
        # 'title_original': []  # XPath expression (or list of them)
        # ...
    }
    subcalendar_showtime_tag_loaders = []

    def __init__(self, *args, **kwargs):
        super(BaseCinemaSpider, self).__init__(*args, **kwargs)
        self.calendar_pages = 1

    def parse(self, resp):
        """Parses the first page as a calendar and is able to follow calendars
        for next days/weeks/months... by 'next links'.
        """
        for rv in self.parse_calendar(resp):
            yield rv
        for rv in self.follow_next_link(resp):
            yield rv

    def follow_next_link(self, resp):
        """Finds and follows next links."""
        if not self.calendar_next_link:
            return
        limit = self.calendar_max_pages - self.calendar_pages

        next_urls = Selector(resp).xpath(self.calendar_next_link).extract()
        next_urls = list(frozenset(next_urls))[:limit]
        self.calendar_pages += len(next_urls)

        return self.subrequests(next_urls, resp, self.parse)

    def parse_calendar(self, resp):
        """Parses the main calendar element."""
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
        """Follows the 'film_url' in order to parse film's detail page."""
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
        """Parses film's detail page."""
        loader = resp.meta['loader']
        loader.add_tags(self.film_tag_loaders)
        loader.add_attrs(self.film)
        yield loader.load_item()

        for showtime in self.parse_subcalendar(resp):
            yield showtime

    def parse_subcalendar(self, resp):
        """Parses possible subcalendars on film's detail page."""
        subcalendars = Selector(resp).xpath(self.subcalendar_element)
        showtimes = subcalendars.xpath(self.subcalendar_showtime_element)

        for showtime in showtimes:
            loader = ShowtimeLoader(selector=showtime, response=resp)
            loader.add_value('calendar_url', resp.url)
            loader.add_tags(self.subcalendar_showtime_tag_loaders)
            loader.add_attrs(self.subcalendar_showtime)
            yield loader.load_item()

    def subrequests(self, urls, resp, callback, meta=None):
        """Helper for spawning subrequests."""
        for url in urls:
            subreq = Request(absolutize_url(url, resp), callback=callback)
            subreq.meta.update(meta or {})
            yield subreq
