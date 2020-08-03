#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages


# def _requires_from_file(filename):
#     return open(filename).read().splitlines()



def parse_requirements_txt(f):
    pat_hash = re.compile(r'--hash=[^:]+:[a-fA-F0-9]+')
    with open(f) as fh:
        content = fh.read()
        content = re.sub(pat_hash, "", content)
        content = content.replace("\\\n", "")
        lines = content.split("\n")
        lines = [ line.strip() for line in lines ]
        lines = [ line for line in lines if line != "" ]
        lines = [ line.split(";")[0] for line in lines ]
        
        return lines


setup(
    name='python-sox',
    version='0.2.1',
    description='Sensor Over XMPP library for python',
    author='Hide. Tokuda Laboratory',
    author_email='ht@ht.sfc.keio.ac.jp',
    url='',
    packages=find_packages(),
    license=open('LICENSE').read(),
    include_package_data=True,
    install_requires=parse_requirements_txt('requirements.txt'),
    tests_requires=['nose'],
    test_suite='nose.collector'
)
