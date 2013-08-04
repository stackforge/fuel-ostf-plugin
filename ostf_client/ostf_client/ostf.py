#!/usr/bin/env python
"""Openstack testing framework client

Usage: ostf.py run <test_set> [--id=<cluster_id>] [--tests=<tests>]  [--url=<url>]  [--timeout=<timeout>]
       ostf.py list [<test_set>]

    -h --help                   Show this screen
    --tests=<tests>             Tests to run
    --id=<cluster_id>           Cluster id to use, default: OSTF_CLUSTER_ID or "1"
    --url=<url>                 Ostf url, default: OSTF_URL or http://0.0.0.0:8989/v1
    --timeout=<timeout>         Amount of time after which test_run will be stopped [default: 60]

"""
import os
import sys

from docopt import docopt
from clint.textui import puts, colored, columns, indent
from blessings import Terminal
from requests import get
from client import TestingAdapterClient


def get_cluster_id():
    try:
        r = get('http://localhost:8000/api/clusters').json()
    except:
        return 0
    return next(item['id'] for item in r)


def main():
    t = Terminal()
    args = docopt(__doc__, version='0.1')
    test_set = args['<test_set>']
    cluster_id = args['--id'] or os.environ.get('OSTF_CLUSTER_ID') or get_cluster_id() or '1'
    tests = args['--tests'] or []
    timeout = args['--timeout']
    url = args['--url'] or os.environ.get('OSTF_URL') or 'http://0.0.0.0:8989/v1'

    client = TestingAdapterClient(url)

    def run():
        col = 60

        statused = dict(
            running='running',
            wait_running='wait_running',
            success=colored.green('success'),
            finished=colored.blue('finished'),
            failure=colored.red('failure'),
            error=colored.red('error'),
            stopped=colored.red('stopped')
        )

        tests = [test['id'].split('.')[-1] for test in client.tests().json() if test['testset'] == test_set]

        puts(columns(["General", col], ['running', col]))
        for test in tests:
            puts(columns([test, col], ['wait_running', col]))

        def polling_hook(response):
            current_status, current_tests = next((item['status'], item['tests']) for item in response.json()
                                                 if item['testset'] == test_set)

            for _ in range(len(current_tests)+1):
                print t.move_up + t.move_left,

            puts(columns(["General", col], [statused[current_status], col]))
            for test in current_tests:
                puts(columns([((test['id'].split('.')[-1])), col], [statused[test['status']], col]))

        try:
            client.run_testset_with_timeout(test_set, cluster_id, timeout, 2, polling_hook)
        except AssertionError as e:
            return 1
        return 0

    def list_tests():
        result = client.tests().json()
        tests = (test for test in result if test['testset'] == test_set)

        col = 60
        puts(columns([(colored.red("ID")), col], [(colored.red("NAME")), None]))

        for test in tests:
            test_id = test['id'].split('.')[-1]
            puts(columns([test_id, col], [test['name'], None]))

        return 0

    def list_test_sets():
        result = client.testsets().json()

        col = 60
        puts(columns([(colored.red("ID")), col], [(colored.red("NAME")), None]))

        for test_set in result:
            puts(columns([test_set['id'], col], [test_set['name'], None]))
        return 0

    if args['run']:
        return run()
    if test_set:
        return list_tests()
    return list_test_sets()

if __name__ == '__main__':
    sys.exit(main())





