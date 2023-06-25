from argparse import Namespace

from fart.commands import create
from fart.config import get_config
from fart.utils import info, warn, success, error, log


def test(_: Namespace) -> None:
    config = get_config()
    info("Information log uwu nya")
    warn("Warning log uwu nya")
    success("Success log uwu nya")
    error("Error log uwu nya")
    log("Normal log uwu nya")


create("debugtest", "random tests uwu", lambda parser: None, test)