# -*- coding: utf-8 -*-


from .base import BaseCinemaSpider
from ..parsers import (TabLabelParser, TextTagParser, ImageTagParser,
                       RequestParser, TextLegendParser)


class BasePremierecinemasCinemaSpider(BaseCinemaSpider):

    calendar_showtime_element = (
        ".//td[ancestor::tr[1][td[@class='ps-program-table-movie']] "
        "and count(preceding-sibling::td) >= 3]"
    )
    calendar_showtime = [
        ('title', "./ancestor::tr[1]//td[1]//a[1]/text()"),
        ('showtime_time', ".//text()"),
        ('showtime_date',
         "./ancestor::div[contains(@id, 'tab')]", TabLabelParser()),
        ('min_age_restriction', "./ancestor::tr[1]//td[2]//text()"),
        ('film_url', "./ancestor::tr[1]//td[1]//a[1]/@href"),
        ('tags', "./ancestor::tr[1]//td[3]", TextTagParser()),
        ('tags', "./ancestor::tr[1]//td[1]//img", ImageTagParser()),
    ]
    calendar_legends = {
        "//*[@class='ps-program-help-info-main']": TextLegendParser(
            mapping_sep='=', stopwords=[
                ur'.*informace.*', ur'.*změna programu.*'
            ]
        )
    }

    film = [
        ('title', "//h1//text()"),
        ('title_original', "//*[@class='originalni-nazev']//text()"),
        ('info', "//*[@class='movie-zanr']//text()"),
        ('info', "//*[@class='movie-info']//text()"),
        ('description', "//*[@class='film-bottom-left']//p//text()"),
        ('poster_urls', "//*[@class='photogal-container']//img/@src"),
    ]

    subcalendar_element = ".//table[@class='ps-program-table-detail-filmu']"
    subcalendar_showtime_element = ".//*[@class='pc-cas-detail-filmu']//a"
    subcalendar_showtime = [
        ('title', "//h1//text()"),
        ('showtime_time', ".//text()"),
        ('showtime_date', "./ancestor::tr[1]//td[1]//text()"),
        ('min_age_restriction', "./ancestor::tr[1]//td[2]//text()"),
        ('tags', "./ancestor::tr[1]//td[3]", TextTagParser()),
        ('tags', "./ancestor::tr[1]//td[4]", TextTagParser()),
        ('tags', "./ancestor::tr[1]//td[4]//img", ImageTagParser()),
        ('booking', ".", RequestParser()),
    ]
