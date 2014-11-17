#!/usr/bin/python

from distutils.core import setup, Extension
setup(
	name='pypredict',
	version='1.1',
	author="Jesse Trutna",
	author_email="jesse@spire.com",
	url="https://github.com/nsat/pypredict",
	py_modules=['predict'],
	ext_modules=[Extension('cpredict', ['predict.c'])]
    )

