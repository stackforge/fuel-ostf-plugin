import argparse
import sys


def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--after-initialization-environment-hook',
                        action='store_true', dest='after_init_hook')
    parser.add_argument('--dbpath', metavar='DB_PATH',
        default='postgresql+psycopg2://adapter:demo@localhost/testing_adapter')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default='8989')
    parser.add_argument('--log_file', default=None, metavar='PATH')
    parser.add_argument('--nailgun-host', default='127.0.0.1')
    parser.add_argument('--nailgun-port', default='3232')
    return parser.parse_args(sys.argv[1:])