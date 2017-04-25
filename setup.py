#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


version = get_version('hack_through_ssh')


setup(
    name='hack_through_ssh',
    version=version,
    license='ISC',
    description='Hack through SSH',
    author='Denis Orehovsky, Artem Matveev',
    author_email='denis.orehovsky@gmail.com, andreygrin97@mail.ru',
    packages=get_packages('hack_through_ssh'),
    install_requires=[
        'paramiko',
        'pycrypto',
        'ecdsa',
        'kivy',
        'sftpserver',
        'pyyaml',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
