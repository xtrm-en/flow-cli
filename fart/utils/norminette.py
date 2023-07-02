# -*- coding: utf-8 -*-
import traceback
from dataclasses import dataclass
from pathlib import Path

from norminette.context import Context
from norminette.exceptions import CParsingError
from norminette.lexer import Lexer, TokenError, Token

from norminette.registry import Registry

__shared_registry = Registry()


@dataclass
class NormOutput:
    file: Path
    position: tuple[int, int]
    error_type: str
    message: str
    is_error: bool

    def format(self):
        return f"{self.error_type} (at {self.position[0]}:{self.position[1]}): {self.message}"


def run_norminette(file: Path, extra: list[str] = None) -> list[NormOutput]:
    """Runs the norminette on a file and returns the output.

    Parameters
    ----------
    file : Path
        The file to run the norminette on.
    extra : list[str], optional
        Extra arguments to pass to the norminette, by default None

    Returns
    -------
    list[NormOutput]
        The norminette output.

    Raises
    ------
    TokenError
        If the file could not be parsed.
    CParsingError
        If the file could not be parsed.
    IOError
        If the file could not be read or is invalid.
    """

    output: list[NormOutput] = []
    target = str(file)
    tokens: list[Token] = []
    if target[-2:] not in [".c", ".h"]:
        raise IOError(f"{target} is not valid C or header file")
    with open(target) as f:
        source = f.read()
        try:
            lexer = Lexer(source)
            tokens = lexer.get_tokens()
        except KeyError as e:
            raise IOError("Error while parsing file", e)
    context = Context(target, tokens, added_value=extra)
    __shared_registry.run(context, source)
    for error in context.errors:
        output.append(
            NormOutput(
                file,
                (error.line if error.line is not None else -1, error.col if error.col is not None else -1),
                error.errno,
                # Capitalize for consistency
                error.error_msg[0].upper() + error.error_msg[1:],
                True
            )
        )
    for warning in context.warnings:
        output.append(
            NormOutput(
                file,
                (warning.line if warning.line is not None else -1, warning.col if warning.col is not None else -1),
                warning.errno,
                # Capitalize for consistency
                warning.error_msg[0].upper() + warning.error_msg[1:],
                False
            )
        )
    return output
