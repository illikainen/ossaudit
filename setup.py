#!/usr/bin/env python3

from setuptools import setup

import ossaudit

setup(
    name=ossaudit.__project__,
    version=ossaudit.__version__,
    author="Hans Jerry Illikainen",
    author_email="hji@dyntopia.com",
    license="BSD-2-Clause",
    description="Audit python packages for known vulnerabilities",
    long_description="See https://github.com/dyntopia/ossaudit",
    url="https://github.com/dyntopia/ossaudit",
    python_requires=">=3.5",
    entry_points={
        "console_scripts": ["ossaudit = ossaudit.__main__:main"],
    },
    packages=[
        "ossaudit",
    ],
    install_requires=[
        "appdirs",
        "click",
        "dparse",
        "requests",
        "texttable",
    ],
    tests_requires=[
        "coverage",
        "isort",
        "mccabe",
        "mypy",
        "pycodestyle",
        "pyflakes",
        "pylint",
        "pylint-quotes",
        "yapf",
    ],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Security",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
)
