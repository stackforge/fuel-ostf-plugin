from ostf_adapter.wsgi import controllers
from ostf_adapter.storage import models
import unittest2
from mock import patch, MagicMock


@patch('ostf_adapter.wsgi.controllers.request')
class TestTestsController(unittest2.TestCase):

    def setUp(self):
        self.fixtures = [models.Test(), models.Test()]
        self.storage = MagicMock()

        self.controller = controllers.TestsController()

    def test_get_all(self, request):
        request.storage = self.storage
        self.storage.get_tests.return_value = self.fixtures
        res = self.controller.get_all()
        self.storage.get_tests.assert_called_once_with()
        self.assertEqual(res, [f.frontend for f in self.fixtures])

    def test_get_one(self, request):
        pass


@patch('ostf_adapter.wsgi.controllers.request')
class TestTestSetsController(unittest2.TestCase):

    def setUp(self):
        self.fixtures = [models.TestSet(), models.TestSet()]
        self.storage = MagicMock()
        self.controller = controllers.TestsetsController()

    def test_get_all(self, request):
        request.storage = self.storage
        self.storage.get_test_sets.return_value = self.fixtures
        res = self.controller.get_all()
        self.storage.get_test_sets.assert_called_once_with()
        self.assertEqual(res, [f.frontend for f in self.fixtures])

    def test_get_one(self, request):
        pass

@patch('ostf_adapter.wsgi.controllers.request')
class TestTestRunsController(unittest2.TestCase):

    def setUp(self):
        self.fixtures = [models.TestRun(), models.TestRun()]
        self.storage = MagicMock()
        self.plugin = MagicMock()
        self.controller = controllers.TestrunsController()

    def test_get_all(self, request):
        request.storage = self.storage
        pass

    def test_post(self, request):
        request.storage = self.storage

    def test_put(self, request):
        request.storage = self.storage

    def test_get_last(self, request):
        request.storage = self.storage
        cluster_id = 1
        self.storage.get_last_test_results.return_value = self.fixtures
        res = self.controller.get_last(cluster_id)
        self.storage.get_last_test_results.assert_called_once_with(cluster_id)
        self.assertEqual(res, [f.frontend for f in self.fixtures])

    def test_run(self, request):
        request.storage = self.storage

    def test_kill(self, request):
        request.storage = self.storage

    def test_restart(self, request):
        request.storage = self.storage

    def test_check_last_running(self, request):
        request.storage = self.storage

