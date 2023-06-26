# -*- coding: utf-8 -*-

import os
from os.path import dirname, realpath
import signal
import sys
import time
from types import FrameType, ModuleType
from typing import Optional


def hijack_python_path() -> None:
    """Allows importing the project as a global module by
    adding the project root to the Python path."""
    root: str

    # Get the path to the project root
    root = dirname(dirname(realpath(__file__)))

    # Add the project root to the Python path
    sys.path.insert(0, root)


def hijack_streams(logging: bool = False) -> None:
    """Allows modified printing by replacing the
    standard output streams with custom ones."""
    if logging:
        os.environ["FART_DEBUG_LOG"] = "1"

    # Debug log output
    writeback: bool = False
    write_logs: bool = os.environ.get("FART_DEBUG_LOG", "0") == "1"

    from fart.output import OutputStreamHook

    OutputStreamHook.apply(sys, "stdout", False, writeback, write_logs)
    OutputStreamHook.apply(sys, "stderr", True, writeback, write_logs)


def restore_streams() -> None:
    """Restores the standard output stream."""
    sys.stdout.flush()
    sys.stderr.flush()

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def main() -> None:
    # Hijack the Python syspath
    hijack_python_path()

    # Hijack the output streams
    hijack_streams()
    print("Initialized output stream hooks")

    # Get the startup time
    startup_time: float = time.time()

    exit_code: int

    # Load the main module and call the main function
    print("Fetching main target...", end=" ")
    try:
        main_module: ModuleType = __import__("fart.main")
        print("got:", main_module)

        print("Calling main function...")
        # noinspection PyBroadException
        try:
            exit_code = main_module.__dict__["main"].__dict__["main"]()
        except Exception:
            import traceback

            print("An unhandled exception occurred in the main function:\n" + traceback.format_exc())
            sys.__stderr__.write(
                "Unhandled exception traceback:\n" + traceback.format_exc()
            )
            exit_code = -1

        # ensure hijacked
        restore_streams()
        hijack_streams()

        print(f"Execution took {time.time() - startup_time:.2f} s")
    except ModuleNotFoundError as e:
        exit_code = -2
        print("failed")
        print("Could not find main module, aborting execution!")
        print(e)

    # Unhook the output streams
    restore_streams()

    # Exit the program
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
