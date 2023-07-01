# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace

from fart.commands import create
from fart.config import get_config


def __exec(_: ArgumentParser, __: Namespace) -> int:

    return 0


create("setup", "show the setup screen", lambda _: None, __exec)
