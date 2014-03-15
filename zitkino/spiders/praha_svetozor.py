# -*- coding: utf-8 -*-


from .base import BaseCinemaSpider, Fields
from ..loaders import (ImageTagLoader, LinkTagLoader, TextTagLoader,
                       RequestLoader)


class Spider(BaseCinemaSpider):

    name = 'praha-svetozor'
    calendar_url = 'http://www.kinosvetozor.cz/cz/program/'
    calendar_next = ".//a[@class='next-week-link']/@href"

    calendar_showtime_element = ".//tr[td[@class='film']]"
    calendar_showtime = Fields([
        ('title',
         ".//td[@class='film']/a[contains(@href,'program/filmy')]/@title"
         "|.//td[@class='film']/a[contains(@href,'program/filmy')]/text()"),
        ('film_url', ".//td[@class='film']/a/@href"),
        ('showtime_time', ".//td[@class='cas']/text()"),
        ('showtime_date',
         "./ancestor::table[1]/preceding-sibling::h2[1]//strong/text()"),
        ('tags', ".//*[@class='cyklusArrow']/a", LinkTagLoader),
        ('tags', ".//*[@class='film-note']/img", ImageTagLoader),
        ('tags', "./ancestor::table[1]//th[1]", TextTagLoader),
    ])

    film = Fields([
        ('title', "//h1/text()"),
        ('csfd_id', "//a[contains(@href,'csfd.cz')]/@href"),
        ('imdb_id', "//a[contains(@href,'imdb.com')]/@href"),
        ('youtube_id', "//a[contains(@href,'youtube.com')]/@href"),
        ('info', "//*[@class='textGreyTwo']/text()"),
        ('description', "//*[@id='movieInfo']/text()"),
        ('poster_urls', "//img[@class='imgFilmDetail']/@src"),
    ])

    subcalendar_element = ".//table[@class='promitameTwo'][1]"
    subcalendar_showtime_element = ".//tr"
    subcalendar_showtime = Fields([
        ('title', "//h1/text()"),
        ('showtime_time', "./td[@class='cas']//text()"),
        ('showtime_date',
         "./td[@class='datum']//text()"
         "|./preceding-sibling::tr[1]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[2]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[3]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[4]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[5]/td[@class='datum']//text()"),
        ('price', "./td[@class='vstupne']//text()"),
        ('tags', ".//*[@class='cyklusArrow']/a", LinkTagLoader),
        ('tags', ".//*[@class='dvd']/img", ImageTagLoader),
        ('tags', ".//*[@class='poznamka']", TextTagLoader),
        ('tags', ".//*[@class='sal']", TextTagLoader),
        ('booking', "./td[@class='cas']//form", RequestLoader),
    ])
