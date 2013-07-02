#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from oslo.config import cfg
import argparse
import sys
import os
from ostf_adapter import cli_config
from ostf_adapter.storage.sql.cli import do_apply_migrations
from ostf_adapter.common import logger
from gevent import wsgi
from ostf_adapter.wsgi import app
import logging

logger.setup()

log = logging.getLogger(__name__)


def main():
    log.info('STARTING SETUP')
    if getattr(cfg.CONF, 'after_init_hook'):
        return do_apply_migrations()
    root = app.setup_app({'server': {
                            'host': cfg.CONF.host,
                            'port': cfg.CONF.port
                        }})

    host, port = app.pecan_config_dict['server'].values()
    srv = wsgi.WSGIServer((host, int(port)), root)
    log.info('Starting server in PID %s' % os.getpid())

    if host == '0.0.0.0':
        log.info('serving on 0.0.0.0:%s,'
                 ' view at http://127.0.0.1:%s' % (port, port))
    else:
        log.info("serving on http://%s:%s" % (host, port))

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        # allow CTRL+C to shutdown without an error
        pass


if __name__ == '__main__':
    main()