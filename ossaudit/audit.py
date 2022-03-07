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
        "coordinate",
        "id",
        "cve",
        "cvss_score",
        "cvss_vector",
        "short_title",
        "title",
        "description",
        "reference",
        "external_references"
    ]
)


class AuditError(Exception):
    pass


def components(
        pkgs: List[packages.Package],
        username: Optional[str] = None,
        token: Optional[str] = None,
        ignore_cache: bool = False,
) -> List[Vulnerability]:
    old = list(_from_cache(pkgs, ignore_cache))
    new = list(_from_api([
        p for p in pkgs
        if not any(p.coordinate == o.coordinate for o, _ in old)
    ], ignore_cache, username, token))  # yapf: disable
    return [
        _transform(p, vuln)
        for p, e in new + old
        for vuln in e.get("vulnerabilities", [])
    ]


def _from_api(
        pkgs: List[packages.Package],
        ignore_cache: bool,
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
                if not ignore_cache:
                    cache.save(entry)
                yield (pkg, entry)
        elif res.status_code == 401:
            raise AuditError("invalid credentials")
        elif res.status_code == 429:
            raise AuditError("too many requests")
        else:
            raise AuditError("unknown status code {}".format(res.status_code))


def _from_cache(pkgs: List[packages.Package], ignore_cache: bool) -> Generator:
    if not ignore_cache:
        for pkg in pkgs:
            entry = cache.get(pkg.coordinate)
            if entry:
                yield (pkg, entry)


def _transform(pkg: packages.Package, vuln: Dict) -> Vulnerability:
    return Vulnerability(
        name=pkg.name,
        version=pkg.version,
        id=vuln.get("id", ""),
        coordinate=pkg.coordinate,
        short_title=vuln.get("displayName", ""),
        cve=vuln.get("cve", ""),
        cvss_score=vuln.get("cvssScore", ""),
        cvss_vector=vuln.get("cvssVector", ""),
        title=vuln.get("title", ""),
        description=vuln.get("description", ""),
        reference=vuln.get("reference", ""),
        external_references=vuln.get("externalReferences", [])
    )
