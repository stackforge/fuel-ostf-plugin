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

    tests = relationship('Test', backref='test_run')


class TestSet(Base):

    __tablename__ = 'test_sets'

    id = sa.Column(sa.String(128), primary_key=True)
    description = sa.Column(sa.String(128))
    data = sa.Column(sa.Text())

    tests = relationship('Test', backref='test_set')


class Test(Base):

    __tablename__ = 'tests'

    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(512))
    status = sa.Column(sa.String(128))
    taken = sa.Column(sa.Float())
    data = sa.Column(sa.Text())

    test_set_id = sa.Column(sa.String(128), sa.ForeignKey('test_sets.id'))
    test_run_id = sa.Column(sa.Integer(), sa.ForeignKey('test_runs.id'))
