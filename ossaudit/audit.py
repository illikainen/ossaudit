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
        ignore_cache: bool = False,
) -> List[Vulnerability]:
    old = list(_from_cache(pkgs, ignore_cache))
    new = list(_from_api([
        p for p in pkgs
        if not any(p.coordinate == o.coordinate for o, _ in old)
    ], ignore_cache, username, token))  # yapf: disable
    return (new + old)


def flatten_vuln_list(vulns):
    return [
        _transform(p, vuln)
        for p, c in vulns       # package, coordinate from ossindex
        for vuln in c.get("vulnerabilities", [])
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
        cve=vuln.get("cve", ""),
        cvss_score=vuln.get("cvssScore", ""),
        title=vuln.get("title", ""),
        description=vuln.get("description", ""),
    )


def create_report(vulns: List):
    """Create a list of dict objects as returned by the SonarType OSSIndex scanner. The list contains on
    dict per python package found and queried against the database. The packages "vulnerabilities" field
    is an list with all vulnerabilites for this package. The vulnerability list can be empty.

    Parameters
    ----------
    vulns : List with a tuple of the package object and the SonarType response for this package

    Returns
    -------
    list - a list of scan coordinates (packages) and a list with their vulnerabilities (if any)
    """
    out_list = []
    for p, c in vulns:
        del c["time"]
        out_list.append(c)
    return out_list

def create_vuln_list(vulns: List, columns: List):
    """Create a list of dicts from the vulnerability tuples containing only the column names requests

    Parameters
    ----------
    vulns : List list of all vulnerabilities found
    columns : List list of all columns(fields) needed from the vulnerability for output

    Returns
    -------
    list - a list of vulnerability dictionaries containing the columns given only
    """
    out_list = []
    for v in vulns:
        v_dict = v._asdict()
        v_out = {}
        for c in columns:
            v_out[c] = v_dict[c] if c in v_dict else ""
        out_list.append(v_out)
    return out_list
