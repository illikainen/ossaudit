# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

import shutil
from typing import IO, List

import click
import texttable

from . import audit, packages


@click.command()
@click.option("--installed", "-i", is_flag=True)
@click.option("--file", "-f", "files", multiple=True, type=click.File())
def cli(installed: bool, files: List[IO]) -> None:
    pkgs = []  # type: list
    if installed:
        pkgs += packages.get_installed()
    if files:
        pkgs += packages.get_from_files(files)

    try:
        vulns = audit.components(pkgs)
    except audit.AuditError as e:
        raise click.ClickException(str(e))

    if vulns:
        size = shutil.get_terminal_size()
        table = texttable.Texttable(max_width=size.columns)
        table.header(vulns[0]._fields)
        table.add_rows([v._asdict().values() for v in vulns], False)
        click.echo(table.draw())
