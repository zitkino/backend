# -*- coding: utf-8 -*-


from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.selector import Selector

from ..utils import absolutize_url
from ..loaders import ShowtimeLoader


class Fields(object):
    """Field definitions container."""

    def __init__(self, fields):
        self.fields = []
        for field in fields:
            if len(field) == 2:
                field_name, xpath = field
                subloader_cls = None
            elif len(field) == 3:
                field_name, xpath, subloader_cls = field
            else:
                raise ValueError
            self.fields.append((field_name, xpath, subloader_cls))

    def __iter__(self):
        return iter(self.fields)

    def get_xpath(self, field_name):
        return '|'.join([
            xpath for (name, xpath, _) in self.fields if name == field_name
        ])


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
    calendar_url = None

    # Main calendar element and links to following days/weeks/months...
    calendar_max_pages = 10
    calendar_element = "//body"  # XPath expression
    calendar_next_link = ""  # XPath expression

    # Main calendar's showtimes and their attributes
    calendar_showtime_element = ""  # XPath expression
    calendar_showtime = Fields([
        # ('title', ".//h1")
        # ('booking', ".//form", BookingLoader)
        # ...
    ])

    # Information on film's detail page
    film = Fields([
        # ('title', ".//h1")
        # ('booking', ".//form", BookingLoader)
        # ...
    ])

    # Possible subcalendar on film's detail page
    subcalendar_element = ""  # XPath expression
    subcalendar_showtime_element = ""  # XPath expression
    subcalendar_showtime = Fields([
        # ('title', ".//h1")
        # ('booking', ".//form", BookingLoader)
        # ...
    ])

    def __init__(self, *args, **kwargs):
        super(BaseCinemaSpider, self).__init__(*args, **kwargs)
        self.calendar_pages = 1

    def start_requests(self):
        return [self.make_requests_from_url(self.calendar_url)]

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
            return []
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
            self.populate_loader(loader, self.calendar_showtime)

            for rv in self.follow_film_url(resp, showtime, loader):
                yield rv

    def follow_film_url(self, resp, showtime, loader):
        """Follows the 'film_url' in order to parse film's detail page."""
        xpath = self.calendar_showtime.get_xpath('film_url')
        if xpath:
            film_urls = showtime.xpath(xpath).extract()
            subreqs = self.subrequests(film_urls, resp, self.parse_film,
                                       meta={'loader': loader})
            for subreq in subreqs:
                yield subreq
        else:
            yield loader.load_item()

    def parse_film(self, resp):
        """Parses film's detail page."""
        loader = resp.meta['loader']
        self.populate_loader(loader, self.film)
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
            self.populate_loader(loader, self.subcalendar_showtime)
            yield loader.load_item()

    def populate_loader(self, loader, fields):
        """Populates loader according to field definitions."""
        for field_name, xpath, subloader_cls in fields:
            if subloader_cls is not None:
                for result in loader.selector.xpath(xpath):
                    subloader = subloader_cls(
                        selector=result,
                        response=loader.context.get('response')
                    )
                    loader.add_value(field_name, subloader.load_item())
            else:
                loader.add_xpath(field_name, xpath)

    def subrequests(self, urls, resp, callback, meta=None):
        """Helper for spawning subrequests."""
        for url in urls:
            subreq = Request(absolutize_url(url, resp), callback=callback)
            subreq.meta.update(meta or {})
            yield subreq
