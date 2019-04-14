# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from pathlib import Path

from . import __project__

API = "https://ossindex.sonatype.org/api/v3/"
COMPONENT_REPORT = "component-report"
MAX_PACKAGES = 128
CACHE = Path.home().joinpath(".cache", __project__, "cache.json")
CACHE_TIME = 60 * 60 * 12
