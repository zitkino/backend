# -*- coding: utf-8 -*-


import urllib
import urlparse
from itertools import combinations, product, chain

import lxml.html
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest as BaseFormRequest

from .utils import absolutize_url, tag_name


class FormFiller(object):

    def __init__(self, element):
        self.element = element

    def _get_opts(self, name, values, is_multi):
        if is_multi:
            # multiple options allowed
            for i in xrange(len(values) + 1):
                for options in combinations(values, i):
                    yield list((name, option) for option in options)
        else:
            # single option allowed
            for value in values:
                yield [(name, value)]

    def _get_selects(self, selects, is_multi, exclude=None):
        exclude = exclude or []

        for select in selects:
            if select.name in exclude:
                continue
            yield self._get_opts(select.name, select.value_options, is_multi)

    def _get_group(self, elements, is_multi, exclude=None):
        exclude = exclude or []

        groups = {}
        for element in elements:
            groups.setdefault(element.name, [])
            groups[element.name].append(element)

        for name, group in groups.items():
            if name in exclude:
                continue
            values = [element.get('value') for element in group]
            yield self._get_opts(name, values, is_multi)

    def possible_fillings(self, formdata=None):
        data = dict(formdata or {})
        exclude = data.keys()

        xpath = self.element.xpath
        selects_multi = xpath(".//select[@name and @multiple]")
        selects = xpath(".//select[@name and not(@multiple)]")
        checkboxes = xpath(".//input[@name and @value and @type = 'checkbox']")
        radios = xpath(".//input[@name and @value and @type = 'radio']")

        options = []
        options.extend(self._get_selects(selects_multi, True, exclude))
        options.extend(self._get_selects(selects, False, exclude))
        options.extend(self._get_group(checkboxes, True, exclude))
        options.extend(self._get_group(radios, False, exclude))

        for item_lists in product(*options):
            items = formdata.copy()
            for key, value in chain(*item_lists):
                items.setdefault(key, [])
                items[key].append(value)
            yield items


class FormRequest(BaseFormRequest):

    def __init__(self, url, *args, **kwargs):
        # implementation of https://github.com/scrapy/scrapy/pull/412/
        formdata = kwargs.get('formdata', None)
        is_get = kwargs.get('method') == 'GET'
        overwrite = kwargs.pop('overwrite', True)

        if formdata and is_get and overwrite:
            overwritten = dict(formdata).keys()
            urlparts = list(urlparse.urlsplit(url))
            params = {
                k: v for (k, v) in urlparse.parse_qs(urlparts[3]).iteritems()
                if k not in overwritten
            }
            urlparts[3] = urllib.urlencode(params, True)
            url = urlparse.urlunsplit(urlparts)

        super(FormRequest, self).__init__(url, *args, **kwargs)


class Crawler(object):

    def __init__(self, xpath_or_selector, formfilling=False, max_depth=10):
        if isinstance(xpath_or_selector, Selector):
            self.selector = xpath_or_selector
            self.xpath = None
        else:
            self.selector = None
            self.xpath = xpath_or_selector

        self.formfilling = formfilling
        self.max_depth = max_depth

    def _extract_url(self, selector, response):
        for url in selector.extract():
            yield absolutize_url(url, response)

    def _extract(self, selector, response, formdata=None):
        formdata = formdata or {}
        forms = [sel.extract() for sel in Selector(response).xpath('//form')]

        for sel in selector:
            tag = tag_name(sel)

            if not tag:
                url = self._extract_url(sel, response)
                yield Request(url)

            elif tag == 'a':
                for url in self._extract_url(sel.xpath("./@href"), response):
                    yield Request(url, response)

            elif tag == 'form':
                form = sel.extract()
                no = forms.index(form)

                if self.formfilling:
                    filler = FormFiller(
                        lxml.html.fromstring(form)
                    )
                    for filling in filler.possible_fillings(formdata):
                        yield FormRequest.from_response(
                            response, formnumber=no, formdata=filling
                        )
                else:
                    yield FormRequest.from_response(
                        response, formnumber=no, formdata=formdata
                    )

            else:
                raise ValueError("Invalid form/link tag: {}".format(tag))

    def requests(self, response, formdata=None, callback=None):
        level = response.meta.get('level', 0)
        if level > self.max_depth:
            return

        if self.selector:
            selector = self.selector.xpath('.')
        else:
            selector = Selector(response).xpath(self.xpath)

        for request in self._extract(selector, response, formdata):
            yield request.replace(
                callback=callback,
                meta={'level': level + 1}
            )
