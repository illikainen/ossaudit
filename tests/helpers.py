# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


class PatchedTestCase(TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()

        self.cache = patch(
            "ossaudit.const.CACHE",
            Path(self.tmpdir.name).joinpath("cache.json"),
        )
        self.cache.start()

        self.config = patch(
            "ossaudit.const.CONFIG",
            Path(self.tmpdir.name).joinpath("config.cfg"),
        )
        self.config.start()

    def tearDown(self) -> None:
        self.cache.stop()
        self.config.stop()
        self.tmpdir.cleanup()
