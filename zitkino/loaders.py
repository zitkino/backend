# -*- coding: utf-8 -*-


from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, MapCompose

from .items import Showtime, Film, Tag
from .processors import (NormalizeSpace, Unique, AbsolutizeUrls, ToCsfdIds,
                         ToPrices, ToImdbIds, ToYoutubeIds, ToTagCodes)


class FilmLoader(ItemLoader):

    default_item_class = Film
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    film_url_in = AbsolutizeUrls()
    csfd_id_in = ToCsfdIds()
    imdb_id_in = ToImdbIds()
    youtube_id_in = ToYoutubeIds()
    year_in = MapCompose(int)
    duration_in = MapCompose(int)
    poster_urls_in = AbsolutizeUrls()

    poster_urls_out = Unique()


class ShowtimeLoader(FilmLoader):

    default_item_class = Showtime
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    calendar_url_in = AbsolutizeUrls()
    price_in = ToPrices()

    tags_out = Unique()

    def add_attrs(self, attr_queries):
        for attr, queries in attr_queries.items():
            if isinstance(queries, basestring):
                queries = [queries]
            for query in queries:
                self.add_xpath(attr, query)

    def add_tags(self, tag_loaders):
        for queries, cls in tag_loaders:
            for result in self.selector.xpath(queries):
                l = cls(selector=result, response=self.context.get('response'))
                self.add_value('tags', l.load_item())


class TagLoader(ItemLoader):

    default_item_class = Tag
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    code_in = ToTagCodes()
    url_in = AbsolutizeUrls()


class TextTagLoader(TagLoader):
    """Ready-made text tag loader."""

    def __init__(self, *args, **kwargs):
        super(TextTagLoader, self).__init__(*args, **kwargs)
        self.add_xpath('name', "./text()")


class LinkTagLoader(TagLoader):
    """Ready-made link tag loader."""

    def __init__(self, *args, **kwargs):
        super(LinkTagLoader, self).__init__(*args, **kwargs)
        self.add_xpath('name', "./@title")
        self.add_xpath('code', "./text()")
        self.add_xpath('url', "./@href")


class ImageTagLoader(TagLoader):
    """Ready-made image tag loader."""

    def __init__(self, *args, **kwargs):
        super(ImageTagLoader, self).__init__(*args, **kwargs)
        self.add_xpath('name', "./@title")
        self.add_xpath('name', "./@alt")
        self.add_xpath('code', "./@src")
