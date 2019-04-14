# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import configparser
from pathlib import Path
from typing import Optional

from . import const


class ConfigError(Exception):
    pass


class Config(configparser.ConfigParser):
    pass


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
