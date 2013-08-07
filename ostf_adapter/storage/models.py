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

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json


BASE = declarative_base()


class TestRun(BASE):

    __tablename__ = 'test_runs'

    id = sa.Column(sa.Integer(), primary_key=True)
    external_id = sa.Column(sa.String(128))
    type = sa.Column(sa.String(128))
    status = sa.Column(sa.String(128))
    stats = sa.Column(sa.Text())
    data = sa.Column(sa.Text())
    started_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    ended_at = sa.Column(sa.DateTime)

    tests = relationship('Test', backref='test_run', order_by='Test.name')

    @property
    def frontend(self):
        test_run_data = {
            'id': self.id,
            'testset': self.type,
            'metadata': json.loads(self.data),
            'status': self.status,
            'started_at': self.started_at,
            'ended_at': self.ended_at
        }
        tests = []
        if self.tests:
            for test in self.tests:
                test_data = {'id': test.name,
                             'taken': test.taken,
                             'status': test.status}
                if test_data:
                    test_data.update(json.loads(test.data))
                tests.append(test_data)
            test_run_data['tests'] = tests
        return test_run_data

class TestSet(BASE):

    __tablename__ = 'test_sets'

    id = sa.Column(sa.String(128), primary_key=True)
    description = sa.Column(sa.String(128))
    data = sa.Column(sa.Text())

    tests = relationship('Test', backref='test_set', order_by='Test.name')

    @property
    def frontend(self):
        return {'id': self.id, 'name': self.description}


class Test(BASE):

    __tablename__ = 'tests'

    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(512))
    status = sa.Column(sa.String(128))
    taken = sa.Column(sa.Float())
    data = sa.Column(sa.Text())

    test_set_id = sa.Column(sa.String(128), sa.ForeignKey('test_sets.id'))
    test_run_id = sa.Column(sa.Integer(), sa.ForeignKey('test_runs.id'))


    @property
    def frontend(self):
        test_data = json.loads(self.data)
        return {
            'id': self.name,
            'testset': self.test_set_id,
            'name': test_data['name'],
            'description': test_data['description'],
            'duration': test_data['duration'],
            'message': test_data['message'],
            'step': test_data['step'],
            'status': self.status,
            'taken': self.taken
        }
