#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os, shutil
import FHOTF

setup(
    name='FHOTF',
    version=FHOTF.__version__,
    packages=find_packages(),
    author="FredThx",
    author_email="FredThx@gmail.com",
    description="A hotfolders creator",
    long_description=open('README.md').read(),
    install_requires=["FUTIL", "watchdog", "toml"],
    include_package_data=True,
    url='',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8"
    ],
    license="CECILL_V2.1",

)
try:
	os.mkdir('/opt/FHOTF')
except OSError:
	pass
shutil.copy('fhotf.py', '/opt/FHOTF')
shutil.copy('fhotf.service', '/opt/FHOTF')
