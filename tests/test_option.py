# Copyright (c) 2019, Hans Jerry Illikainen <hji@dyntopia.com>
#
# SPDX-License-Identifier: BSD-2-Clause

from typing import Any, Tuple
from unittest import TestCase

import click
from click.testing import CliRunner

from ossaudit import __project__, option


class TestOption(TestCase):
    def test_without_config(self) -> None:
        @click.command()
        @option.add("--abcd")
        def fun(**kwargs: Any) -> None:
            self.assertIsNone(kwargs["abcd"])

        runner = CliRunner()
        result = runner.invoke(fun)
        self.assertEqual(result.exit_code, 0)

    def test_missing_config(self) -> None:
        @click.command()
        @option.add_config("--config", default="x")
        @option.add("--abcd")
        def fun(**kwargs: Any) -> None:
            self.assertIsNone(kwargs["abcd"])

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(fun)
            self.assertEqual(result.exit_code, 0)

    def test_invalid_config(self) -> None:
        @click.command()
        @option.add_config("--config")
        def fun(**_kwargs: Any) -> None:
            pass

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("x.ini", "w") as f:
                f.write("asdf=xyz")

            result = runner.invoke(fun, ["--config", "x.ini"])
            self.assertEqual(result.exc_info[0], SystemExit)  # type: ignore
            self.assertNotEqual(result.exit_code, 0)

    def test_with_config(self) -> None:
        @click.command()
        @option.add_config("--config")
        @option.add("--string")
        @option.add("--string-empty")
        @option.add("--multi-string", multiple=True)
        @option.add("--multi-string-empty", multiple=True)
        @option.add("--boolean", is_flag=True)
        @option.add("--boolean-empty", is_flag=True)
        @option.add("--integer", type=int)
        @option.add("--integer-empty", type=int)
        @option.add("--multi-integer", type=int, multiple=True)
        @option.add("--multi-integer-empty", type=int, multiple=True)
        @option.add("--f", type=click.File())
        @option.add("--multi-f", type=click.File(), multiple=True)
        def fun(**kwargs: Any) -> None:
            self.assertEqual(kwargs["string"], "xyz")
            self.assertEqual(kwargs["string_empty"], None)
            self.assertEqual(kwargs["multi_string"], ("one", "two", "thr ee"))
            self.assertEqual(kwargs["multi_string_empty"], ())
            self.assertEqual(kwargs["boolean"], True)
            self.assertEqual(kwargs["boolean_empty"], False)
            self.assertEqual(kwargs["integer"], 123)
            self.assertEqual(kwargs["integer_empty"], None)
            self.assertEqual(kwargs["multi_integer"], (11, 22, 33))
            self.assertEqual(kwargs["multi_integer_empty"], ())
            self.assertEqual(kwargs["f"].read(), "a")
            self.assertEqual(kwargs["multi_f"][0].read(), "b")
            self.assertEqual(kwargs["multi_f"][1].read(), "c")

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("x.ini", "w") as f:
                f.write(
                    """
                    [{}]
                    string =    xyz
                    string-env-override = from-config
                    multi-string = one,      two

                        thr ee
                    boolean = true
                    integer = 123
                    multi-integer = 11,   22,    33
                    f = a
                    multi-f = b, c
                    """.format(__project__)
                )
            for name in ["a", "b", "c"]:
                with open(name, "w") as f:
                    f.write(name)

            result = runner.invoke(fun, ["--config", "x.ini"])
            self.assertEqual(result.exit_code, 0)

    def test_with_config_other_name(self) -> None:
        @click.command()
        @option.add_config("--xyz")
        @option.add("--asdf")
        def fun(**kwargs: Any) -> None:
            self.assertEqual(kwargs["asdf"], "abcd")

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("x.ini", "w") as f:
                f.write(
                    """
                    [{}]
                    asdf = abcd
                    """.format(__project__)
                )
            result = runner.invoke(fun, ["--xyz", "x.ini"])
            self.assertEqual(result.exit_code, 0)

    def test_with_config_and_overrides(self) -> None:
        @click.command()
        @option.add_config("--config")
        @option.add("--from-cfg")
        @option.add("--from-cfg-and-cli")
        @option.add("--from-cfg-and-env")
        @option.add("--from-cfg-and-env-and-cli")
        def fun(**kwargs: Any) -> None:
            self.assertEqual(kwargs["from_cfg"], "xyz")
            self.assertEqual(kwargs["from_cfg_and_cli"], "cli")
            self.assertEqual(kwargs["from_cfg_and_env"], "env")
            self.assertEqual(kwargs["from_cfg_and_env_and_cli"], "cli")

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("x.ini", "w") as f:
                f.write(
                    """
                    [{}]
                    from-cfg = xyz
                    from-cfg-and-cli = xyz
                    from-cfg-and-env = xyz
                    from-cfg-and-env-and-cli = xyz
                    """.format(__project__)
                )

            args = [
                "--from-cfg-and-cli",
                "cli",
                "--from-cfg-and-env-and-cli",
                "cli",
            ]
            env = {
                "FUN_CONFIG": "x.ini",
                "FUN_FROM_CFG_AND_ENV": "env",
                "FUN_FROM_CFG_AND_ENV_AND_CLI": "env",
            }

            result = runner.invoke(
                fun,
                args=args,
                env=env,
                auto_envvar_prefix="FUN",
            )
            self.assertEqual(result.exit_code, 0)


class TestAdd(TestCase):
    def test_add(self) -> None:
        @click.command()
        @option.add("-a", type=int)
        @option.add("-b", is_flag=True)
        @option.add("-c", multiple=True)
        def fun(a: int, b: bool, c: Tuple[str]) -> None:
            self.assertEqual(a, 5)
            self.assertEqual(b, True)
            self.assertEqual(c, ("x", "y"))

        runner = CliRunner()
        result = runner.invoke(fun, ["-a", "5", "-b", "-c", "x", "-c", "y"])
        self.assertEqual(result.exit_code, 0)
