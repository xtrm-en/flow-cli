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


def hijack_streams() -> None:
    """Allows modified printing by replacing the
    standard output streams with custom ones."""

    # Debug log output
    writeback: bool = False
    write_logs: bool = os.environ.get("FART_DEBUG_LOG", "0") == "1"

    from fart.output import OutputStreamHook

    OutputStreamHook.apply(sys, "stdout", False, writeback, write_logs)
    OutputStreamHook.apply(sys, "stderr", True, writeback, write_logs)

    print("Initialized output stream hooks")


def restore_streams() -> None:
    """Restores the standard output stream."""
    sys.stdout.flush()
    sys.stderr.flush()

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def main() -> None:
    startup_time: float
    delta: float

    # Hijack the Python syspath
    hijack_python_path()

    # Hijack the output streams
    hijack_streams()

    # Get the startup time
    startup_time = time.time()

    # Load the main module and call the main function
    print("Fetching main target...", end=" ")
    try:
        main_module: ModuleType = __import__("fart.main")
        print("got:", main_module)

        print("Calling main function...")
        try:
            main_module.__dict__["main"].__dict__["main"]()
        except Exception:
            import traceback

            print("An unhandled exception occurred in the main function")
            sys.stderr.write(
                "Unhandled exception traceback:\n" + traceback.format_exc()
            )
        print(f"Execution took {time.time() - startup_time:.2f} s")
    except ModuleNotFoundError:
        print("failed")
        print("Could not find main module, aborting execution!")

    # Unhook the output streams
    restore_streams()

    # Prevents creating another logfile with the same name
    delta = time.time() - startup_time
    if delta < 1:

        def signal_handler(sig: int, frame: Optional[FrameType]) -> None:
            cols: int
            cols = os.get_terminal_size().columns

            # Don't print weird control characters in the terminal
            sys.__stdout__.write("\r" + " " * cols + "\r")
            sys.__stdout__.flush()

        signal.signal(signal.SIGINT, signal_handler)
        time.sleep(1.01 - delta)

    # Exit the program
    sys.exit(0)


if __name__ == "__main__":
    main()
