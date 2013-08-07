#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import os
from ostf_adapter import cli_config
from ostf_adapter.storage.alembic_cli import do_apply_migrations
from ostf_adapter import logger
from gevent import pywsgi
from ostf_adapter.wsgi import app
import logging
import signal
import pecan


def main():

    cli_args = cli_config.parse_cli()

    config = {
        'server': {
            'host': cli_args.host,
            'port': cli_args.port
        },
        'dbpath': cli_args.dbpath,
        'debug': cli_args.debug
    }

    logger.setup(log_file=cli_args.log_file)
    app.setup_config(config)

    log = logging.getLogger(__name__)
    log.info('STARTING SETUP')

    if getattr(cli_args, 'after_init_hook'):
        return do_apply_migrations()

    root = app.setup_app()

    host, port = pecan.conf.server.host, pecan.conf.server.port
    srv = pywsgi.WSGIServer((host, int(port)), root)
    log.info('Starting server in PID %s', os.getpid())

    log.info("serving on http://%s:%s", host, port)

    try:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        srv.serve_forever()
    except KeyboardInterrupt:
        # allow CTRL+C to shutdown without an error
        pass


if __name__ == '__main__':
    main()
