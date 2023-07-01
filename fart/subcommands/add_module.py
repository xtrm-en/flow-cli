# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace
import subprocess
import time

from fart.commands import create
from fart.modules import add_module
from fart.config import DATA_DIR
from fart.utils import error, info, warn


def __parser(parser: ArgumentParser):
    parser.add_argument("target", help="the url/repository id to fetch from")


def __exec(_: ArgumentParser, args: Namespace) -> int:
    target: str = args.target
    return 0 if add_module(target) else 1


create("add-module", "fetches a remote module from a git url", __parser, __exec)
