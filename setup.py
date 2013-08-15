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

import multiprocessing
import setuptools

requirements = [
    'Mako==0.8.1',
    'MarkupSafe==0.18',
    'SQLAlchemy==0.8.2',
    'WebOb==1.2.3',
    'WebTest==2.0.6',
    'alembic==0.5.0',
    'argparse==1.2.1',
    'beautifulsoup4==4.2.1',
    'distribute==0.7.3',
    'gevent==0.13.8',
    'greenlet==0.4.1',
    'nose==1.3.0',
    'pecan==0.3.0',
    'psycogreen==1.0',
    'psycopg2==2.5.1',
    'simplegeneric==0.8.1',
    'six==1.3.0',
    'stevedore==0.10',
    'waitress==0.8.5',
    'wsgiref==0.1.2',
    'WSME==0.5b2'
]

test_requires = [
    'mock==1.0.1',
    'pep8==1.4.6',
    'py==1.4.15',
    'six==1.3.0',
    'tox==1.5.0',
    'unittest2',
    'nose',
    'requests'
]

setuptools.setup(

    name='testing_adapter',
    version='0.2',

    description='cloud computing testing',

    zip_safe=False,

    test_suite='tests',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Setuptools Plugin',
        'Environment :: OpenStack',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Testing',
    ],

    packages=setuptools.find_packages(
        exclude=['tests', 'utils', '*_tests']),

    include_package_data=True,

    install_requires=requirements,

    test_requires=test_requires,

    entry_points={
        'plugins': [
            'nose = ostf_adapter.nose_plugin.nose_adapter:NoseDriver'
        ],
        'console_scripts': [
            'ostf-server = bin.adapter_api:main',
            'update-commands = test_utils.update_commands:main'
        ]
    },
)
