import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()


class TestRun(Base):

    __tablename__ = 'test_runs'

    id = sa.Column(sa.Integer(), primary_key=True)
    type = sa.Column(sa.String(128))


class Test(Base):

    __tablename__ = 'tests'

    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.String(128))
    status = sa.Column(sa.String(128))
    taken = sa.Column(sa.Time())
    data = sa.Column(sa.Text())

    test_run_id = sa.Column(sa.Integer(), sa.ForeignKey('test_runs.id'))
