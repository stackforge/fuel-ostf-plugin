from gevent.monkey import patch_all
patch_all()

from psycogreen.gevent import patch_psycopg
patch_psycopg()

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.pool import QueuePool

from ostf_adapter.storage.sql import models
from ostf_adapter import exceptions as exc

import simplejson as json
import logging

log = logging.getLogger(__name__)


class SqlStorage(object):

    def __init__(self, engine_url):
        log.info('Create sqlalchemy engine - %s' % engine_url)
        self._engine = create_engine(engine_url, pool_size=20, poolclass=QueuePool)
        self._engine.pool._use_threadlocal = True
        self._session = sessionmaker(bind=self._engine)

    def get_session(self):
        return self._session()

    def add_test_run(self, test_run):
        log.info('Invoke test run - %s' % test_run)
        session = self.get_session()
        test_run = models.TestRun(type=test_run)
        session.add(test_run)
        session.commit()
        return {'type': test_run.type, 'id': test_run.id}

    def add_test_set(self, test_set, test_set_data):
        log.info('Inserting test set %s' % test_set)
        session = self.get_session()
        description = test_set_data.pop("description", "")
        test_set_obj = models.TestSet(
            id=test_set, description=description, data=json.dumps(test_set_data))
        session.add(test_set_obj)
        try:
            session.commit()
        except Exception:
            log.info('Test set %s already there' % test_set)
        return True

    def get_test_sets(self):
        session = self.get_session()
        test_sets = session.query(models.TestSet).all()
        session.commit()
        return test_sets

    def get_test_results(self, test_run_id):
        session = self.get_session()
        test_run = session.query(models.TestRun).\
            options(joinedload('tests')).\
            filter_by(id=test_run_id).first()
        session.commit()
        if not test_run:
            msg = 'Database does not contains ' \
                  'Test Run with ID %s' % test_run_id
            log.warning(msg)
            raise exc.OstfDBException(message=msg)
        tests = {}
        for test in test_run.tests:
            tests[test.name] = json.loads(test.data)
        res = {'type': test_run.type,
                'id': test_run.id,
                'tests': tests}
        if test_run.data:
            res['stats'] = json.loads(test_run.data)
        return res

    def get_test_result(self, test_run_id, test_id, stats=False):
        pass

    def add_test_result(self, test_run_id, test_name, data):
        log.info('Add test result for: ID: %s\n'
                 'TEST NAME: %s\n'
                 'DATA: %s' % (test_run_id, test_name, data))
        session = self.get_session()
        test = models.Test(name=test_name, status=data.get('type', None),
                           taken=data.get('taken', None),
                           test_run_id=test_run_id,
                           data=json.dumps(data))
        session.add(test)
        session.commit()
        return test

    def update_test_run(self, test_run_id, data):
        session = self.get_session()
        test_run = session.query(models.TestRun).\
            filter(models.TestRun.id == test_run_id).\
            update({'data': json.dumps(data)})
        session.commit()
        return test_run