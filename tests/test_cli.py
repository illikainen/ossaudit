# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import tempfile
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from ossaudit import audit, cli, packages


class TestCli(TestCase):
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
                result = runner.invoke(cli.cli, ["--installed"])
                self.assertEqual(result.exit_code, 0)
                components.assert_called_with(pkgs)

    def test_files(self) -> None:
        runner = CliRunner()

        pkgs = [
            packages.Package("a", "1.1"),
            packages.Package("b", "2.2"),
        ]

        with patch("ossaudit.packages.get_from_files") as get_from_files:
            get_from_files.return_value = pkgs
            with patch("ossaudit.audit.components") as components:
                with tempfile.NamedTemporaryFile() as tmp:
                    result = runner.invoke(cli.cli, ["--file", tmp.name])
                    self.assertEqual(result.exit_code, 0)
                    components.assert_called_with(pkgs)

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
                    with tempfile.NamedTemporaryFile() as tmp:
                        result = runner.invoke(
                            cli.cli, ["--installed", "--file", tmp.name]
                        )
                        self.assertEqual(result.exit_code, 0)
                        components.assert_called_with(installed + files)

    def test_audit_error(self) -> None:
        with patch("ossaudit.packages.get_installed") as get_installed:
            get_installed.return_value = []
            with patch("ossaudit.audit.components") as components:
                components.side_effect = audit.AuditError("xyz")
                runner = CliRunner()
                result = runner.invoke(cli.cli, ["--installed"])
                self.assertTrue("xyz" in result.output)
                self.assertNotEqual(result.exit_code, 0)
