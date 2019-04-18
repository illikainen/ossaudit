# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from ossaudit import const, option


class PatchedTestCase(TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()

        self.cache = patch(
            "ossaudit.const.CACHE",
            Path(self.tmpdir.name).joinpath("cache.json"),
        )
        self.cache.start()

        # Bleh.  Simply mocking const.CONFIG isn't enough because it's
        # already referenced as the `default` argument for --config.
        orig_config = const.CONFIG
        orig_config_init = option.Config.__init__

        def config_init(self: option.Config, path: Path) -> None:
            if path == orig_config:
                path = const.CONFIG
            return orig_config_init(self, path)

        self.config_init = patch(
            "ossaudit.option.Config.__init__",
            config_init,
        )
        self.config_init.start()

        self.config = patch(
            "ossaudit.const.CONFIG",
            Path(self.tmpdir.name).joinpath("config.cfg"),
        )
        self.config.start()

    def tearDown(self) -> None:
        self.cache.stop()
        self.config_init.stop()
        self.config.stop()
        self.tmpdir.cleanup()
