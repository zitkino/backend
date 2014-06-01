# -*- coding: utf-8 -*-


from .base import BaseCinemaSpider
from ..parsers import TagParser, RequestParser


class Spider(BaseCinemaSpider):

    name = 'praha-svetozor'
    calendar_url = 'http://www.kinosvetozor.cz/cz/program/'
    calendar_next = ".//a[@class='next-week-link']/@href"

    calendar_showtime_element = ".//tr[td[@class='film']]"
    calendar_showtime = [
        ('title',
         ".//td[@class='film']/a[contains(@href,'program/filmy')]/@title"
         "|.//td[@class='film']/a[contains(@href,'program/filmy')]/text()"),
        ('film_url', ".//td[@class='film']/a/@href"),
        ('showtime_time', ".//td[@class='cas']/text()"),
        ('showtime_date',
         "./ancestor::table[1]/preceding-sibling::h2[1]//strong/text()"),
        ('tags', ".//*[@class='cyklusArrow']/a", TagParser()),
        ('tags', ".//*[@class='film-note']/img", TagParser()),
        ('tags', "./ancestor::table[1]//th[1]", TagParser()),
    ]

    film = [
        ('title', "//h1/text()"),
        ('info', "//*[@class='textGreyTwo']/text()"),
        ('description', "//*[@id='movieInfo']/text()"),
        ('poster_urls', "//img[@class='imgFilmDetail']/@src"),
    ]

    subcalendar_element = ".//table[@class='promitameTwo'][1]"
    subcalendar_showtime_element = ".//tr"
    subcalendar_showtime = [
        ('title', "//h1/text()"),
        ('showtime_time', "./td[@class='cas']//text()"),
        ('showtime_date',
         "./td[@class='datum']//text()"
         "|./preceding-sibling::tr[1]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[2]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[3]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[4]/td[@class='datum']//text()"
         "|./preceding-sibling::tr[5]/td[@class='datum']//text()"),
        ('prices', "./td[@class='vstupne']//text()"),
        ('tags', ".//*[@class='cyklusArrow']/a", TagParser()),
        ('tags', ".//*[@class='dvd']/img", TagParser()),
        ('tags', ".//*[@class='poznamka']", TagParser()),
        ('tags', ".//*[@class='sal']", TagParser()),
        ('booking', "./td[@class='cas']//form", RequestParser()),
    ]
