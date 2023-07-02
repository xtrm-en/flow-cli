import os
import signal
import sys
import subprocess
from argparse import Namespace, ArgumentParser

from flow.commands import create


# noinspection PyShadowingBuiltins
def print(o: object, flush: bool = False, end: str = "\n") -> None:
    sys.__stdout__.write(str(o) + end)
    if flush:
        sys.__stdout__.flush()


def __sig_handler(signal_number, frame):
    cols = os.get_terminal_size().columns
    sys.__stdout__.write("\r" + " " * cols + "\r" + "\033[2J" + "\033[0;0H" + "\033[?25h")
    sys.__stdout__.flush()
    exit(0)


def __watch(_: ArgumentParser, __: Namespace) -> int:
    signal.signal(signal.SIGINT, __sig_handler)

    # TODO: replace to info
    print("\n" * 4, flush=False)
    print("\033[2J\033[0;0Hrunning")
    print("\033[?25l")

    running: bool = True
    while running:
        process = subprocess.run(["flow", "check"], capture_output=True)
        sys.__stdout__.write("\033[0;0H")
        print("\n" * 4, flush=False)
        print(process.stdout.decode(), flush=False)
        print("\033[0J")
        sys.__stdout__.flush()
    return 0


create("watch", "watches the check results", lambda _: None, __watch)
