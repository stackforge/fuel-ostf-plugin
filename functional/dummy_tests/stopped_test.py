import time
import unittest


class dummy_tests_stopped(unittest.TestCase):

    def test_really_long(self):
        """This is long running tests
           Duration: 25sec
        """
        time.sleep(25)
        self.assertTrue(True)

    def test_one_no_so_long(self):
        """What i am doing here? You ask me????
        """
        time.sleep(5)
        self.assertFalse(1 == 2)

    def test_not_long_at_all(self):
        """You know.. for testing
            Duration: 1sec
        """
        self.assertTrue(True)

