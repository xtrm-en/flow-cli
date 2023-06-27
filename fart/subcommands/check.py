# -*- coding: utf-8 -*-
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


@dataclass
class NormErrorData:
    type: str
    line: int
    column: int
    message: str


def norminette(_: Namespace) -> bool:
    # TODO: change to Popen and buffer the output in real time
    process = subprocess.run(["norminette"], capture_output=True)
    if process.returncode != 0:
        errors: dict[str, list[NormErrorData]] = {}
        output = process.stdout.decode("utf-8")
        last_data = None
        for line in output.split("\n"):
            if line.endswith("OK!"):
                # success(line[:-5])
                pass
            elif line.endswith("Error!"):
                # error(line[:-8])
                last_data = line.split(":")[0]
                errors[last_data] = []
            elif line.startswith("Error: "):
                # log("\t" + line[7:], end="\n")
                if last_data is None:
                    warn("Found error without file name.")
                    continue
                if last_data not in errors:
                    errors[last_data] = []

                tokens = [token.strip() for token in line[7:].replace("\t", " ").split(" ") if len(token.strip()) > 0]
                message: str = " ".join(tokens[5:])
                errors[last_data].append(
                    NormErrorData(
                        tokens[0],
                        int(tokens[2].split(",")[0]),
                        int(tokens[4].split(")")[0]),
                        message,
                    )
                )

        for file, file_errors in errors.items():
            error(f"File {file} has {len(file_errors)} errors:")
            for file_error in file_errors:
                log(f"\t{file_error.type} on line {file_error.line}, column {file_error.column}: {file_error.message}")
        return False
    return True


checks: list[Callable[[Namespace], bool]] = [
    norminette, compiler
]
POSSIBLE_VALUES["check.disabled_checks"] = [c.__name__ for c in checks]


def __praser(parser: ArgumentParser) -> None:
    parser.add_argument("checks", help="checks to run", nargs="*")


def __exec(_: ArgumentParser, namespace: Namespace) -> int:
    config = get_config()
    disabled_checks = config["check"]["disabled_checks"]
    force_checks = namespace.checks

    if len(force_checks) > 0:
        disabled_checks = [check.__name__ for check in checks if check.__name__ not in force_checks]

    result = True
    for check_func in checks:
        check_name = check_func.__name__
        if check_name in disabled_checks:
            info(f"Skipping check '{check_name}' since it's disabled.")
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
