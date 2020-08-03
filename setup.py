#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name='pysox',
    version='0.2.0',
    description='Sensor Over XMPP library for python',
    author='Hide. Tokuda Laboratory',
    author_email='ht@ht.sfc.keio.ac.jp',
    url='',
    packages=find_packages(),
    license=open('LICENSE').read(),
    include_package_data=True,
    install_requires=_requires_from_file('requirements.txt'),
    tests_requires=['nose'],
    test_suite='nose.collector'
)
