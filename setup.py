import setuptools
import io


def load_requirements(requirements_path):
    with io.open(requirements_path, 'r') as reqs:
        return reqs.read()


setuptools.setup(

    name='testing-adapter',
    version='0.2',

    description='cloud computing testing',


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

    packages=setuptools.find_packages(),

    include_package_data=True,

    install_requires=load_requirements('tools/pip-requires'),

    tests_require=load_requirements('tools/test-requires'),

    scripts=['bin/adapter-api.py', 'bin/adapter-db.py'],

    package_data={
        '' : ['data/*.json', '*.ini']
    },

    entry_points={
        'plugins': [
            'nose = core.transport.nose_adapter:NoseDriver'
        ],
        'console_scripts': [
            'ostf-server = adapter-api:main',
            'ostf-db = adapter-db:main'
        ]
    },
)