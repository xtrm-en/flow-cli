# -*- coding: utf-8 -*-
from argparse import Namespace, ArgumentParser

from fart.commands import create
from fart.config import get_config
from fart.utils import info, warn, success, error, log, fatal


def __run(_: ArgumentParser, __: Namespace) -> int:
    config = get_config()
    info("Information log uwu nya")
    warn("Warning log uwu nya")
    success("Success log uwu nya")
    error("Error log uwu nya")
    fatal("Fatal log!!!!! uwu nya")
    log("Normal log uwu nya")
    return 0


create("meow", "random tests uwu", lambda parser: None, __run, visible=False, aliases=["nya"])
