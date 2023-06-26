from argparse import Namespace, ArgumentParser
from typing import Callable, Optional

from fart.commands import create
from fart.config import get_config
from fart.utils import info, warn, success, error, log
import subprocess


def gcc(_: Optional[Namespace] = None) -> bool:
    config = get_config()

    process = subprocess.run([config["commands"]["compiler_command"], *config["commands"]["compiler_flags"]], capture_output=True)
    if process.returncode != 0:
        output = process.stderr.decode("utf-8")
        log(output)
        return False
    return True


def norminette(_: Namespace) -> bool:
    process = subprocess.run(["norminette"], capture_output=True)
    if process.returncode != 0:
        output = process.stdout.decode("utf-8")
        for line in output.split("\n"):
            if line.endswith("OK!"):
                # success(line[:-5])
                pass
            elif line.endswith("Error!"):
                error(line[:-8])
            elif line.startswith("Error: "):
                log("\t" + line[7:], end="\n")
        return False
    return True


checks: list[Callable[[Namespace], bool]] = [
    norminette, gcc
]


def __exec(_: ArgumentParser, namespace: Namespace) -> None:
    config = get_config()
    disabled_checks = config["check"]["checks"]

    if len(disabled_checks) > 0:
        warn(f"Skipping {len(disabled_checks)} disabled check" + ("s" if len(disabled_checks) != 1 else "") + ".")

    result = True
    for check_func in checks:
        check_name = check_func.__name__
        if check_name in disabled_checks:
            print(f"Skipping check '{check_name}' since it's disabled.")
            continue
        info(f"Running check '{check_name}'")
        check_res: bool = check_func(namespace)
        if not check_res:
            warn(f"Check '{check_name}' failed.")
            result = False
        else:
            # success(f"Check '{check_name}' passed.")
            pass

    if not result:
        error("Some checks failed. Please fix them before continuing.")
    else:
        success("All checks passed.")


create("check", "checks your code for formatting or compilation errors", lambda parser: None, __exec)
