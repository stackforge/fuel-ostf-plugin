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
from setuptools import setup, find_packages

version = '0.1'
requirements = [
    'blessings==1.5',
    'clint==0.3.1',
    'docopt==0.6.1',
    'requests==1.2.3'
]

setup(

    name='ostf_client',
    version=version,
    description="Command line client for Fuel OSTF plugin.",

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
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),

    include_package_data=True,

    zip_safe=False,

    install_requires=requirements,

    entry_points={
        'console_scripts': [
            'ostf = ostf_client.ostf:main'
        ]
    },
)
