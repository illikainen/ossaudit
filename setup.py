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
    packages=["ossaudit"],
    entry_points={"console_scripts": ["ossaudit = ossaudit.__main__:main"]}
)
