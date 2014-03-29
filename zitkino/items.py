# -*- coding: utf-8 -*-


from scrapy.item import Item, Field


class Tag(Item):
    name = Field()
    code = Field()
    url = Field()


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


class Showtime(Film):
    showtime_day = Field()
    showtime_month = Field()
    showtime_date = Field()
    showtime_time = Field()
    showtime_year = Field()
    showtime_datetime = Field()
    calendar_url = Field()
    prices = Field()
    tags = Field()
    booking = Field()
