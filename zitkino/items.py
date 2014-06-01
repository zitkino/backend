# -*- coding: utf-8 -*-


from pprint import pformat

from scrapy.item import Item, Field


class Tag(Item):
    name = Field()
    code = Field()
    url = Field()
    type = Field()


class Request(Item):
    url = Field()
    method = Field()
    data = Field()


class Film(Item):
    title = Field()
    title_original = Field()
    film_url = Field()
    csfd_id = Field()
    imdb_id = Field()
    youtube_id = Field()
    year = Field()
    info = Field()
    description = Field()
    duration = Field()
    poster_urls = Field()
    release_date = Field()


class Showtime(Film):
    showtime_date = Field()
    showtime_dates = Field()
    showtime_time = Field()
    showtime_times = Field()
    calendar_url = Field()
    calendar_html = Field()
    prices = Field()
    tags = Field()
    booking = Field()
    min_age_restriction = Field()

    def __repr__(self):
        return pformat(dict(self, calendar_html='...'))
