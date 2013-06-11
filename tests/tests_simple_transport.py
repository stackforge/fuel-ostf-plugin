import unittest2
from core.transport import simple


class TestSimpleTransport(unittest2.TestCase):

    def test_redis_saving(self):
        service_path = '/home/dshulyak/projects/ceilometer'
        test_id = 'ceilometer:1'
