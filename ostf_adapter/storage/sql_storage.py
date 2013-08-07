#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from datetime import datetime
import json
import logging

from sqlalchemy import create_engine, exc, desc, func, asc
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import pool

from ostf_adapter.storage import models


log = logging.getLogger(__name__)


class SqlStorage(object):
    def __init__(self, engine_url, poolclass=pool.NullPool):
        log.info('Create sqlalchemy engine - %s' % engine_url)
        self._engine = create_engine(
            engine_url,
            poolclass=poolclass)
        self._session = sessionmaker(
            bind=self._engine, expire_on_commit=False)

    def get_session(self):
        return self._session()

    def add_test_run(self, test_set, external_id, data, status='running',
                     tests=None):
        log.info('ADD test run - %s' % test_set)
        predefined_tests = tests or []
        session = self.get_session()
        tests = session.query(models.Test).filter_by(test_set_id=test_set)
        test_run = models.TestRun(type=test_set, external_id=external_id,
                                  data=json.dumps(data), status=status)
        session.add(test_run)
        for test in tests:
            test_data = {'test_run_id': test_run.id,
                         'name': test.name,
                         'data': test.data,
                         'status': 'wait_running'}
            if predefined_tests and test.name not in predefined_tests:
                log.info('PREDEFINED TEST %s' % test.name)
                test_data.update({'status': 'disabled'})
            new_test = models.Test(**test_data)
            session.add(new_test)
        session.commit()
        return test_run, session

    def add_test_set(self, test_set):
        log.info('Inserting test set %s' % test_set)
        session = self.get_session()
        test_set_obj = models.TestSet(**test_set)
        new_obj = session.merge(test_set_obj)
        session.add(new_obj)
        session.commit()
        session.close()
        return new_obj

    def get_test_sets(self):
        session = self.get_session()
        test_sets = session.query(models.TestSet).all()
        session.commit()
        session.close()
        return test_sets

    def get_test_set(self, test_set):
        session = self.get_session()
        test_set = session.query(models.TestSet).filter_by(id=test_set).first()
        session.commit()
        session.close()
        return test_set

    def get_tests(self):
        session = self.get_session()
        tests = session.query(models.Test).order_by(
            asc(models.Test.test_set_id), asc(models.Test.name)). \
            filter_by(test_run_id=None).all()
        session.commit()
        session.close()
        return tests

    def add_test_for_testset(self, test_set, test_name, data):
        log.info('Data received %s' % data)
        session = self.get_session()
        old_test_obj = session.query(models.Test).filter_by(
            name=test_name, test_set_id=test_set, test_run_id=None).\
            update(data, synchronize_session=False)
        if old_test_obj:
            old_test_obj(**data)
            session.add(old_test_obj)
        else:
            data.update({'test_set_id': test_set,
                         'name': test_name})
            test_obj = models.Test(**data)
            session.add(test_obj)
        session.commit()
        session.close()

    def get_last_test_run(self, test_set, external_id):
        session = self.get_session()
        test_run = session.query(models.TestRun). \
            filter_by(external_id=str(external_id), type=test_set). \
            order_by(desc(models.TestRun.id)).first()
        session.commit()
        session.close()
        return test_run

    def get_test_results(self):
        session = self.get_session()
        test_runs = session.query(models.TestRun). \
            options(joinedload('tests')). \
            order_by(desc(models.TestRun.id))
        session.commit()
        session.close()
        return test_runs

    def get_last_test_results(self, external_id):
        session = self.get_session()
        test_run_ids = session.query(func.max(models.TestRun.id)) \
            .group_by(models.TestRun.type).filter_by(external_id=external_id)
        log.info('LASR TEST RUN IDS %s' % test_run_ids)
        test_runs = session.query(models.TestRun). \
            options(joinedload('tests')). \
            filter(models.TestRun.id.in_((test_run_ids)))
        session.commit()
        session.close()
        if not test_runs:
            msg = 'Database does not contains ' \
                  'Test Run with ID %s' % external_id
            log.warning(msg)
            raise exc.OstfDBException(message=msg)
        return test_runs

    def get_test_run(self, test_run_id, joined=False):
        session = self.get_session()
        if not joined:
            test_run = session.query(models.TestRun). \
                filter_by(id=test_run_id).first()
        else:
            test_run = session.query(models.TestRun). \
                options(joinedload('tests')). \
                filter_by(id=test_run_id).first()
        session.commit()
        session.close()
        return test_run

    def add_test_result(
            self, test_run_id, test_name, status, time_taken, data):
        log.info('Add test result for: ID: %s\n'
                 'TEST NAME: %s\n'
                 'DATA: %s' % (test_run_id, test_name, data))
        session = self.get_session()
        session.query(models.Test). \
            filter_by(name=test_name, test_run_id=test_run_id). \
            update({
            'status': status,
            'taken': time_taken,
            'data': json.dumps(data)
        })
        session.commit()
        session.close()

    def update_test_run(self, test_run_id, status=None):
        session = self.get_session()
        updated_data = {}
        if status:
            updated_data['status'] = status
        if status in ['finished', 'error', 'error_on_cleanup']:
            updated_data['ended_at'] = datetime.utcnow()
        session.query(models.TestRun). \
            filter(models.TestRun.id == test_run_id). \
            update(updated_data, synchronize_session=False)
        session.commit()
        session.close()

    def update_running_tests(self, test_run_id, status='stopped'):
        session = self.get_session()
        session.query(models.Test). \
            filter(models.Test.test_run_id == test_run_id,
                   models.Test.status.in_(('running', 'wait_running'))). \
            update({'status': status}, synchronize_session=False)
        session.commit()
        session.close()

    def flush_testsets(self):
        session = self.get_session()
        session.query(models.Test).filter_by(test_run_id=None).delete()
        session.query(models.TestSet).delete()
        session.commit()
        session.close()

    def update_all_running_test_runs(self, status='finished'):
        session = self.get_session()
        session.query(models.TestRun). \
            filter(models.TestRun.status.in_(('started', 'running'))). \
            update({'status': 'finished'}, synchronize_session=False)
        session.query(models.Test). \
            filter(models.Test.status.in_(('running', 'wait_running'))). \
            update({'status': 'stopped'}, synchronize_session=False)
        session.commit()
        session.close()

    def update_test_run_tests(self, test_run_id,
                              tests_names, status='wait_running'):
        session = self.get_session()
        session.query(models.Test). \
            filter(models.Test.name.in_(tests_names),
                   models.Test.test_run_id == test_run_id). \
            update({'status': status}, synchronize_session=False)
        session.commit()
        session.close()