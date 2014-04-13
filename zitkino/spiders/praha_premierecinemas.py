# -*- coding: utf-8 -*-


from .base_premierecinemas import BasePremierecinemasCinemaSpider


class Spider(BasePremierecinemasCinemaSpider):

    name = 'praha-premierecinemas'
    calendar_url = 'http://www.premierecinemas.cz/'
