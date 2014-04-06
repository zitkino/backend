# -*- coding: utf-8 -*-


from .base_cinestar import BaseCinestarCinemaSpider


class Spider(BaseCinestarCinemaSpider):

    name = 'praha-cinestar-cm'
    calendar_url = 'http://praha9.cinestar.cz/program_multikino.php'
