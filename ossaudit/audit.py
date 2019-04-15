# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from collections import namedtuple
from typing import Dict, Generator, List, Optional
from urllib.parse import urljoin

import requests

from . import cache, const, packages

Vulnerability = namedtuple(
    "Vulnerability", [
        "name",
        "version",
        "id",
        "cve",
        "cvss_score",
        "title",
        "description",
    ]
)


class AuditError(Exception):
    pass


def components(
        pkgs: List[packages.Package],
        username: Optional[str] = None,
        token: Optional[str] = None,
) -> List[Vulnerability]:
    old = list(_from_cache(pkgs))
    new = list(_from_api([
        p for p in pkgs
        if not any(p.coordinate == o.coordinate for o, _ in old)
    ], username, token))  # yapf: disable
    return [
        _transform(p, vuln)
        for p, e in new + old
        for vuln in e.get("vulnerabilities", [])
    ]


def _from_api(
        pkgs: List[packages.Package],
        username: Optional[str] = None,
        token: Optional[str] = None,
) -> Generator:
    url = urljoin(const.API, const.COMPONENT_REPORT)
    auth = (username, token) if username and token else None

    for i in range(0, len(pkgs), const.MAX_PACKAGES):
        coordinates = [p.coordinate for p in pkgs[i:i + const.MAX_PACKAGES]]
        res = requests.post(url, auth=auth, json={"coordinates": coordinates})

        if res.status_code == 200:
            for entry in res.json():
                pkg = next((
                    p for p in pkgs
                    if p.coordinate == entry.get("coordinates")
                ), packages.Package("unknown", "0"))
                cache.save(entry)
                yield (pkg, entry)
        elif res.status_code == 401:
            raise AuditError("invalid credentials")
        elif res.status_code == 429:
            raise AuditError("too many requests")
        else:
            raise AuditError("unknown status code {}".format(res.status_code))


def _from_cache(pkgs: List[packages.Package]) -> Generator:
    for pkg in pkgs:
        entry = cache.get(pkg.coordinate)
        if entry:
            yield (pkg, entry)


def _transform(pkg: packages.Package, vuln: Dict) -> Vulnerability:
    return Vulnerability(
        name=pkg.name,
        version=pkg.version,
        id=vuln.get("id", ""),
        cve=vuln.get("cve", ""),
        cvss_score=vuln.get("cvssScore", ""),
        title=vuln.get("title", ""),
        description=vuln.get("description", ""),
    )
