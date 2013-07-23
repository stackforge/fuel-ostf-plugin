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


Base = declarative_base()


class TestRun(Base):

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


class TestSet(Base):

    __tablename__ = 'test_sets'

    id = sa.Column(sa.String(128), primary_key=True)
    description = sa.Column(sa.String(128))
    data = sa.Column(sa.Text())

    tests = relationship('Test', backref='test_set', order_by='Test.name')


class Test(Base):

    __tablename__ = 'tests'

    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(512))
    status = sa.Column(sa.String(128))
    taken = sa.Column(sa.Float())
    data = sa.Column(sa.Text())

    test_set_id = sa.Column(sa.String(128), sa.ForeignKey('test_sets.id'))
    test_run_id = sa.Column(sa.Integer(), sa.ForeignKey('test_runs.id'))
