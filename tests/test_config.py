# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from ossaudit import config, const


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
