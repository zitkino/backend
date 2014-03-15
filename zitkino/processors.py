# -*- coding: utf-8 -*-


import re
import decimal
from os import path

from .utils import absolutize_url


class NormalizeSpace(object):

    _whitespace_re = re.compile(
        ur'[{0}\s\xa0]+'.format(
            re.escape(''.join(map(unichr, range(0, 32) + range(127, 160))))
        )
    )

    def __call__(self, values):
        for value in values:
            try:
                yield self._whitespace_re.sub(' ', value).strip()
            except TypeError:
                yield value


class ToTagCodes(object):

    def __call__(self, values):
        for value in values:
            value = path.splitext(path.basename(value))[0]
            yield value.upper().replace('_', '-')


class ToNumbers(object):

    def __init__(self, cls=int):
        self.cls = cls

    def __call__(self, values):
        for value in values:
            if isinstance(value, basestring):
                value = re.sub(r'[^\d\.\,]', '', value).replace(',', '.')
            try:
                yield self.cls(value)
            except (ValueError, TypeError, decimal.InvalidOperation):
                pass  # skip it


class AbsolutizeUrls(object):

    def __call__(self, values, loader_context):
        for value in values:
            response = loader_context.get('response')
            yield absolutize_url(value, response)


class ToCsfdIds(object):

    def __call__(self, values):
        for value in values:
            if re.match(r'\d+$', value):
                yield value
            else:
                yield re.search(r'/film/(\d+)', value).group(1)


class ToImdbIds(object):

    def __call__(self, values):
        for value in values:
            if re.match(r'\d+$', value):
                yield value
            else:
                yield re.search(r'/title/tt(\d+)', value).group(1)


class ToYoutubeIds(object):

    def __call__(self, values):
        for value in values:
            if re.search(r'youtube\.com/v/', value):
                yield re.search(r'youtube\.com/v/(.+)$', value).group(1)
            else:
                raise NotImplementedError


class Unique(object):

    def __call__(self, values):
        return list(frozenset(v for v in values if v))
