from gevent.monkey import patch_all
patch_all()
from psycogreen.gevent import patch_psycopg
patch_psycopg()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.storage.sql import models


class SqlStorage(object):

    def __init__(self, engine_url):
        self._engine = create_engine(engine_url)
        self._engine.pool._use_threadlocal = True
        self._sessionmaker = sessionmaker(bind=self._engine,
            autocommit=True, expire_on_commit=False)
        self._session = None

    @property
    def session(self):
        if not self._session:
            self._session = self._sessionmaker()
        return self._session

    def add_test_run(self, test_run):
        with self.session.begin(subtransactions=True):
            test_run = models.TestRun(type=test_run)
            self.session.add(test_run)
        return {test_run.type: test_run.id}

    def get_test_results(self, test_run_id):
        pass

    def get_test_result(self, test_run_id, test_id, stats=False):
        pass

    def add_test_result(self, test_run_id, test_id, data):
        pass

