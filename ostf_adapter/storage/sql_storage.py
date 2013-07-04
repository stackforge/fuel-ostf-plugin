from gevent.monkey import patch_all
patch_all()

from psycogreen.gevent import patch_psycopg
patch_psycopg()

from sqlalchemy import create_engine, exc, desc
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.pool import QueuePool
from datetime import datetime

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

    def add_test_run(self, test_set, external_id, data, status='started'):
        log.info('Invoke test run - %s' % test_set)
        session = self.get_session()
        tests = session.query(models.Test).filter_by(test_set_id=test_set)
        test_run = models.TestRun(type=test_set, external_id=external_id,
                                  data=json.dumps(data), status='started')
        session.add(test_run)
        for test in tests:
            new_test = models.Test(test_run_id=test_run.id,
                                   status='wait_running',
                                   name=test.name,
                                   data=test.data)
            session.add(new_test)
        session.commit()
        return test_run.id

    def add_test_set(self, test_set, test_set_data):
        log.info('Inserting test set %s' % test_set)
        session = self.get_session()
        description = test_set_data.pop("description", "")

        test_set_obj = models.TestSet(
            id=test_set, description=description, data=json.dumps(test_set_data))
        new_obj = session.merge(test_set_obj)
        session.add(new_obj)
        session.commit()
        return True

    def get_test_sets(self):
        session = self.get_session()
        test_sets = session.query(models.TestSet).all()
        session.commit()
        return test_sets

    def get_tests(self):
        session = self.get_session()
        tests = session.query(models.Test).filter_by(test_run_id=None)
        log.info('Tests received %s' % tests.count())
        session.commit()
        return [{'id': t.name, 'test_set': t.test_set_id,
                 'name': json.loads(t.data)['name']} for t in tests]

    def add_sets_test(self, test_set, test_name, data):
        log.info('Data received %s' % data)
        session = self.get_session()
        old_test_obj = session.query(models.Test).filter_by(
            name=test_name, test_set_id=test_set).first()
        if old_test_obj:
            old_test_obj.data = json.dumps(data)
            session.add(old_test_obj)
        else:
            test_obj = models.Test(
                name=test_name, data=json.dumps(data), test_set_id=test_set)
            session.add(test_obj)
        session.commit()

    def get_last_test_run(self, external_id):
        session = self.get_session()
        test_run = session.query(models.TestRun).\
            filter_by(external_id=external_id).\
            order_by(desc(models.TestRun.id)).first()
        session.commit()
        return test_run

    def get_test_results(self):
        session = self.get_session()
        test_runs = session.query(models.TestRun).\
            options(joinedload('tests')).\
            order_by(desc(models.TestRun.id))
        session.commit()
        return test_runs

    def get_last_test_results(self, external_id):
        session = self.get_session()
        test_run = session.query(models.TestRun).\
            options(joinedload('tests')).\
            filter_by(external_id=external_id).\
            order_by(desc(models.TestRun.id)).first()
        session.commit()
        if not test_run:
            msg = 'Database does not contains ' \
                  'Test Run with ID %s' % external_id
            log.warning(msg)
            raise exc.OstfDBException(message=msg)
        return test_run

    def get_test_run(self, test_run_id):
        session = self.get_session()
        test_run = session.query(models.TestRun).\
            filter_by(id=test_run_id).first()
        session.commit()
        return test_run

    def add_test_result(
            self, test_run_id, test_name, status, time_taken, data):
        log.info('Add test result for: ID: %s\n'
                 'TEST NAME: %s\n'
                 'DATA: %s' % (test_run_id, test_name, data))
        session = self.get_session()
        session.query(models.Test).\
            filter_by(name=test_name, test_run_id=test_run_id).\
            update({
                'status': status,
                'taken': time_taken,
                'data': json.dumps(data)
            })
        session.commit()

    def update_test_run(self, test_run_id, stats=None, status=None):
        session = self.get_session()
        updated_data = {'ended_at': datetime.utcnow()}
        if stats:
            updated_data['stats'] = json.dumps(stats)
        if status:
            updated_data['status'] = status
        test_run = session.query(models.TestRun).\
            filter(models.TestRun.id == test_run_id).\
            update(updated_data)
        session.commit()
        return test_run

    def update_running_tests(self, test_run_id, status='stopped'):
        session = self.get_session()
        session.query(models.Test).\
            filter(models.Test.test_run_id == test_run_id,
                   models.Test.status.in_(('running', 'wait_running'))).\
            update({'status': status}, synchronize_session=False)
        session.commit()
