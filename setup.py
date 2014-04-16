#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pysox',
    version='0.0.1',
    description='Sensor Over XMPP library for python',
    author='Hide. Tokuda Laboratory',
    author_email='ht@ht.sfc.keio.ac.jp',
    url='',
    packages=find_packages(),
    license=open('LICENSE').read(),
    include_package_data=True,
    install_requires=[],
    tests_requires=['nose'],
    test_suite='nose.collector'
)
