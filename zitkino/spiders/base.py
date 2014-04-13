# -*- coding: utf-8 -*-


import itertools

from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.selector import Selector

from ..crawler import Crawler
from ..loaders import ShowtimeLoader


class FieldDefinitions(object):
    """Field definitions container."""

    def __init__(self, fields):
        self.fields = []
        self.extend(fields)

    def _parse_definition(self, definition):
        if len(definition) == 2:
            field_name, xpath = definition
            parser_cls = None
        elif len(definition) == 3:
            field_name, xpath, parser_cls = definition
        else:
            raise ValueError
        return (field_name, xpath, parser_cls)

    def append(self, definition):
        self.fields.append(self._parse_definition(definition))

    def extend(self, definitions):
        for definition in definitions:
            self.append(definition)

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
    couple of XPath expressions.
    """

    #! Name of the scraper.
    name = None

    #! Base URL where the main calendar is to be found.
    calendar_url = None

    #! XPath expression for the main calendar element.
    calendar_element = "//body"

    #! XPath expression poiting to a HTML element representing
    #! a transition to a next page of the main calendar. This can be
    #! usually an ``<a>`` or ``<form>``.
    calendar_next = ""

    #! Fixed form data used for crawling next pages of the main calendar.
    #!
    #! In case :obj:`~BaseCinemaSpider.calendar_next` points to a form,
    #! this dict is used to pre-fill the form with data when determining
    #! all possible fillings to follow. For more complicated cases it's
    #! possible to override
    #! :meth:`~BaseCinemaSpider.iter_calendar_next_formdata()`
    calendar_next_formdata = {}

    #! Maximum number of next main calendar pages followed within
    #! one variant.
    #!
    #! If the element specified by :obj:`~BaseCinemaSpider.calendar_next`
    #! points to a form, the variant stands for one possible filling of
    #! the form. If it points to a link, then the maximum number of pages
    #! will apply in total, because there is only one way to
    #! *fill and follow* a link.
    calendar_next_max_depth = 10

    #! XPath expression pointing to an element of showtime within the main
    #! calendar.
    calendar_showtime_element = ""

    #! Main calendar showtime attributes as a list of field definitions.
    #!
    #! Field definitions are tuples of two or three items, where the first
    #! one is an attribute name, second is an XPath expression, and the last
    #! one, optional, is a custom specialized parser to be used to parse
    #! the attribute::
    #!
    #!    calendar_showtime = [
    #!        ('title', ".//h1|.//h2")
    #!        ('booking', ".//form", RequestParser())
    #!        ...
    #!    ]
    calendar_showtime = []

    #! Film detail attributes as a list of field definitions.
    #!
    #! The same applies as for :obj:`~BaseCinemaSpider.calendar_showtime`.
    film = []

    #! XPath expression for a possible subcalendar element.
    subcalendar_element = ""

    #! XPath expression pointing to an element of showtime within possible
    #! subcalendar.
    subcalendar_showtime_element = ""

    #! Subcalendar showtime attributes as a list of field definitions.
    #!
    #! The same applies as for :obj:`~BaseCinemaSpider.calendar_showtime`.
    subcalendar_showtime = []

    def __init__(self, *args, **kwargs):
        super(BaseCinemaSpider, self).__init__(*args, **kwargs)
        self.calendar_pages = 1

    def start_requests(self):
        return [self.make_requests_from_url(self.calendar_url)]

    def parse(self, response):
        """Parses the first page as a calendar and is able to follow calendars
        for next days/weeks/months... by *next links*.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        for rv in self._parse_calendar(response):
            yield rv
        for rv in self._follow_next(response):
            yield rv

    def _follow_next(self, response):
        """Finds and follows next calendar pages.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        if not self.calendar_next:
            return []

        crawler = Crawler(
            self.calendar_next,
            formfilling=True,
            max_depth=self.calendar_next_max_depth
        )
        return itertools.chain(*[
            crawler.requests(response, formdata, self.parse)
            for formdata in self.iter_calendar_next_formdata()
        ])

    def _parse_calendar(self, response):
        """Parses the main calendar element.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        calendars = Selector(response).xpath(self.calendar_element)
        showtimes = calendars.xpath(self.calendar_showtime_element)

        for selector in showtimes:
            loader = ShowtimeLoader(selector=selector, response=response)
            self.parse_calendar_showtime(loader, response)
            item = loader.load_item()

            for rv in self._follow_film_url(item):
                yield rv

    def _follow_film_url(self, item):
        """Follows the ``film_url`` in order to parse film's detail page.

        :param item: Showtime item.
        :type item: :class:`scrapy.item.Item`
        """
        url = item.get('film_url')
        if url:
            yield Request(url, callback=self._parse_film, meta={'item': item},
                          dont_filter=True)
        else:
            yield item

    def _parse_film(self, response):
        """Parses film's detail page.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        loader = ShowtimeLoader(item=response.meta['item'], response=response)
        self.parse_film(loader, response)
        yield loader.load_item()

        for item in self._parse_subcalendar(response):
            yield item

    def _parse_subcalendar(self, response):
        """Parses possible subcalendars on film's detail page.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        if not self.subcalendar_element:
            return
        subcalendars = Selector(response).xpath(self.subcalendar_element)

        if not self.subcalendar_showtime_element:
            return
        showtimes = subcalendars.xpath(self.subcalendar_showtime_element)

        for selector in showtimes:
            loader = ShowtimeLoader(selector=selector, response=response)
            self.parse_subcalendar_showtime(loader, response)
            yield loader.load_item()

    def _populate_loader(self, loader, fields):
        """Populates loader according to field definitions.

        :param item: Item loader.
        :type item: :class:`scrapy.contrib.loader.ItemLoader`
        :param fields: Field definitions.
        :type fields: :class:`FieldDefinitions`
        """
        selector = loader.selector
        response = loader.context.get('response')

        for field_name, xpath, parser in fields:
            if parser is not None:
                for result in selector.xpath(xpath):
                    for value in parser(result, response):
                        loader.add_value(field_name, value)
            else:
                loader.add_xpath(field_name, xpath)

    def iter_calendar_next_formdata(self):
        """Getter providing form data to *next calendar page* crawler.

        Form data variations are yielded one by one as dicts. By default
        only :obj:`~BaseCinemaSpider.calendar_next_formdata` is yielded.
        """
        yield self.calendar_next_formdata

    def get_calendar_showtime(self):
        """Getter providing showtime field definitions.

        By default :obj:`~BaseCinemaSpider.calendar_showtime` is taken,
        some more field definitions are added (implementing *smart defaults*
        for various fields) and this is returned as a
        :class:`FieldDefinitions` object.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        return FieldDefinitions(self.calendar_showtime)

    def parse_calendar_showtime(self, loader, response):
        """Calendar showtime parser.

        :param loader: Loader object.
        :type loader: :class:`scrapy.contrib.loader.ItemLoader`
        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        loader.add_value('calendar_url', response.url)
        loader.add_value('calendar_html', response.body)
        self._populate_loader(loader, self.get_calendar_showtime())

    def get_film(self):
        """Getter providing film detail field definitions.

        The same applies as for
        :meth:`~BaseCinemaSpider.get_calendar_showtime`, only
        :obj:`~BaseCinemaSpider.film` is taken by default.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        return FieldDefinitions(self.film + [
            ('csfd_id', "//a[contains(@href, 'csfd.cz')]/@href"),
            ('imdb_id', "//a[contains(@href, 'imdb.com')]/@href"),
            ('youtube_id', "//a[contains(@href, 'youtube.com')]/@href"),
            ('youtube_id', "//iframe[contains(@src, 'youtube.com')]/@src"),
        ])

    def parse_film(self, loader, response):
        """Film parser.

        :param loader: Loader object.
        :type loader: :class:`scrapy.contrib.loader.ItemLoader`
        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        self._populate_loader(loader, self.get_film())

    def get_subcalendar_showtime(self):
        """Getter providing subcalendar showtime field definitions.

        The same applies as for
        :meth:`~BaseCinemaSpider.get_calendar_showtime`, only
        :obj:`~BaseCinemaSpider.subcalendar_showtime` is taken by default.

        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        return FieldDefinitions(self.subcalendar_showtime)

    def parse_subcalendar_showtime(self, loader, response):
        """Subcalendar showtime parser.

        :param loader: Loader object.
        :type loader: :class:`scrapy.contrib.loader.ItemLoader`
        :param response: Currently processed response.
        :type response: :class:`scrapy.http.Response`
        """
        loader.add_value('calendar_url', response.url)
        loader.add_value('calendar_html', response.body)
        self._populate_loader(loader, self.get_subcalendar_showtime())
