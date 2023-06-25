# -*- coding: utf-8 -*-

from __future__ import annotations
import inquirer
import sys
from types import ModuleType


def prompt(questions):
    """Wraps the inquirer#prompt function to allow for custom output hooking."""
    from fart.launcher import hijack_streams, restore_streams
    restore_streams()
    answers = inquirer.prompt(questions)
    hijack_streams()
    return answers


def info(message: object, end: str = "\n") -> None:
    """Prints a message to the original standard output stream, as well as the hooked one."""
    print(message, end=end)
    sys.__stdout__.write(str(message) + end)


class Colors:
    """ANSI color codes"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"

    WHITE = RESET
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    YELLOW = "\033[1;33m"
    LIGHT_GRAY = "\033[0;37m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    DARK_GRAY = "\033[1;30m"

    VALUES = [
        BLACK,
        RED,
        GREEN,
        BROWN,
        BLUE,
        PURPLE,
        CYAN,
        LIGHT_GRAY,
        DARK_GRAY,
        LIGHT_RED,
        LIGHT_GREEN,
        YELLOW,
        LIGHT_BLUE,
        LIGHT_PURPLE,
        LIGHT_CYAN,
        LIGHT_WHITE,
        RESET,
        WHITE,
        BOLD,
        FAINT,
        ITALIC,
        UNDERLINE,
        BLINK,
        NEGATIVE,
        CROSSED,
    ]

    # cancel SGR codes if we don't write to a terminal
    if not __import__("sys").stdout.isatty():
        for _ in dir():
            if isinstance(_, str) and _[0] != "_":
                locals()[_] = ""
    else:
        # set Windows console in VT mode
        if __import__("platform").system() == "Windows":
            ctypes: ModuleType = __import__("ctypes")
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7
            )
            del ctypes
