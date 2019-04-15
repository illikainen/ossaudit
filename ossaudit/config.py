# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import configparser
from pathlib import Path
from typing import List, Optional

from . import __project__, const


class ConfigError(Exception):
    pass


class Config(configparser.ConfigParser):
    @property
    def username(self) -> Optional[str]:
        return self._get_optional("username")

    @property
    def token(self) -> Optional[str]:
        return self._get_optional("token")

    @property
    def columns(self) -> List[str]:
        cols = self._get_optional("columns") or "name, version, title"
        return [c.strip() for c in cols.split(",")]

    def _get_optional(self, option: str) -> Optional[str]:
        try:
            return self.get(__project__, option)
        except configparser.Error:
            return None


def read(path: Optional[Path] = None) -> Config:
    """
    Read a configuration file.

    A default path is used if `path` is not specified.  In that case,
    OSError exceptions are ignored.
    """
    cfg = Config()
    try:
        with (path or const.CONFIG).open() as f:
            cfg.read_file(f)
    except configparser.Error as e:
        raise ConfigError(e)
    except OSError as e:
        if path:
            raise ConfigError("{}: {}".format(e.filename, e.strerror))
    return cfg
