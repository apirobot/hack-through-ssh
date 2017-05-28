#!/bin/sh

virtualenv --python=python2 venv

venv/bin/pip install cython
venv/bin/pip install -r requirements.txt
venv/bin/python setup.py install
