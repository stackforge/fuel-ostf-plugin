__author__ = 'ekonstantinov'
from os import environ as env
from unittest import TestCase
from oslo.config import cfg

opts = [
    cfg.StrOpt('quantum', default='ALALALALA')
]

class Config(TestCase):
    def test_config(self):
        file_path = env['OSTF_CONF_PATH']
        cfg.CONF






