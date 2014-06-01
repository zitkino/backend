# -*- coding: utf-8 -*-


from ..javascript import JavaScript
from ..parsers import TagParser, RequestParser
from .base import BaseCinemaSpider, FieldDefinitions


class BaseCinestarCinemaSpider(BaseCinemaSpider):

    calendar_next = ".//form[@id='day-chooser']"

    calendar_showtime_element = (
        ".//td[contains(@class, 'time') and contains(@class, 'active')]"
    )
    calendar_showtime = [
        ('title', "./ancestor::tr[1]//td[@class='name']//a/text()"),
        ('title', "./ancestor::tr[1]//td[@class='name']//noscript/text()"),
        ('showtime_time', ".//noscript/text()"),
        ('showtime_time', "./text()"),
        ('showtime_date',
         "//form[@id='day-chooser']//option[@selected]/text()"),
        ('tags',
         "./ancestor::tr[1]//td[@class='hall']",
         TagParser()),
        ('tags',
         ("./ancestor::tr[1]//td[@class='age'][1]"
          "//span[contains(@style, 'normal')]"),
         TagParser()),
        ('tags',
         "./ancestor::table[1]/preceding-sibling::*[.//h3]//h3",
         TagParser()),
        ('tags',
         "./ancestor::table[1]/preceding-sibling::*[.//h3]//h3//img",
         TagParser()),
        ('min_age_restriction',
         "./ancestor::tr[1]//td[@class='age'][2]//text()"),
    ]

    calendar_showtime_scripted = [
        ('film_url', "./ancestor::tr[1]//td[@class='name']//script/text()"),
        ('booking', ".//script/text()", RequestParser()),
    ]

    film = [
        ('title', "//*[contains(@class,'film-detail')]/h2/text()"),
        ('info', "//*[@class='meta']//text()"),
        ('description',
         "//*[contains(@class,'film-detail')]//p[1]/text()"),
        ('poster_urls', "//*[@id='images']//img/@src"),
    ]

    script_base = "//script[contains(./text(), 'function zobrazOdkaz')]/text()"
    websale_url_hall = "//input[@id='websale_url_hall']/@value"

    def _get_link_selector(self, selector, xpath):
        js = JavaScript(selector=selector)
        js.append_xpath(self.script_base)
        js.append_xpath(xpath)

        websale_url_hall = selector.xpath(self.websale_url_hall).extract()[0]
        js.code = js.code.replace(
            '$("#websale_url_hall").val()',
            '"{}"'.format(websale_url_hall)
        )
        return js.capture_as_selector().xpath('.//a/@href')

    def parse_calendar_showtime(self, loader, response):
        fields = FieldDefinitions(self.calendar_showtime_scripted)
        selector = loader.selector

        for field_name, xpath, parser in fields:
            for result in self._get_link_selector(selector, xpath):
                if parser is not None:
                    for value in parser(result, response):
                        loader.add_value(field_name, value)
                else:
                    loader.add_value(field_name, result.extract())

        super(BaseCinestarCinemaSpider, self).parse_calendar_showtime(
            loader,
            response
        )
