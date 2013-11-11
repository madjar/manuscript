#!/usr/bin/env python

from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requires = [
    'docopt',
    'pathlib',
    ]

setup(
    name='manuscript',
    version='0.1.0',
    description='Manuscript helps you manage your python scripts and their dependencies',
    long_description=readme + '\n\n' + history,
    author='Georges Dubus',
    author_email='georges.dubus@gmail.com',
    url='https://github.com/madjar/manuscript',
    py_modules=['manuscript'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'manuscript = manuscript:main',
        ]
    },
    install_requires=requires,
    license="BSD",
    zip_safe=False,
    keywords='manuscript',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
