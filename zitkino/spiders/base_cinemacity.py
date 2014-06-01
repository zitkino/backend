# -*- coding: utf-8 -*-


from datetime import timedelta

from ..utils import now
from .base import BaseCinemaSpider
from ..parsers import TagParser, LegendParser


class BaseCinemacityCinemaSpider(BaseCinemaSpider):

    location_id = ''

    calendar_showtime_element = (
        ".//a[contains(@class, 'presentationLink')]"
    )
    calendar_showtime = [
        ('title', "./ancestor::tr[1]//td[@class='featureName']//a/text()"),
        ('film_url', "./ancestor::tr[1]//td[@class='featureName']//a/@href"),
        ('min_age_restriction',
         "./ancestor::tr[1]//td[@class='rating']//text()"),
        ('tags', "./ancestor::tr[1]//td[3]", TagParser()),
        ('tags',
         "./ancestor::tr[1]//td[4][not(contains(., '---'))]", TagParser()),
        ('duration', "./ancestor::tr[1]//td[5]"),
        ('showtime_time', "./text()"),
        ('showtime_date', "//label[@class='date']//text()"),
    ]

    calendar_legends = {
        "//*[@class='footer']": LegendParser(stopwords=[
            ur'.*změna programu vyhrazena\.'
        ])
    }

    def row_xpath(label, include_label=False):
        xpath = (
            u"//*[@class='pre_label' and contains(., '{}')]"
            "//ancestor::*[contains(@class, 'feature_info_row')]"
        ).format(label)
        if include_label:
            xpath += "//text()"
        else:
            xpath += "//*[contains(@class, 'white')]//text()"
        return xpath

    film = [
        ('title', "//*[@class='feature_info_title']//text()"),
        ('title_original', row_xpath(u'Name')),
        ('info', row_xpath(u'Žánr', include_label=True)),
        ('duration', row_xpath(u'Délka')),
        ('release_date', row_xpath(u'Premiéra')),
        ('info', row_xpath(u'Režisér', include_label=True)),
        ('info', row_xpath(u'Hrají', include_label=True)),
        ('info', row_xpath(u'Země', include_label=True)),
        ('description',
         "//*[contains(@class, 'feature_info_synopsis')]//text()"),
        ('poster_urls', "//*[@class='poster_holder']//img/@src"),
    ]

    def start_requests(self):
        day = now().date()
        url_template = ('http://www.cinemacity.cz/scheduleInfo?'
                        'locationId={location_id}&date={date:%d/%m/%Y}')

        for i in xrange(self.calendar_next_max_depth):
            url = url_template.format(location_id=self.location_id, date=day)
            yield self.make_requests_from_url(url)
            day += timedelta(days=1)
