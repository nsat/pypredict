#!/usr/bin/python

from distutils.core import setup, Extension
setup(
    name='pypredict',
    version='1.2',
    author="Jesse Trutna",
    author_email="jesse@spire.com",
    url="https://github.com/nsat/pypredict",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    ],
    py_modules=['predict'],
    ext_modules=[Extension('cpredict', ['predict.c'])]
    )
