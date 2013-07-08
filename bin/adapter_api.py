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
import sys
import os
import argparse
from ostf_adapter import cli_config
from ostf_adapter.storage.sql.cli import do_apply_migrations
from ostf_adapter.common import logger
from gevent import pywsgi
from ostf_adapter.wsgi import app
import logging


def main():

    cli_args = cli_config.parse_cli()

    config = {'server':
            {
                'host': cli_args.host,
                'port': cli_args.port
            },
        'dbpath': cli_args.dbpath
            }

    logger.setup(log_file=cli_args.log_file)
    app.setup_config(config)

    log = logging.getLogger(__name__)
    log.info('STARTING SETUP')

    if getattr(cli_args, 'after_init_hook'):
        return do_apply_migrations()

    root = app.setup_app()

    host, port = app.pecan_config_dict['server'].values()
    srv = pywsgi.WSGIServer((host, int(port)), root)
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