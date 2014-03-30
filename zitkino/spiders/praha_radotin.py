# -*- coding: utf-8 -*-


from .base import BaseCinemaSpider
from ..parsers import TextTagParser, RequestParser


class Spider(BaseCinemaSpider):

    name = 'praha-radotin'
    calendar_url = (
        'http://www.praha16.eu/Mestska-cast/Kultura-skolstvi-volny-cas/'
        'Kino-Radotin-3D/area1526'
    )

    calendar_element = "//table[@class='tblKinoList']"

    calendar_showtime_element = ".//tr[not(th) and not(td[@colspan])]"
    calendar_showtime = [
        ('showtime_date', ".//td[2]/text()"),
        ('showtime_time', ".//td[3]/text()"),
        ('title', ".//td[4]//text()"),
        ('tags', ".//td[6]", TextTagParser()),
        ('tags', ".//td[7]", TextTagParser()),
        ('duration', ".//td[8]//text()"),
        ('csfd_id', "//a[contains(@href,'csfd.cz')]/@href"),
        ('prices', "./following-sibling::tr[1]/td[2]//text()"),
        ('booking', "./following-sibling::tr[1]/td[3]//a", RequestParser()),
    ]
