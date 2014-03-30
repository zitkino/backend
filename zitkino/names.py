# -*- coding: utf-8 -*-


class BaseNames(object):

    _names = ()
    _replace_format = "{}"

    def items(self):
        return [(name, self[name]) for name in self._names]

    def __getitem__(self, name):
        raise NotImplementedError

    def parse(self, value):
        if not isinstance(value, basestring):
            raise TypeError(value)
        for name, number in self.items():
            if name in value:
                return number
        raise ValueError(value)


class MonthNames(BaseNames):

    _names = (
        u'leden', u'únor', u'březen', u'duben',
        u'květen', u'červen', u'červenec', u'srpen',
        u'září', u'říjen', u'listopad', u'prosinec',
        u'ledna', u'února', u'března', u'dubna',
        u'května', u'června', u'července', u'srpna',
        u'září', u'října', u'listopadu', u'prosince',
    )

    def __getitem__(self, name):
        return (self._names.index(name) % 12) + 1

    def replace(self, value):
        if not isinstance(value, basestring):
            raise TypeError(value)
        for name, number in self.items():
            value = value.replace(name, "{}.".format(number))
        return value


class WeekdayNames(BaseNames):

    _names = (
        u'pondělí', u'úterý', u'středa', u'čtvrtek',
        u'pátek', u'sobota', u'neděle',
        u'po', u'út', u'st', u'čt',
        u'pá', u'so', u'ne',
    )

    def __getitem__(self, name):
        return (self._names.index(name) % 7) + 1
