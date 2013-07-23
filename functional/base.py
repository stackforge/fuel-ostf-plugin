__author__ = 'ekonstantinov'
from unittest import TestCase
from functional.client import TestingAdapterClient
from functools import wraps


class EmptyResponseError(Exception):
    pass


class Response(object):
    """This is testing_adapter response object"""
    def __init__(self, response):
        self._parse_json(response.json)
        self.request = '{} {} \n with {}'\
            .format(response.request.method, response.request.url, response.request.body)

    def __getattr__(self, item):
        if item in self.test_sets or item in self._tests:
            return self.test_sets.get(item) or self._tests.get(item)

    def __getattribute__(self, item):
        if self.is_empty:
            raise EmptyResponseError()
        else:
            super(Response, self).__getattribute__(item)

    def __str__(self):
        return self.test_sets.__str__()

    @classmethod
    def set_test_name_mapping(cls, mapping):
        cls.test_name_mapping = mapping

    def _parse_json(self, json):
        if json == [{}]:
            self.is_empty = True
            return
        else:
            self.is_empty = False

        self.test_sets = {}
        self._tests = {}
        for testset in json:
            self._tests = self.test_sets[testset.pop('testset')] = testset
            self._tests['tests'] = {self._friendly_name(item.pop('id')): item for item in testset['tests']}

    def _friendly_name(self, name):
        return self.test_name_mapping.get(name, name)


class AdapterClientProxy(object):

    def __init__(self, url):
        self.client = TestingAdapterClient(url)

    def __getattr__(self, item):
        if item in TestingAdapterClient.__dict__:
            call = getattr(self.client, item)
            return self._decorate_call(call)

    def _decorate_call(self, call):
        @wraps(call)
        def inner(*args, **kwargs):
            r = call(*args, **kwargs)
            return Response(r)
        return inner




class SubsetException(Exception):
    pass


class BaseAdapterTest(TestCase):
    def _verify_json(self, assertions, json):
        """For the given json response verify that assertions are present
        """
        for item in json:
            for subitem in assertions:
                if item['testset'] == subitem['testset']:
                    for s in subitem['tests']:
                        if s['id'] not in (i['id'] for i in item['tests']):
                            raise AssertionError('{} not in:\n{}'.format(s['id'], [i['id'] for i in item['tests']]))

        def is_subset(item, subset):
            if type(item) != type(subset) and type(subset) not in (str, unicode):
                return False
            if type(subset) is list:

                return all(is_subset(i, s) for i in item for s in subset if i.get('id') == s.get('id') or s.get('id') == None)
            elif type(subset) is dict:
                try:
                    return all(is_subset(item[s], subset[s]) for s in subset)
                except AssertionError as e:
                    real, expected = e.message.split('|')
                    key = [x for x in subset if subset[x] == expected][0]
                    msg = '"{}" was found, when "{}" was excepted in key = "{}"'.format(real, expected, key)
                    raise SubsetException(msg)
            else:
                msg = '{item}|{subset}'.format(item=item, subset=subset)
                assert item == subset, msg
                return item == subset

        msg = '{subset}     IS NOT IN     {item}'.format(subset=assertions, item=json)
        try:
            self.assertTrue(is_subset(json, assertions), msg)
        except SubsetException as e:
            msg = '{}\nwith response:\n{}\nand assertion:\n{}'.format(e.message, json, assertions)
            raise AssertionError(msg)

