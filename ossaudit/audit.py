# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from collections import namedtuple
from typing import List
from urllib.parse import urljoin

import requests

from . import const, packages

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


def components(pkgs: List[packages.Package]) -> List[Vulnerability]:
    if not pkgs:
        return []

    url = urljoin(const.API, const.COMPONENT_REPORT)
    vulns = []

    for i in range(0, len(pkgs), const.MAX_PACKAGES):
        coordinates = [p.coordinate for p in pkgs[i:i + const.MAX_PACKAGES]]
        res = requests.post(url, json={"coordinates": coordinates})

        if res.status_code == 200:
            for pkg in res.json():
                name, version = next(
                    ([p.name, p.version]
                     for p in pkgs
                     if p.coordinate == pkg.get("coordinates")),
                    ["", ""],
                )

                for vuln in pkg.get("vulnerabilities", []):
                    vulns.append(
                        Vulnerability(
                            name=name,
                            version=version,
                            id=vuln.get("id", ""),
                            cve=vuln.get("cve", ""),
                            cvss_score=vuln.get("cvssScore", ""),
                            title=vuln.get("title", ""),
                            description=vuln.get("description", ""),
                        )
                    )
        elif res.status_code == 429:
            raise AuditError("too many requests")
        else:
            raise AuditError("unknown status code {}".format(res.status_code))
    return vulns
