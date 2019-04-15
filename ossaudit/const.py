# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from pathlib import Path

import appdirs

from . import __project__

API = "https://ossindex.sonatype.org/api/v3/"
COMPONENT_REPORT = "component-report"
MAX_PACKAGES = 128
CONFIG = Path(appdirs.user_config_dir(__project__)).joinpath("config.ini")
CACHE = Path(appdirs.user_cache_dir(__project__)).joinpath("cache.json")
CACHE_TIME = 60 * 60 * 12
