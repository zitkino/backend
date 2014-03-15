# -*- coding: utf-8 -*-


from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Compose, MapCompose

from .items import Showtime, Film, Tag
from .utils import NormalizeSpace, Unique
from .coercing import (coerce_absolute_url, coerce_tag_code, coerce_csfd_id,
                       coerce_imdb_id, coerce_youtube_id, coerce_price)


class FilmLoader(ItemLoader):

    default_item_class = Film
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    film_url_in = MapCompose(coerce_absolute_url)
    csfd_id_in = MapCompose(coerce_csfd_id)
    imdb_id_in = MapCompose(coerce_imdb_id)
    youtube_id_in = MapCompose(coerce_youtube_id)
    year_in = MapCompose(int)
    duration_in = MapCompose(int)
    poster_urls_in = MapCompose(coerce_absolute_url)

    poster_urls_out = Unique()


class ShowtimeLoader(FilmLoader):

    default_item_class = Showtime
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    calendar_url_in = MapCompose(coerce_absolute_url)
    price_in = MapCompose(coerce_price)

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

    code_in = MapCompose(coerce_tag_code)
    url_in = MapCompose(coerce_absolute_url)
