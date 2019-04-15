# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause
#
# pylint: disable=protected-access

import io
import json
from unittest import TestCase
from unittest.mock import patch

import pkg_resources

from ossaudit import packages


class TestVersion(TestCase):
    def test_arithmetic(self) -> None:
        versions = [
            ("0", 1, "1", "0"),
            ("0", 123, "123", "0"),
            ("0.0.0", 1, "0.0.1", "0.0.0"),
            ("0.0.9", 9, "0.0.18", "0.0.0"),
            ("1.1.1", 1, "1.1.2", "1.1.0"),
            ("1.1.1", 5, "1.1.6", "1.0.6"),
            ("1.16.1", 1, "1.16.2", "1.16.0"),
            ("100", 1, "101", "99"),
            ("9.9.10", 1, "9.9.11", "9.9.9"),
            ("9.9.9", 1, "9.9.10", "9.9.8"),
        ]

        for before, num, add, sub in versions:
            v = packages._Version(before)
            v += num
            self.assertEqual(v.base_version, add)

            v = packages._Version(before)
            v -= num
            self.assertEqual(v.base_version, sub)


class TestCoordinate(TestCase):
    def test_downcase(self) -> None:
        p = packages.Package("NAMe", "1.2.3")
        self.assertEqual(p.coordinate, "pkg:pypi/name@1.2.3")


class TestGetFromFiles(TestCase):
    def test_requirements(self) -> None:
        pkgs = [
            ("django == 2.*", "django@2.0"),
            ("mccabe >= 9.9.9rc1", "mccabe@9.9.8"),
            ("munch >= 9.9.10rc1", "munch@9.9.9"),
            ("mypy >= 10.10.10rc1", "mypy@10.10.9"),
            ("numpy > 1.16.1, > 1.15.4, == 1.16.0", "numpy@1.15.5"),
            ("packaging == 2.0.0b3", "packaging@1.9.9"),
            ("pkg-resources == 1.3.0", "pkg-resources@1.3.0"),
            ("pycodestyle == 1.3.0b2", "pycodestyle@1.2.9"),
            ("pydocstyle > 1.2.9", "pydocstyle@1.2.10"),
            ("pyflakes > 0.0.0b3", "pyflakes@0.0.1"),
            ("pyparsing >= 0b2", "pyparsing@0"),
            ("pytz ~= 2018.9", "pytz@2018.9"),
            ("pyyaml > 5.1b5, < 8", "pyyaml@5.1"),
            ("requests == 2.21.0", "requests@2.21.0"),
            ("scipy == 1.*.1", "scipy@1.0.1"),
            ("scrapy >= 1.6.0", "scrapy@1.6.0"),
            ("setuptools < 5", "setuptools@0"),
            ("six == 1.2.3 --hash=sha256:abcd", "six@1.2.3"),
            ("snowballstemmer == 0.0.0b3", "snowballstemmer@0.0.0"),
            ("twisted", "twisted@0"),
            ("yapf >= 5.1b5", "yapf@5.0"),
        ]
        f = io.StringIO("\n".join(p for p, _ in pkgs))
        f.name = "requirements.txt"

        got = [p.coordinate for p in packages.get_from_files([f])]
        want = ["pkg:pypi/{}".format(p) for _, p in pkgs]
        self.assertEqual(sorted(got), sorted(want))

    def test_pipfile(self) -> None:
        pkgs = [
            ("docutils = '> 0.6.5rc5'", "docutils@0.6.5"),
            ("flake8 = '==0.6.5'", "flake8@0.6.5"),
            ("pysocks = '>= 0.6.5rc5'", "pysocks@0.6.4"),
            ("pytest = '>=2.8.0,<4.1'", "pytest@2.8.0"),
            ("pytest-mock = '>2.8.0,<4.1'", "pytest-mock@2.8.1"),
            ("requests = '>5.1, >=4.2, >=3.3, >9.4'", "requests@3.3"),
            ("sphinx = '==0.6.5rc5'", "sphinx@0.6.4"),
            ("tox = '*'", "tox@0"),
        ]
        f = io.StringIO("[packages]\n{}".format("\n".join(p for p, _ in pkgs)))
        f.name = "Pipfile"

        got = [p.coordinate for p in packages.get_from_files([f])]
        want = ["pkg:pypi/{}".format(p) for _, p in pkgs]
        self.assertEqual(sorted(got), sorted(want))

    def test_pipfile_lock(self) -> None:
        pkgs = [
            ("docutils", "> 0.6.5rc5", "docutils@0.6.5"),
            ("pytest", "==2.8.0", "pytest@2.8.0"),
        ]

        entries = {n: {"version": v, "hashes": []} for n, v, *_ in pkgs}
        f = io.StringIO(json.dumps({"default": entries}))
        f.name = "Pipfile.lock"

        got = [p.coordinate for p in packages.get_from_files([f])]
        want = ["pkg:pypi/{}".format(p) for *_, p in pkgs]
        self.assertEqual(sorted(got), sorted(want))

    def test_tox(self) -> None:
        pkgs = [
            ("pylint", "pylint@0"),
            ("pytest >= 3.0.0, <4", "pytest@3.0.0"),
            ("pytz ~= 2018.9", "pytz@2018.9"),
        ]

        f = io.StringIO("[x]\ndeps={}".format("\n ".join(p for p, _ in pkgs)))
        f.name = "tox.ini"

        got = [p.coordinate for p in packages.get_from_files([f])]
        want = ["pkg:pypi/{}".format(p) for _, p in pkgs]
        self.assertEqual(sorted(got), sorted(want))

    def test_multiple(self) -> None:
        r = [
            ("pytz > 2018.9", "pytz@2018.10"),
            ("requests == 1.2", "requests@1.2"),
        ]
        rf = io.StringIO("\n".join(x for x, _ in r))
        rf.name = "requirements.txt"

        p = [
            ("pysocks = '>= 0.6.5rc5'", "pysocks@0.6.4"),
            ("pytest = '>2.8.0'", "pytest@2.8.1"),
        ]
        pf = io.StringIO("[packages]\n{}".format("\n".join(x for x, _ in p)))
        pf.name = "Pipfile"

        t = [
            ("docutils >3.0", "docutils@3.1"),
            ("pylint", "pylint@0"),
        ]
        tf = io.StringIO("[x]\ndeps={}".format("\n ".join(x for x, _ in t)))
        tf.name = "tox.ini"

        got = [p.coordinate for p in packages.get_from_files([rf, pf, tf])]
        want = ["pkg:pypi/{}".format(x) for x in [y for *_, y in r + p + t]]
        self.assertEqual(sorted(got), sorted(want))


class TestGetInstalled(TestCase):
    def test_installed(self) -> None:
        pkgs = [
            ("pylint", "0rc2", "pylint@0"),
            ("pytest", "1.2.3", "pytest@1.2.3"),
            ("pytz", "2018.12", "pytz@2018.12"),
            ("requests", "5.6.7rc1", "requests@5.6.6"),
            ("tox", "1.9.0rc7", "tox@1.8.9"),
        ]

        with patch("pkg_resources.working_set") as mock:
            mock.__iter__.return_value = [
                pkg_resources.Distribution(project_name=n, version=v)
                for n, v, _ in pkgs
            ]
            got = [p.coordinate for p in packages.get_installed()]
            want = ["pkg:pypi/{}".format(p) for *_, p in pkgs]
            self.assertEqual(sorted(got), sorted(want))
