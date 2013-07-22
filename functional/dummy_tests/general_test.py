import time
import httplib
import unittest


class Dummy_test(unittest.TestCase):
    """Class docstring is required?
    """

    def test_fast_pass(self):
        """fast pass test
        This is a simple always pass test
        duration: 1 sec
        """
        self.assertTrue(True)

    def test_long_pass(self):
        """Will sleep 15 sec
        This is a simple test
        it will run for 15 sec
        duration: 15 sec
        """
        time.sleep(5)
        self.assertTrue(True)

    def test_fast_fail(self):
        """Fast fail
        """
        self.assertTrue(False, msg='Something goes wroooong')

    def test_fast_error(self):
        """And fast error
        """
        conn = httplib.HTTPSConnection('random.random/random')
        conn.request("GET", "/random.aspx")

    def test_fail_with_step(self):
        self.fail('Step 3 Failed: MEssaasasas')
