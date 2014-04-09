# -*- coding: utf-8 -*-


import re
import decimal
from os import path
from datetime import datetime, date, time, timedelta

from .names import MonthNames
from .utils import absolutize_url, now


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


class TagCodes(object):

    def __call__(self, values):
        for value in values:
            if value.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
                value = path.splitext(path.basename(value))[0]
                value = value.upper().replace('_', '-')

            if value and value.upper() == value and len(value) < 5:
                yield value


class Numbers(object):

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


class Prices(Numbers):

    split_re = re.compile(r'/')

    def __init__(self):
        super(Prices, self).__init__(decimal.Decimal)

    def __call__(self, multivalues):
        for multivalue in multivalues:
            values = self.split_re.split(multivalue)
            for value in super(Prices, self).__call__(values):
                yield value


class AbsolutizeUrls(object):

    def __call__(self, values, loader_context):
        for value in values:
            if value:
                response = loader_context.get('response')
                yield absolutize_url(value, response)


class CsfdIds(object):

    def __call__(self, values):
        for value in values:
            if re.match(r'\d+$', value):
                yield value
            else:
                match = re.search(r'/film/(\d+)', value)
                if match:
                    yield match.group(1)


class ImdbIds(object):

    def __call__(self, values):
        for value in values:
            if re.match(r'\d+$', value):
                yield value
            else:
                yield re.search(r'/title/tt(\d+)', value).group(1)


class YoutubeIds(object):

    def __call__(self, values):
        for value in values:
            if re.search(r'youtube\.com/v/', value):
                yield re.search(r'youtube\.com/v/(.+)$', value).group(1)

            if re.search(r'youtube\.com/embed/', value):
                match = re.search(r'youtube\.com/embed/([^\?\&\'\"]+)', value)
                yield match.group(1)

            else:
                raise NotImplementedError


class Unique(object):

    def __call__(self, values):
        return list(frozenset(v for v in values if v))


class Months(Numbers):

    months = MonthNames()

    def __init__(self):
        super(Months, self).__init__()

    def __call__(self, values):
        months = []
        for value in values:
            try:
                value = self.months.parse(value)
            except (TypeError, ValueError):
                pass
            months.append(value)
        return super(Months, self).__call__(months)


class Dates(object):

    formats = (
        '%d.%m.%Y',
        '%d.%m.%y',
        '%d/%m/%Y',
        '%d/%m/%y',
        '%d.%m.',
        '%d/%m',
    )

    months = MonthNames()

    def __init__(self, year=None):
        self.year = year or now().year

    def _date_string(self, value):
        value = self.months.replace(value)
        return re.sub(r'[^\d\.\/]', '', value)

    def __call__(self, values):
        for value in values:
            if isinstance(value, date):
                yield value
                continue
            if isinstance(value, datetime):
                yield value.date()
                continue

            value = self._date_string(value)
            for fmt in self.formats:
                try:
                    dt = datetime.strptime(value, fmt)
                except ValueError:
                    pass
                else:
                    if dt.year <= 1900:
                        dt = dt.replace(year=self.year)
                    yield dt.date()
                    break


class DateRanges(object):

    def _range(self, start, end):
        d = start
        yield d
        while d != end:
            d += timedelta(days=1)
            yield d

    def __call__(self, values):
        to_dates = Dates(year=1)

        for value in values:
            start, end = list(to_dates(value.split('-')))

            if end.year <= 1900:
                end = end.replace(year=now().year)
            if start.year <= 1900:
                start = start.replace(year=end.year)

            for d in self._range(start, end):
                yield d


class Times(object):

    formats = (
        '%H:%M:%S',
        '%H:%M',
        '%H.%M',
    )

    def _time_string(self, value):
        return re.sub(r'[^\d\.\:]', '', value)

    def __call__(self, values):
        for value in values:
            if isinstance(value, time):
                yield value
                continue
            if isinstance(value, datetime):
                yield value.time()
                continue

            value = self._time_string(value)
            for fmt in self.formats:
                try:
                    dt = datetime.strptime(value, fmt)
                except ValueError:
                    pass
                else:
                    yield dt.time()
                    break
