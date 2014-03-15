# -*- coding: utf-8 -*-


import string
from decimal import Decimal

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, MapCompose

from .utils import serialize_form
from .items import Showtime, Film, Tag, Request
from .processors import (NormalizeSpace, Unique, AbsolutizeUrls, ToCsfdIds,
                         ToNumbers, ToImdbIds, ToYoutubeIds, ToTagCodes)


class FilmLoader(ItemLoader):

    default_item_class = Film
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    film_url_in = AbsolutizeUrls()
    csfd_id_in = ToCsfdIds()
    imdb_id_in = ToImdbIds()
    youtube_id_in = ToYoutubeIds()
    year_in = ToNumbers()
    duration_in = ToNumbers()
    poster_urls_in = AbsolutizeUrls()

    poster_urls_out = Unique()


class ShowtimeLoader(FilmLoader):

    default_item_class = Showtime
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    calendar_url_in = AbsolutizeUrls()
    price_in = ToNumbers(Decimal)

    tags_out = Unique()


class TagLoader(ItemLoader):

    default_item_class = Tag
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    code_in = ToTagCodes()
    url_in = AbsolutizeUrls()


class TextTagLoader(TagLoader):
    """Ready-made text tag loader."""

    def load_item(self):
        self.add_xpath('name', ".//text()")
        return super(TextTagLoader, self).load_item()


class LinkTagLoader(TagLoader):
    """Ready-made link tag loader."""

    def load_item(self):
        self.add_xpath('name', "./@title")
        self.add_xpath('code', ".//text()")
        self.add_xpath('url', "./@href")
        return super(LinkTagLoader, self).load_item()


class ImageTagLoader(TagLoader):
    """Ready-made image tag loader."""

    def load_item(self):
        self.add_xpath('name', "./@title")
        self.add_xpath('name', "./@alt")
        self.add_xpath('code', "./@src")
        return super(ImageTagLoader, self).load_item()


class RequestLoader(ItemLoader):

    default_item_class = Request
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    url_in = AbsolutizeUrls()
    method_in = MapCompose(string.upper)

    def load_item(self):
        name = self.selector.xpath("name(.)").extract()[0]
        if name == 'a':
            self.add_xpath('url', "./@href")
            self.add_value('method', "GET")

        elif name == 'form':
            self.add_xpath('url', "./@action")
            self.add_xpath('method', "./@method")
            self.add_value('data', serialize_form(self.selector))

        else:
            raise ValueError("Invalid booking tag: {}".format(name))
        return super(RequestLoader, self).load_item()
