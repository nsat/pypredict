#!/usr/bin/env python

from distutils.core import setup, Extension
setup(
    name='pypredict',
    version='1.5.0',
    author="Jesse Trutna",
    author_email="jesse@spire.com",
    url="https://github.com/nsat/pypredict",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
    ],
    py_modules=['predict'],
    ext_modules=[Extension('cpredict', ['predict.c'])]
    )
