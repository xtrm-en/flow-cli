# -*- coding: utf-8 -*-
import traceback
from argparse import Namespace, ArgumentParser
from pathlib import Path

from norminette.exceptions import CParsingError
from norminette.lexer import TokenError

from flow.commands import create
from flow.config import get_config, POSSIBLE_VALUES
from flow.utils import info, warn, success, error, log, run_norminette

import subprocess
from typing import Callable, Optional


def compiler(_: Optional[Namespace] = None) -> bool:
    config = get_config()

    # TODO: compilation process

    # process = subprocess.run([config["commands"]["compiler_command"], *config["commands"]["compiler_flags"]],
    #                          capture_output=True)
    # if process.returncode != 0:
    #     output = process.stderr.decode("utf-8")
    #     log(output)
    #     return False
    return True


def norminette(_: Namespace) -> bool:
    show_success: bool = get_config()["check"]["show_success"]
    check_result = True
    for target in __find_target_files(Path(".")):
        try:
            output = run_norminette(target)
            if len(output) == 0:
                if show_success:
                    success(f"{target}")
                continue

            is_error: bool = any([it.is_error for it in output])
            if is_error:
                check_result = False
                error(f"{target}:")
            else:
                info(f"{target}:")
            for it in output:
                if it.is_error:
                    error(f"\t{it.format()}")
                else:
                    warn(f"\t{it.format()}")
        except (CParsingError, TokenError) as e:
            error(f"Failed to parse '{target}': {e}")
            check_result = False
        except Exception as e:
            error(f"Error while checking '{target}': {e}")
            traceback.print_exc()
            return False
    return check_result


def __is_c_file(path: Path) -> bool:
    return path.name.endswith(".c") or path.name.endswith(".h")


def __find_target_files(root: Path, predicate: Callable[[Path], bool] = __is_c_file) -> list[Path]:
    targets: list[Path] = []
    for path in root.iterdir():
        if path.is_dir():
            targets.extend(__find_target_files(path, predicate))
        elif predicate(path):
            targets.append(path)
    return sorted(targets, key=lambda p: str(p))


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
            [c for c in checks if c.__name__ == check_name][0] if check_name in [c.__name__ for c in checks] else None
        if check_func is None:
            error(f"Check '{check_name}' does not exist. Existing checks are: {', '.join([c.__name__ for c in checks])}")
            return 1
        check_res: bool = check_func(namespace)
        if not check_res:
            warn(f"Check '{check_name}' failed.")
            result = False
        else:
            if len(checks_to_run) > 1:
                success(f"Check '{check_name}' passed.")

    if not result:
        error("Some checks failed. Please fix them before continuing.")
        return 1

    success("All checks passed.")
    return 0


create("check", "checks your code for formatting or compilation errors", __praser, __exec)
