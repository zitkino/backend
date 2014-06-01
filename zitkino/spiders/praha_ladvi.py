# -*- coding: utf-8 -*-


from scrapy.selector import Selector

from .base import BaseCinemaSpider
from ..processors import DateRanges
from ..parsers import TagParser, SwitchParser


def create_dates_parser(*weekdays):
    def fn(parser_context):
        xpath = "//*[contains(./text(), 'Program')]//text()"
        response = parser_context.get('response')

        range_text = Selector(response).xpath(xpath).extract()[0]
        to_dates = DateRanges()
        dates = to_dates([range_text])

        for date in dates:
            if date.weekday() in weekdays:
                yield date
    return fn


class Spider(BaseCinemaSpider):

    name = 'praha-ladvi'
    calendar_url = 'http://www.kinoladvi.cz/program.htm'

    calendar_element = "//*[contains(., 'Program')]/ancestor::table[1]"
    calendar_showtime_element = (
        ".//tr[2]/following::tr//td[4]/following-sibling::td"
    )

    calendar_showtime = [
        ('title', "./ancestor::tr[1]//td[1]//text()"),
        ('tags', "./ancestor::tr[1]//td[2]", TagParser()),
        ('min_age_restriction', "./ancestor::tr[1]//td[3]//text()"),
        ('duration', "./ancestor::tr[1]//td[4]//text()"),
        ('showtime_time', ".//text()"),
        ('showtime_dates', ".", SwitchParser([
            ("./@bgcolor", r'#FFFF00', create_dates_parser(5, 6)),
            ("./@bgcolor", r'#FF00FF', create_dates_parser(0, 1, 2, 3, 4)),
            ("./@bgcolor", r'#00FF00', create_dates_parser(1)),
            ("./@bgcolor", r'#00FFFF', create_dates_parser(4)),
            ("./@bgcolor", r'#FF9900', create_dates_parser(0, 1, 2, 3, 5, 6)),
            ("./@bgcolor", r'#FF99FF', create_dates_parser(0, 2, 3, 4)),
            (".", None, create_dates_parser(0, 1, 2, 3, 4, 5, 6)),
        ])),
    ]
