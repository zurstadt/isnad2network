#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="isnad2network",
    version="0.2.0",  # Update version number as appropriate
    author="Jeremy Farrell",
    author_email="j.e.farrell@umail.leidenuniv.nl",
    description="A toolkit for processing and analyzing isnad chains",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zurstadt/isnad2network",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "tqdm>=4.45.0",
    ],
    entry_points={
        "console_scripts": [
            "isnad2network=isnad2network.__main__:main",
        ],
    },
)
