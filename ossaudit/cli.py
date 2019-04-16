# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import shutil
from pathlib import Path
from typing import IO, List

import click
import texttable

from . import audit, config, packages


@click.command()
@click.option(
    "--config-file",
    "-c",
    type=Path,
    help="Configuration file.",
)
@click.option(
    "--installed",
    "-i",
    is_flag=True,
    help="Audit installed packages.",
)
@click.option(
    "--file",
    "-f",
    "files",
    multiple=True,
    type=click.File(),
    help="Audit packages in file (can be specified multiple times).",
)
def cli(config_file: Path, installed: bool, files: List[IO]) -> None:
    pkgs = []  # type: list
    if installed:
        pkgs += packages.get_installed()
    if files:
        pkgs += packages.get_from_files(files)

    try:
        cfg = config.read(config_file)
    except config.ConfigError as e:
        raise click.ClickException(str(e))

    try:
        vulns = audit.components(pkgs, cfg.username, cfg.token)
    except audit.AuditError as e:
        raise click.ClickException(str(e))

    if vulns:
        size = shutil.get_terminal_size()
        table = texttable.Texttable(max_width=size.columns)
        table.header(cfg.columns)
        table.add_rows([[getattr(v, c.lower(), "")
                         for c in cfg.columns]
                        for v in vulns], False)
        click.echo(table.draw())
        raise click.ClickException(
            "{} vulnerable package(s)".format(len(vulns))
        )
