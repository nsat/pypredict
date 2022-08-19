#!/usr/bin/env python

from setuptools import setup, Extension

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pypredict",
    version="1.7.0",
    author="Jesse Trutna",
    author_email="jesse@spire.com",
    maintainer="Spire Global Inc",
    maintainer_email="opensource@spire.com",
    description="Interface to the Predict satellite tracking and orbital prediction library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nsat/pypredict",
    py_modules=["predict"],
    ext_modules=[Extension("cpredict", ["predict.c"])],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
