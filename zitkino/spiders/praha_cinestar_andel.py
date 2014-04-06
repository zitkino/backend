# -*- coding: utf-8 -*-


from .base_cinestar import BaseCinestarCinemaSpider


class Spider(BaseCinestarCinemaSpider):

    name = 'praha-cinestar-andel'
    calendar_url = 'http://praha5.cinestar.cz/program_multikino.php'
