import setuptools
import textwrap

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

    packages=setuptools.find_packages(exclude=['bin',
                                               'tests',
                                               'tests.*',
                                               '*.tests',]),

    include_package_data=True,

    test_suite='nose.collector',

    scripts=['bin/adapter-api'],

    py_modules=[],


    zip_safe=False,

    entry_points={
    'plugins': [
        'nose = core.transport.nose_adapter:NoseDriver'
    ]
    },
)