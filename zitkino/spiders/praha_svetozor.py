# -*- coding: utf-8 -*-


from .base import BaseCinemaSpider
from ..loaders import ImageTagLoader, LinkTagLoader, TextTagLoader


class Spider(BaseCinemaSpider):

    name = 'praha-svetozor'
    allowed_domains = ['kinosvetozor.cz']
    start_urls = ['http://www.kinosvetozor.cz/cz/program/']

    calendar_next_link = ".//*[@class='next-week-link']/@href"

    calendar_showtime_element = ".//tr[td[@class='film']]"
    calendar_showtime = {
        'title': [
            ".//td[@class='film']/a[contains(@href,'program/filmy')]/@title",
            ".//td[@class='film']/a[contains(@href,'program/filmy')]/text()",
        ],
        'film_url': ".//td[@class='film']/a/@href",
        'showtime_time': ".//td[@class='cas']/text()",
        'showtime_date': [
            "./ancestor::table[1]/preceding-sibling::h2[1]//strong/text()"
        ],
    }
    calendar_showtime_tag_loaders = [
        (".//*[@class='cyklusArrow']/a", LinkTagLoader),
        (".//*[@class='film-note']/img", ImageTagLoader),
        ("./ancestor::table[1]//th[1]", TextTagLoader),
    ]

    film = {
        'title': "//h1/text()",
        'csfd_id': "//a[contains(@href,'csfd.cz')]/@href",
        'imdb_id': "//a[contains(@href,'imdb.com')]/@href",
        'youtube_id': "//a[contains(@href,'youtube.com')]/@href",
        'info': "//*[@class='textGreyTwo']/text()",
        'description': "//*[@id='movieInfo']/text()",
        'poster_urls': "//img[@class='imgFilmDetail']/@src",
    }
    film_tag_loaders = []

    subcalendar_element = ".//table[@class='promitameTwo'][1]"
    subcalendar_showtime_element = ".//tr"
    subcalendar_showtime = {
        'title': "//h1/text()",
        'showtime_time': "./td[@class='cas']//text()",
        'showtime_date': [
            "./td[@class='datum']//text()",
            "./preceding-sibling::tr[1]/td[@class='datum']//text()",
            "./preceding-sibling::tr[2]/td[@class='datum']//text()",
            "./preceding-sibling::tr[3]/td[@class='datum']//text()",
            "./preceding-sibling::tr[4]/td[@class='datum']//text()",
            "./preceding-sibling::tr[5]/td[@class='datum']//text()",
        ],
        'price': "./td[@class='vstupne']//text()",
    }
    subcalendar_showtime_tag_loaders = [
        (".//*[@class='cyklusArrow']/a", LinkTagLoader),
        (".//*[@class='dvd']/img", ImageTagLoader),
        (".//*[@class='poznamka']", TextTagLoader),
        (".//*[@class='sal']", TextTagLoader),
    ]
