#!/usr/bin/env python

from setuptools import setup, Extension

setup(
    name="pypredict",
    version="1.6.1",
    author="Jesse Trutna",
    author_email="jesse@spire.com",
    url="https://github.com/nsat/pypredict",
    py_modules=["predict"],
    ext_modules=[Extension("cpredict", ["predict.c"])],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
