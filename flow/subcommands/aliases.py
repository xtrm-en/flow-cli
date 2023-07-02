# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace

from flow.commands import create_alias
from flow.config import get_config
import subprocess


def __parser(parser: ArgumentParser) -> None:
    parser.add_argument("extra", help="extra arguments to pass to the command", nargs="*")


def __wrap(command: str, extra: list[str]) -> int:
    command = [command, *extra]
    print(f"Running {command}")
    process = subprocess.run(command, shell=True, capture_output=False)
    print(f"Process {command} exited with code {process.returncode}")
    return process.returncode


def __gcc(_: ArgumentParser, namespace: Namespace) -> int:
    return __wrap("gcc", [*get_config()["commands"]["compiler_flags"], *namespace.extra])


def __clang(_: ArgumentParser, namespace: Namespace) -> int:
    return __wrap("clang", [*get_config()["commands"]["compiler_flags"], *namespace.extra])


def __valgrind(_: ArgumentParser, namespace: Namespace) -> int:
    return __wrap(get_config()["commands"]["valgrind_command"], [*get_config()["commands"]["valgrind_flags"], *namespace.extra])


create_alias("gcc", "compile with gcc using configured compiler flags", __parser, __gcc)
create_alias("clang", "compile with clang using configured compiler flags", __parser, __clang)
create_alias("valgrind", "debug and check for memory leaks", __parser, __valgrind)
