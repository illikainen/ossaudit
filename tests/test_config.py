# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from ossaudit import __project__, config, const


class TestRead(TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config = patch(
            "ossaudit.const.CONFIG",
            Path(self.tmpdir.name).joinpath("x.cfg"),
        )
        self.config.start()

    def tearDown(self) -> None:
        self.config.stop()
        self.tmpdir.cleanup()

    def test_default_not_found(self) -> None:
        self.assertFalse(const.CONFIG.exists())
        self.assertIsInstance(config.read(), config.Config)

    def test_not_found(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            pass

        with self.assertRaises(config.ConfigError):
            config.read(Path(tmp.name))

    def test_error(self) -> None:
        with const.CONFIG.open("w") as f:
            f.write("x=y")

        with self.assertRaises(config.ConfigError):
            config.read()

    def test_missing_username(self) -> None:
        cfg = config.read()
        self.assertIsNone(cfg.username)

    def test_username(self) -> None:
        with const.CONFIG.open("w") as f:
            f.write("[{}]\n username=abcd".format(__project__))

        cfg = config.read()
        self.assertEqual(cfg.username, "abcd")

    def test_missing_token(self) -> None:
        cfg = config.read()
        self.assertIsNone(cfg.token)

    def test_token(self) -> None:
        with const.CONFIG.open("w") as f:
            f.write("[{}]\n token=abcd".format(__project__))

        cfg = config.read()
        self.assertEqual(cfg.token, "abcd")

    def test_missing_columns(self) -> None:
        cfg = config.read()
        columns = cfg.columns

        self.assertTrue(len(columns))
        for c in columns:
            self.assertIsInstance(c, str)

    def test_columns(self) -> None:
        with const.CONFIG.open("w") as f:
            f.write("[{}]\n columns =  aaa,  Bbb  , CCC\n".format(__project__))

        cfg = config.read()
        self.assertEqual(cfg.columns, ["aaa", "Bbb", "CCC"])
