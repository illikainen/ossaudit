# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import tempfile
from functools import partial
from unittest.mock import ANY, patch

from click.testing import CliRunner

from ossaudit import __project__, audit, cli, const, packages

from .helpers import PatchedTestCase

Vulnerability = partial(
    audit.Vulnerability,
    **{f: f
       for f in audit.Vulnerability._fields},
)


class TestCli(PatchedTestCase):
    def test_run(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli.cli)
        self.assertEqual(result.exit_code, 0)

    def test_installed(self) -> None:
        runner = CliRunner()

        pkgs = [
            packages.Package("a", "1.1"),
            packages.Package("b", "2.2"),
        ]

        with patch("ossaudit.packages.get_installed") as get_installed:
            get_installed.return_value = pkgs
            with patch("ossaudit.audit.components") as components:
                components.return_value = []
                result = runner.invoke(cli.cli, ["--installed"])
                self.assertEqual(result.exit_code, 0)
                components.assert_called_with(pkgs, None, None)

    def test_files(self) -> None:
        runner = CliRunner()

        pkgs = [
            packages.Package("a", "1.1"),
            packages.Package("b", "2.2"),
        ]

        with patch("ossaudit.packages.get_from_files") as get_from_files:
            get_from_files.return_value = pkgs
            with patch("ossaudit.audit.components") as components:
                components.return_value = []
                with tempfile.NamedTemporaryFile() as tmp:
                    result = runner.invoke(cli.cli, ["--file", tmp.name])
                    self.assertEqual(result.exit_code, 0)
                    components.assert_called_with(pkgs, None, None)

    def test_mixed(self) -> None:
        runner = CliRunner()

        files = [
            packages.Package("c", "1.1"),
            packages.Package("d", "2.2"),
        ]

        installed = [
            packages.Package("a", "1.1"),
            packages.Package("b", "2.2"),
        ]

        with patch("ossaudit.packages.get_from_files") as get_from_files:
            get_from_files.return_value = files
            with patch("ossaudit.packages.get_installed") as get_installed:
                get_installed.return_value = installed

                with patch("ossaudit.audit.components") as components:
                    components.return_value = []
                    with tempfile.NamedTemporaryFile() as tmp:
                        result = runner.invoke(
                            cli.cli, ["--installed", "--file", tmp.name]
                        )
                        self.assertEqual(result.exit_code, 0)
                        components.assert_called_with(
                            installed + files,
                            None,
                            None,
                        )

    def test_credentials(self) -> None:
        with const.CONFIG.open("w") as f:
            f.write("[{}]\n username=abc \n token=xyz".format(__project__))

        runner = CliRunner()
        with patch("ossaudit.packages.get_installed") as get_installed:
            get_installed.return_value = [packages.Package("a", "1.1")]
            with patch("ossaudit.audit.components") as components:
                components.return_value = []
                result = runner.invoke(cli.cli, ["--installed"])
                self.assertEqual(result.exit_code, 0)
                components.assert_called_with(ANY, "abc", "xyz")

    def test_audit_error(self) -> None:
        with patch("ossaudit.packages.get_installed") as get_installed:
            get_installed.return_value = []
            with patch("ossaudit.audit.components") as components:
                components.side_effect = audit.AuditError("xyz")
                runner = CliRunner()
                result = runner.invoke(cli.cli, ["--installed"])
                self.assertTrue("xyz" in result.output)
                self.assertNotEqual(result.exit_code, 0)

    def test_config_error(self) -> None:
        with const.CONFIG.open("w") as f:
            f.write("...")

        runner = CliRunner()
        result = runner.invoke(cli.cli)
        self.assertNotEqual(result.exit_code, 0)

    def test_have_vulnerabilities(self) -> None:
        with patch("ossaudit.packages.get_installed"):
            with patch("ossaudit.audit.components") as components:
                components.return_value = [Vulnerability()]
                runner = CliRunner()
                result = runner.invoke(cli.cli, ["--installed"])
                self.assertNotEqual(result.exit_code, 0)
                self.assertTrue("1 vulnerabilities" in result.output)

    def test_no_vulnerabilities(self) -> None:
        with patch("ossaudit.packages.get_installed"):
            with patch("ossaudit.audit.components") as components:
                components.return_value = []
                runner = CliRunner()
                result = runner.invoke(cli.cli, ["--installed"])
                self.assertEqual(result.exit_code, 0)
                self.assertTrue("0 vulnerabilities" in result.output)

    def test_ignore_some_ids_arg(self) -> None:
        vulns = [
            Vulnerability(id="0"),
            Vulnerability(id="1"),
            Vulnerability(id="2"),
            Vulnerability(id="10"),
            Vulnerability(id="20"),
        ]

        with patch("ossaudit.packages.get_installed"):
            with patch("ossaudit.audit.components") as components:
                components.return_value = vulns
                runner = CliRunner()
                args = ["--installed", "--ignore-id", "1", "--ignore-id", "20"]
                result = runner.invoke(cli.cli, args)
                self.assertNotEqual(result.exit_code, 0)
                self.assertTrue("3 vulnerabilities" in result.output)

    def test_ignore_all_ids_arg(self) -> None:
        vulns = [
            Vulnerability(id="0"),
            Vulnerability(id="1"),
            Vulnerability(id="2"),
        ]

        with patch("ossaudit.packages.get_installed"):
            with patch("ossaudit.audit.components") as components:
                components.return_value = vulns
                runner = CliRunner()
                args = [
                    "--installed",
                    "--ignore-id",
                    "0",
                    "--ignore-id",
                    "1",
                    "--ignore-id",
                    "2",
                ]
                result = runner.invoke(cli.cli, args)
                self.assertEqual(result.exit_code, 0)
                self.assertTrue("0 vulnerabilities" in result.output)
