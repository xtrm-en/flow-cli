# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace
from typing import Callable

from fart.commands import create
from fart.config import get_config


def aliases(_: Namespace) -> bool:

    return True


def __parser(parser: ArgumentParser):
    parser.add_argument("target", help="the action to execute setup for", nargs="?")


actions: list[Callable[[Namespace], bool]] = [
    aliases
]


def __exec(_: ArgumentParser, args: Namespace) -> int:
    config = get_config()

    target: str = args.target
    if target is None or target not in [it.__name__ for it in actions]:
        pass

    return 0


create("setup", "show the setup screen", __parser, __exec)
