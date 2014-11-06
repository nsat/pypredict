#!/usr/bin/python

from distutils.core import setup, Extension
setup(name='pypredict', version='1.1',  \
      ext_modules=[Extension('predict', ['predict.c'])])
