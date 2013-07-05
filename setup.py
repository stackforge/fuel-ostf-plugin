import multiprocessing
import os
import subprocess
import setuptools


def load_requirements(requirements_path):
    root = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(root, requirements_path), 'r') as reqs:
        return reqs.read().split('\n')

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

    packages=setuptools.find_packages(exclude=['tests', 'bin']),

    include_package_data=True,

    install_requires=load_requirements('tools/pip-requires'),

    tests_require=load_requirements('tools/test-requires'),

    setup_requires=['setuptools_git>=0.4'],

    entry_points={
        'plugins': [
            'nose = ostf_adapter.transport.nose_adapter:NoseDriver'
        ],
        'console_scripts': [
            'ostf-server = bin.adapter_api:main',
            'update-commands = tests.utils.update_commands:main'
        ]
    },
)
