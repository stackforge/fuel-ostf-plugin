import logging
from nose import case
import os
import traceback
import re

log = logging.getLogger(__name__)


def get_exc_message(exception_value):
    """
    @exception_value - Exception type object
    """
    _exc_long = str(exception_value)
    if isinstance(_exc_long, basestring):
        return _exc_long.split('\n')[0]
    return u""


def get_description(test_obj):
    if isinstance(test_obj, case.Test):
        docstring = test_obj.shortDescription()

        if docstring:
            duration_pattern = r'Duration:.?(?P<duration>.+)'
            duration_matcher = re.search(duration_pattern, docstring)
            log.info('DOCSTRING %s %s' % (docstring, duration_matcher))
            if duration_matcher:
                duration = duration_matcher.group(1)
                docstring = docstring[:duration_matcher.start()]
            else:
                duration = None
            docstring = docstring.split('\n')
            name = docstring.pop(0)
            description = u'\n'.join(docstring) if docstring else u""

            return name, description, duration
    return u"", u"", u""


def config_name_generator(test_path, test_set, external_id):
    log.info('CALLED WITH %s' % locals())
    try:
        module_path = os.path.dirname(__import__(test_path).__file__)
        log.info('MODULE PATH IS %s' % module_path)
        return os.path.join(
            module_path,
            'test_{0}_{1}.conf'.format(test_set, external_id))
    except Exception, e:
        log.info('ERROR IN PARSING CONFIG PATH %s' % e)
        current_path = os.path.join(os.path.realpath('.'), test_path)
        dir_path = os.path.dirname(current_path)
        return os.path.join(
            dir_path,
            'test_{0}_{1}.conf'.format(test_set, external_id))


def modify_test_name_for_nose(test_path):
    test_module, test_class, test_method = test_path.rsplit('.', 2)
    return '{0}:{1}.{2}'.format(test_module, test_class, test_method)


def format_exception(exc_info):
    ec, ev, tb = exc_info

    # formatError() may have turned our exception object into a string, and
    # Python 3's traceback.format_exception() doesn't take kindly to that (it
    # expects an actual exception object).  So we work around it, by doing the
    # work ourselves if ev is a string.
    if isinstance(ev, basestring):
        tb_data = ''.join(traceback.format_tb(tb))
        return tb_data + ev
    else:
        return ''.join(traceback.format_exception(*exc_info))


def format_failure_message(message):
    matcher = re.search(
        r'^[a-zA-Z]+\s?(\d+)\s?[a-zA-Z]+\s?[\.:]\s?(.+)',
        message)
    if matcher:
        step, msg = matcher.groups()
        return step, msg
    return '', message

