from nose import main, plugins
from nose.plugins import manager, capture, skip
import os
from core.storage import get_storage


class RedisPlugin(plugins.Plugin):

    enabled = True
    name = 'redis'
    score = 15000
    env_opt = 'NOSE_NOCAPTURE'

    def __init__(self, test_run_id):
        self.test_run_id = test_run_id
        self.storage = get_storage()
        super(RedisPlugin, self).__init__()

    def options(self, parser, env=os.environ):
        pass

    def configure(self, options, conf):
        self.conf = conf

    def begin(self):
        pass

    def addSuccess(self, test, capt=None):
        self.storage.add_test_result(self.test_run_id, test.id(),
                                     {'status': 'SUCCESS'})

    def addFailure(self, test, err, capt=None, tb_info=None):
        self.storage.add_test_result(self.test_run_id, test.id(),
                                     {'status': 'FAILURE'})

    def addError(self, test, err, capt=None, tb_info=None):
        self.storage.add_test_result(self.test_run_id, test.id(),
                                     {'status': 'ERROR'})


def run(service_path, test_run_id):
    test_run = main(defaultTest=service_path,
                    addplugins=[RedisPlugin(test_run_id)],
                    exit=False)
    return test_run

