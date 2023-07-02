# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace
from fart.config import get_config
from fart.commands import create


def __parser(parser: ArgumentParser):
    parser.add_argument("target_name", help="the name of the output binary", nargs="?")


def __exec(_: ArgumentParser, args: Namespace) -> int:
    config = get_config()

    return 0


create("compile", "compiles your code to a binary file", __parser, __exec, aliases=["make", "build"])
