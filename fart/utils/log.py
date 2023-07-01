# -*- coding: utf-8 -*-
import sys

from . import Colors
from fart.config import get_config

SYMBOL_TABLE = {
    "emoji": {
        "info": "ℹ️",
        "warn": "⚠️",
        "error": "❌",
        "success": "✅",
    },
    "unicode": {
        "info": "ℹ",
        "warn": "⚠",
        "error": "𐄂",
        "success": "✓",
    },
    "ascii": {
        "info": "i",
        "warn": "!",
        "error": "x",
        "success": "v",
    },
}


def log(message: object, end: str = "\n") -> None:
    """Prints a message to the original standard output stream, as well as the hooked one."""
    print(message, end=end)
    sys.__stdout__.write(str(message) + end)


def fatal(message: object, end: str = "\n") -> None:
    """Prints a fatal error message to the original standard error stream, as well as the hooked one."""
    print(message, end=end, file=sys.stderr)
    sys.__stderr__.write(str(message) + end)


def __symbol(message: object, symbol: str, color: str, end: str = "\n") -> None:
    config = get_config()
    brackets: bool = config["logging"]["log_brackets"]
    symbol_type: str = config["logging"]["log_symbols"]
    log(f"{Colors.DARK_GRAY}{'[' if brackets else ''}{color}{SYMBOL_TABLE[symbol_type][symbol]}{Colors.DARK_GRAY}{']' if brackets else ''}{Colors.WHITE} {message}{Colors.RESET}",
        end=end)


def info(message: object, end: str = "\n") -> None:
    __symbol(message, "info", Colors.CYAN, end=end)


def warn(message: object, end: str = "\n") -> None:
    __symbol(message, "warn", Colors.YELLOW, end=end)


def error(message: object, end: str = "\n") -> None:
    __symbol(message, "error", Colors.RED, end=end)


def success(message: object, end: str = "\n") -> None:
    __symbol(message, "success", Colors.GREEN, end=end)
