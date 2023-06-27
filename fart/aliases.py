# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace
from typing import Callable

from fart.config import get_config
import subprocess

from fart.utils import log


def __parser(parser: ArgumentParser) -> None:
    parser.add_argument("extra", help="extra arguments to pass to the command", nargs="*")


def __wrap(command: str, extra: list[str]) -> int:
    command = " ".join([command, *extra])
    print(f"Running {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            log(output.decode("utf-8").strip())
    rc = process.poll()
    print(f"Process {command} exited with code {rc}")
    return rc


def __gcc(_: ArgumentParser, namespace: Namespace) -> int:
    return __wrap("gcc", [*get_config()["commands"]["compiler_flags"], *namespace.extra])


def __clang(_: ArgumentParser, namespace: Namespace) -> int:
    pass


def create_alias(name: str, description: str, parser: Callable[[ArgumentParser], None], function: Callable[[ArgumentParser, Namespace], int]) -> None:
    pass


create_alias("gcc", "compile with gcc", __parser, __gcc)
create_alias("clang", "compile with clang", __parser, __clang)
