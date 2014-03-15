# -*- coding: utf-8 -*-


import re
from os import path
from decimal import Decimal

from .utils import absolute_url


def coerce_tag_code(value):
    value = path.splitext(path.basename(value))[0]
    return value.upper().replace('_', '-')


def coerce_price(value):
    return Decimal(re.sub(r'[^\d\.\,]', '', value).replace(',', '.'))


def coerce_absolute_url(value, loader_context):
    response = loader_context.get('response')
    return absolute_url(value, response)


def coerce_csfd_id(value):
    if re.match(r'\d+$', value):
        return value
    return re.search(r'/film/(\d+)', value).group(1)


def coerce_imdb_id(value):
    if re.match(r'\d+$', value):
        return value
    return re.search(r'/title/tt(\d+)', value).group(1)


def coerce_youtube_id(value):
    if re.search(r'youtube\.com/v/', value):
        return re.search(r'youtube\.com/v/(.+)$', value).group(1)
    raise NotImplementedError
