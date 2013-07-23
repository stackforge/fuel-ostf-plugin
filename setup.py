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
    'wsgiref==0.1.2'
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

    entry_points={
        'plugins': [
            'nose = ostf_adapter.transport.nose_adapter:NoseDriver'
        ],
        'console_scripts': [
            'ostf-server = bin.adapter_api:main',
            'update-commands = test_utils.update_commands:main'
        ]
    },
)
