# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import io
import warnings
from typing import IO, List

import dparse
import packaging.version
import pkg_resources


class Package:
    def __init__(self, name: str, version: str) -> None:
        self._name = name
        self._version = version

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def coordinate(self) -> str:
        return "pkg:pypi/{name}@{version}".format(
            name=self.name, version=self.version
        ).lower()


class _Version(packaging.version.Version):  # type: ignore
    def __iadd__(self, num: int) -> "_Version":
        """
        Add a number to the release.
        """
        release = self.release[:-1] + (self.release[-1] + num, )
        self._version = self._version._replace(release=release)  # type: ignore
        return self

    def __isub__(self, num: int) -> "_Version":
        """
        Subtract a number from the release.

        For example:

        - 2.5.0 is decreased to 2.4.9
        - 2018.0 is decreased to 2017.9

        This is obviously quite horrible.  We don't really know (without
        consulting PyPI, which we don't) if these versions are actually
        correct.  The previous versions could just as well be:

        - 2.4.123 or 2.4.3
        - 2017.12 or 2016.1

        This functionality is meant to decrease the version number for
        pre-releases (since OSS Index breaks on them), so imperfections
        are probably alright.
        """
        for _ in range(num):
            release = list(reversed(self.release))
            for i, x in enumerate(release):
                x -= 1
                release[i] = x if x >= 0 else 9
                if x >= 0:
                    self._version = self._version._replace(
                        release=tuple(reversed(release))
                    )
                    break
        return self


def get_from_files(fhs: List[IO[str]]) -> List[Package]:
    """
    Read packages from a list of file handles.

    The version specifier(s) for a package can be written in a number of
    ways:

        pkg
        pkg == 0.1
        pkg > 1, <= 3
        pkg == 1.0pre
        pkg == 1.0pre1.dev2
        pkg > 1!2rc3.dev6
        pkg ===abcd
        pkg != 3
        pkg == 3.2.*
        pkg ~= 1.2

    Also, the `packaging` module accepts bogus version specifiers such
    as:

        pkg >5, <4, ==9, ==1

    For now, the lowest value of the operators ==, ~=, > and >= is used
    as the coordinate version for OSS Index.  Upper bounds and negations
    are ignored.

    Furthermore, only the `final release` part of the version is used
    (see PEP 440).  The reason is that OSS Index doesn't seem to handle
    other parts of a version specifier very well.  For example, the
    coordinate `pkg:pypi/django@1.7.2` gives a number of vulnerabilities
    that `pkg:pypi/django@1.7.2rc1` is missing.
    """
    pkgs = []
    for f in fhs:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            dependencies = dparse.parse(f.read(), path=f.name).dependencies

        for dep in dependencies:
            versions = []
            for spec in dep.specs:
                if spec.operator in ["==", "~=", ">=", ">"]:
                    version = _Version(spec.version.replace("*", "0"))
                    if version.is_prerelease:
                        version -= 1
                    if spec.operator == ">":
                        version += 1
                    versions.append(version)
            version = min(versions or [_Version("0")])
            pkgs.append(Package(dep.name, version.base_version))
    return pkgs


def get_installed() -> List[Package]:
    """
    Retrieve installed packages.
    """
    requirements = "\n".join(
        str(p.as_requirement()) for p in iter(pkg_resources.working_set)
    )
    f = io.StringIO(requirements)
    f.name = "requirements.txt"
    return get_from_files([f])
