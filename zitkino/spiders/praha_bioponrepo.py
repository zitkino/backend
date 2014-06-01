# -*- coding: utf-8 -*-


from datetime import date

from ..parsers import TagParser
from .base import BaseCinemaSpider


class Spider(BaseCinemaSpider):

    name = 'praha-bioponrepo'
    calendar_url = 'http://www.bio-ponrepo.cz/program.html'
    calendar_next = ".//*[@class='programme']/form"

    def iter_calendar_next_formdata(self):
        year = date.today().year
        formdata = {
            'filterFor': 'all',
            'filterAction': '2',  # -- film --
            'filterDay': '0',  # -- vše --
        }
        yield dict(filterYear=str(year), **formdata)
        yield dict(filterYear=str(year + 1), **formdata)

    calendar_showtime_element = ".//*[@class='programme']//tr[th]"
    calendar_showtime = [
        ('title', ".//a/@title|.//a/text()"),
        ('film_url', ".//a/@href"),
        ('showtime_time', ".//td[1]//text()"),
        ('showtime_date', ".//th[2]//text()"),
        ('tags', "./following-sibling::tr[1]//td[3]//a", TagParser()),
        ('info', "./following-sibling::tr[1]//td[3]//text()"),
    ]

    film = [
        ('title', "//*[@class='film-detail']/text()"),
        ('info',
         "//*[@class='film-detail']/ancestor::*[@class='container']"
         "//text()[following::img[@class='film-picture'] and "
         "preceding::*[@class='film-detail']]"),
        ('description',
         "//*[@class='film-detail']/ancestor::*[@class='container']"
         "//text()[preceding::img[@class='film-picture']]"),
        ('poster_urls', "//img[@class='film-picture']/@src"),
    ]
