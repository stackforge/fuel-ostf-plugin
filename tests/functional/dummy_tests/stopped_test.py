import time
import unittest


class dummy_tests_stopped(unittest.TestCase):
    def test_really_long(self):
        time.sleep(25)
        self.assertTrue(True)