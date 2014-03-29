# -*- coding: utf-8 -*-


import string

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import (TakeFirst, Compose, Join,
                                             MapCompose)

from .items import Showtime, Film, Tag, Request
from .processors import (NormalizeSpace, Unique, AbsolutizeUrls, ToCsfdIds,
                         ToNumbers, ToImdbIds, ToYoutubeIds, ToTagCodes,
                         ToPrices)


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
    info_in = Join(' ')
    description_in = Join(' ')

    poster_urls_out = Unique()


class ShowtimeLoader(FilmLoader):

    default_item_class = Showtime
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    calendar_url_in = AbsolutizeUrls()
    prices_in = ToPrices()

    tags_out = Unique()
    prices_out = Unique()


class TagLoader(ItemLoader):

    default_item_class = Tag
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    code_in = ToTagCodes()
    url_in = AbsolutizeUrls()


class RequestLoader(ItemLoader):

    default_item_class = Request
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    url_in = AbsolutizeUrls()
    method_in = MapCompose(string.upper)
