# -*- coding: utf-8 -*-


import string

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import (TakeFirst, Compose, Join,
                                             MapCompose)

from .items import Showtime, Film, Tag, Request
from .processors import (NormalizeSpace, Unique, AbsolutizeUrls, CsfdIds,
                         Numbers, ImdbIds, YoutubeIds, TagCodes,
                         Prices, Dates, Times)


class FilmLoader(ItemLoader):

    default_item_class = Film
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    film_url_in = AbsolutizeUrls()
    csfd_id_in = CsfdIds()
    imdb_id_in = ImdbIds()
    youtube_id_in = YoutubeIds()
    year_in = Numbers()
    duration_in = Numbers()
    poster_urls_in = AbsolutizeUrls()
    release_date_in = Compose(NormalizeSpace(), Dates())

    poster_urls_out = Unique()
    info_out = Compose(NormalizeSpace(), Join(' '))
    description_out = Compose(NormalizeSpace(), Join(' '))


class ShowtimeLoader(FilmLoader):

    default_item_class = Showtime
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    showtime_date_in = Compose(NormalizeSpace(), Dates())
    showtime_dates_in = Compose(NormalizeSpace(), Dates())
    showtime_time_in = Compose(NormalizeSpace(), Times())
    showtime_times_in = Compose(NormalizeSpace(), Times())
    calendar_url_in = AbsolutizeUrls()
    prices_in = Prices()
    min_age_restriction_in = Numbers()

    showtime_dates_out = Unique()
    showtime_times_out = Unique()
    tags_out = Unique()
    prices_out = Unique()


class TagLoader(ItemLoader):

    default_item_class = Tag
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    code_in = TagCodes()
    url_in = AbsolutizeUrls()


class RequestLoader(ItemLoader):

    default_item_class = Request
    default_output_processor = Compose(NormalizeSpace(), TakeFirst())

    url_in = AbsolutizeUrls()
    method_in = MapCompose(string.upper)
