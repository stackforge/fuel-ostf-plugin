import time
import httplib
import unittest


class Dummy_test(unittest.TestCase):
    """Class docstring is required?
    """

    def test_fast_pass(self):
        """Ths tests fast pass OK?
        """
        self.assertTrue(True)

    def test_long_pass(self):
        """Will sleep 5 sec
        """
        time.sleep(1)
        self.assertTrue(True)

    def test_fast_fail(self):
        """Fust fail
        """
        self.assertTrue(False, msg='Something goes wroooong')

    def test_fast_error(self):
        """And fast error
        """
        conn = httplib.HTTPSConnection('random.random/random')
        conn.request("GET", "/random.aspx")

    def test_fail_with_step(self):
        self.fail('Step 3 Failed: MEssaasasas')