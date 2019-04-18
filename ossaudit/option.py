# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import configparser
import re
from pathlib import Path
from typing import Any, Callable, Tuple, Union

import click

from . import __project__


class Option(click.Option):
    def full_process_value(self, ctx: click.Context, value: Any) -> Any:
        """
        Process a value.

        Resolution order:

        1. From command-line arguments.
        2. From `default_map`.
        3. From environment variables.
        4. From configuration files.
        5. From the `default` keyword argument.
        """
        if not value:
            name = self.name.replace("_", "-")
            config = ctx.params.get("config")
            value = config and config.get_value(name, self.multiple)
        return super().full_process_value(ctx, value)


class Config(configparser.ConfigParser):
    def __init__(self, path: Path) -> None:
        super().__init__()
        try:
            self.read(str(path))
        except configparser.Error as e:
            raise click.ClickException(str(e))

    def get_value(self, name: str, multiple: bool) -> Union[str, Tuple, None]:
        value = self.get(__project__, name, fallback=None)  # type: ignore
        if value and multiple:
            return tuple(v.strip() for v in re.split("[\n\r,]", value) if v)
        return value


def add(*param_decls: str, **attrs: Any) -> Callable:
    """
    Add an option with the extended `Option` class.
    """
    return click.option(*param_decls, **attrs, cls=Option)  # type: ignore
