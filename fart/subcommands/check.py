# -*- coding: utf-8 -*-
import os
import sys
import traceback
from argparse import Namespace, ArgumentParser
from pathlib import Path

from norminette.context import Context
from norminette.exceptions import CParsingError
from norminette.lexer import TokenError, Lexer

from fart.commands import create
from fart.config import get_config, POSSIBLE_VALUES
from fart.utils import info, warn, success, error, log

from norminette.registry import Registry

import subprocess
from typing import Callable, Optional


def compiler(_: Optional[Namespace] = None) -> bool:
    config = get_config()

    process = subprocess.run([config["commands"]["compiler_command"], *config["commands"]["compiler_flags"]],
                             capture_output=True)
    if process.returncode != 0:
        output = process.stderr.decode("utf-8")
        log(output)
        return False
    return True


def norminette(_: Namespace) -> bool:
    targets: list[Path] = __find_target_files(Path("."))

    registry = Registry()
    has_err: bool = False
    content = None
    for path in targets:
        target = str(path)
        if target[-2:] not in [".c", ".h"]:
            error(f"{target} is not valid C or C header file")
        else:
            try:
                if content is None:
                    with open(target) as f:
                        try:
                            source = f.read()
                        except Exception as e:
                            error("File could not be read: " + str(e))
                            print(traceback.format_exc())
                            sys.exit(0)
                else:
                    source = content
                try:
                    lexer = Lexer(source)
                    tokens = lexer.get_tokens()
                except KeyError as e:
                    error("Error while parsing file: " + str(e))
                    print(traceback.format_exc())
                    sys.exit(0)
                context = Context(target, tokens, False, [])  # TODO: -R
                registry.run(context, source)
                if context.errors:
                    has_err = True
            except TokenError as e:
                has_err = True
                error(target + ": " + e.msg[7:])
            except CParsingError as e:
                has_err = True
                # print(target + f": Error!\n\t{colors(e.msg, 'red')}")
            except KeyboardInterrupt:
                sys.exit(1)

    return has_err


def __is_c_file(path: Path) -> bool:
    return path.name.endswith(".c") or path.name.endswith(".h")


def __find_target_files(root: Path, predicate: Callable[[Path], bool] = __is_c_file) -> list[Path]:
    targets: list[Path] = []
    for path in root.iterdir():
        if path.is_dir():
            targets.extend(__find_target_files(path, predicate))
        elif predicate(path):
            targets.append(path)
    return targets


checks: list[Callable[[Namespace], bool]] = [
    norminette, compiler
]
POSSIBLE_VALUES["check.disabled_checks"] = [c.__name__ for c in checks]


def __praser(parser: ArgumentParser) -> None:
    parser.add_argument("checks", help="checks to run", nargs="*")


def __exec(_: ArgumentParser, namespace: Namespace) -> int:
    checks_to_run: list[str]
    if namespace.checks is not None and len(namespace.checks) > 0:
        checks_to_run = namespace.checks
    else:
        config = get_config()
        disabled_checks: list[str] = config["check"]["disabled_checks"]
        checks_to_run = [c.__name__ for c in checks if c.__name__ not in disabled_checks]

    result = True
    for check_name in checks_to_run:
        info(f"Running check '{check_name}'")
        check_func: Optional[Callable[[Namespace], bool]] = \
            next((c for c in checks if c.__name__ == check_name), __default=None)
        if check_func is None:
            error(f"Check '{check_name}' does not exist. Existing checks are: {', '.join([c.__name__ for c in checks])}")
            return 1
        check_res: bool = check_func(namespace)
        if not check_res:
            warn(f"Check '{check_name}' failed.")
            result = False
        else:
            success(f"Check '{check_name}' passed.")
            pass

    if not result:
        error("Some checks failed. Please fix them before continuing.")
        return 1

    success("All checks passed.")
    return 0


create("check", "checks your code for formatting or compilation errors", __praser, __exec)
