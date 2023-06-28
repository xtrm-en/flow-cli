# -*- coding: utf-8 -*-
import sys
from argparse import Namespace, ArgumentParser
from dataclasses import dataclass
from typing import Callable, Optional

from fart.commands import create
from fart.config import get_config, POSSIBLE_VALUES
from fart.utils import info, warn, success, error, log
import subprocess


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
    @dataclass
    class NormErrorData:
        type: str
        line: int
        column: int
        message: str

    last_file_errors: Optional[tuple[str, list[NormErrorData]]] = None
    has_errors: bool = False
    show_success: bool = get_config()["check"]["show_success"]

    process = subprocess.Popen(["norminette"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        sys.__stdout__.flush()
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            line = output.decode("utf-8").strip()
            # TODO: Notice!
            # Notice: GLOBAL_VAR_DETECTED  (line:   6, col:   1):     Global variable present in file. Make sure it is a reasonable choice.
            if line.startswith("Error: "):
                if last_file_errors is None:
                    warn("Found error without file name.")
                    continue

                tokens = [token.strip() for token in line[7:].replace("\t", " ").split(" ") if len(token.strip()) > 0]
                message: str = " ".join(tokens[5:])
                last_file_errors[1].append(
                    NormErrorData(
                        tokens[0],
                        int(tokens[2].split(",")[0]),
                        int(tokens[4].split(")")[0]),
                        message,
                    )
                )
            else:
                if last_file_errors is not None:
                    error(last_file_errors[0])
                    for error_data in last_file_errors[1]:
                        log(f"\t{error_data.type} at ({error_data.line}:{error_data.column}) -> {error_data.message}")
                if line.endswith("OK!"):
                    last_file_errors = None
                    if show_success:
                        success(line[:-5])
                elif line.endswith("Error!"):
                    has_errors = True
                    last_file_errors = (line[:-6], [])
    return not has_errors


checks: list[Callable[[Namespace], bool]] = [
    norminette, compiler
]
POSSIBLE_VALUES["check.disabled_checks"] = [c.__name__ for c in checks]


def __praser(parser: ArgumentParser) -> None:
    parser.add_argument("checks", help="checks to run", nargs="*")


def __exec(_: ArgumentParser, namespace: Namespace) -> int:
    config = get_config()

    # checks_to_run

    # disabled_checks = config["check"]["disabled_checks"]
    # force_checks = namespace.checks
    #
    # if len(force_checks) > 0:
    #     disabled_checks = [check.__name__ for check in checks if check.__name__ not in force_checks]
    #
    # enabled_checks = dict([(check.__name__, check) for check in checks if check.__name__ not in disabled_checks])
    #
    # info(f"Running checks ")
    result = True
    for check_func in checks:
        check_name = check_func.__name__
        if check_name in disabled_checks:
            continue
        info(f"Running check '{check_name}'")
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
