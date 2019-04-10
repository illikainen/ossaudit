# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from unittest import TestCase

from click.testing import CliRunner

from ossaudit import cli


class TestCli(TestCase):
    def test_run(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli.cli)
        self.assertEqual(result.exit_code, 0)
