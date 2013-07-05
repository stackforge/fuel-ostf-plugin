
import time
import httplib
import unittest


class Dummy_test(unittest.TestCase):

    def test_fast_pass(self):
        self.assertTrue(True)

    def test_long_pass(self):
        time.sleep(5)
        self.assertTrue(True)

    def test_fast_fail(self):
        self.assertTrue(False)

    def test_fast_error(self):
        conn = httplib.HTTPSConnection('random.random/random')
        conn.request("GET", "/random.aspx")