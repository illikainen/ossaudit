# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import json
import os
import time
from typing import Dict, Optional
from unittest.mock import ANY, patch

from ossaudit import audit, packages

from .helpers import PatchedTestCase


class TestComponents(PatchedTestCase):
    def test_ok(self) -> None:
        pkgs = [
            ("django", "2.2", ()),
            ("requests", "0.10.0", ("CVE-2014-1830", "CVE-2014-1829")),
            ("pyyaml", "3.13", ("CVE-2017-18342", )),
        ]  # type: list

        with patch("requests.post") as mock:
            mock.return_value.status_code = 200
            with open(os.path.join("tests", "data", "vulns01.json")) as f:
                mock.return_value.json.return_value = json.load(f)

            vulns = audit.components([
                packages.Package(n, v) for n, v, _ in pkgs
            ])
            self.assertEqual(len(vulns), 3)

            for name, version, cves in pkgs:
                for cve in cves:
                    vuln = next(
                        v for v in vulns if v.name == name
                        and v.version == version and v.cve == cve
                    )
                    self.assertIsInstance(vuln, audit.Vulnerability)

    def test_max_packages(self) -> None:
        pkgs = [
            packages.Package(n, v) for n, v in [
                ("django", "2.2"),
                ("pylint", "4.1"),
                ("pyyaml", "3.13"),
                ("requests", "0.10.0"),
                ("yapf", "1.2.3"),
            ]
        ]
        max_packages = 2

        with patch("requests.post") as mock:
            mock.return_value.status_code = 200
            with patch("ossaudit.const.MAX_PACKAGES", max_packages):
                audit.components(pkgs)
            self.assertEqual(mock.call_count, 3)

            calls = []
            for i in range(0, len(pkgs), max_packages):
                coords = [p.coordinate for p in pkgs[i:i + max_packages]]
                kw = {"auth": None, "json": {"coordinates": coords}}
                calls.append((ANY, kw))
            self.assertEqual(mock.call_args_list, calls)

    def test_no_packages(self) -> None:
        self.assertEqual(audit.components([]), [])

    def test_missing_fields(self) -> None:
        with patch("requests.post") as mock:
            mock.return_value.status_code = 200
            pkgs = [{"vulnerabilities": [{}]}]  # type: list
            mock.return_value.json.return_value = pkgs
            vulns = audit.components([packages.Package("a", "1")])

            self.assertEqual(len(vulns), 1)
            self.assertEqual(vulns[0].name, "unknown")
            self.assertEqual(vulns[0].version, "0")

    def test_too_many_requests(self) -> None:
        with patch("requests.post") as mock:
            mock.return_value.status_code = 429

            with self.assertRaises(audit.AuditError):
                audit.components([packages.Package("a", "1")])

    def test_unknown_status(self) -> None:
        with patch("requests.post") as mock:
            mock.return_value.status_code = 501

            with self.assertRaises(audit.AuditError):
                audit.components([packages.Package("a", "1")])

    def test_from_cache(self) -> None:
        pkgs = [
            packages.Package(n, v) for n, v in [
                ("django", "2.2"),
                ("pylint", "4.1"),
                ("pyyaml", "3.13"),
                ("requests", "0.10.0"),
                ("yapf", "1.2.3"),
            ]
        ]

        with patch("requests.post") as post:
            post.return_value.status_code = 200

            def getfun(coordinate: str) -> Optional[Dict]:
                return {
                    "coordinates": "pkg:pypi/pyyaml@3.13",
                    "time": time.time(),
                    "vulnerabilities": [{
                        "id": "123",
                    }]
                } if coordinate == "pkg:pypi/pyyaml@3.13" else None

            with patch("ossaudit.cache.get", wraps=getfun) as get:
                with patch("ossaudit.const.MAX_PACKAGES", 1):
                    vulns = audit.components(pkgs)

                    self.assertEqual(len(vulns), 1)
                    self.assertEqual(get.call_count, len(pkgs))
                    self.assertEqual(post.call_count, len(pkgs) - 1)

                    calls = [(
                        ANY, {
                            "auth": None,
                            "json": {
                                "coordinates": [p.coordinate]
                            }
                        }
                    ) for p in pkgs if p.coordinate != "pkg:pypi/pyyaml@3.13"]
                    self.assertEqual(post.call_args_list, calls)

    def test_save_cache(self) -> None:
        pkgs = [
            packages.Package(n, v) for n, v in [
                ("django", "2.2"),
                ("pyyaml", "3.13"),
                ("requests", "0.10.0"),
            ]
        ]

        with patch("requests.post") as post:
            post.return_value.status_code = 200
            with open(os.path.join("tests", "data", "vulns01.json")) as f:
                post.return_value.json.return_value = json.load(f)

            with patch("ossaudit.cache.save") as save:
                audit.components(pkgs)
                self.assertEqual(save.call_count, len(pkgs))

    def test_invalid_credentials(self) -> None:
        with patch("requests.post") as post:
            post.return_value.status_code = 401
            with self.assertRaises(audit.AuditError) as ctx:
                audit.components([packages.Package("x", "1")])
            self.assertTrue("credentials" in str(ctx.exception))

    def test_credentials(self) -> None:
        with patch("requests.post") as post:
            post.return_value.status_code = 200
            audit.components([packages.Package("x", "1")], "usr", "token")
            calls = [(ANY, {"auth": ("usr", "token"), "json": ANY})]
            self.assertEqual(post.call_args_list, calls)

    def test_missing_username(self) -> None:
        with patch("requests.post") as post:
            post.return_value.status_code = 200
            audit.components([packages.Package("x", "1")], None, "token")
            calls = [(ANY, {"auth": None, "json": ANY})]
            self.assertEqual(post.call_args_list, calls)

    def test_missing_token(self) -> None:
        with patch("requests.post") as post:
            post.return_value.status_code = 200
            audit.components([packages.Package("x", "1")], "usr", None)
            calls = [(ANY, {"auth": None, "json": ANY})]
            self.assertEqual(post.call_args_list, calls)
