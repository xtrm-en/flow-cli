# -*- coding: utf-8 -*-
import os
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from flow.utils import info, error, success, warn

from flow.config import get_config
from flow.commands import create


def __parser(parser: ArgumentParser):
    parser.add_argument("target_name", help="the name the output binary should have", nargs="?")


def __exec(_: ArgumentParser, args: Namespace) -> int:
    current_working_dir = Path(os.getcwd())
    target_name: Optional[str] = args.target_name

    print(f"Trying to compile {current_working_dir.name}...")
    # Check if makefile
    makefile_path = current_working_dir / "Makefile"
    if makefile_path.exists():
        info("Found Makefile, checking for build target...")
        if target_name is not None:
            warn("A target name was specified, but is not supported for Makefile compilation.")

        # check if build exists
        process = subprocess.run(["make", "build", "-n"], capture_output=True)
        if process.returncode == 0:
            print("Makefile has a build target, running it...")
            info("Found Makefile, running `make build`...")
            code: int = os.system("make build")
            if code != 0:
                error("Failed to compile.")
                return code
        else:
            print("Makefile has no build target, trying to run `make`...")
            info("Found Makefile, running `make`...")
            code: int = os.system("make")
            if code != 0:
                error("Failed to compile.")
                return code
        success("Successfully compiled (via Makefile).")
        return 0

    # Check if CMake
    cmake_path = current_working_dir / "CMakeLists.txt"
    if cmake_path.exists():
        error("CMake is not supported yet.")
        return 1

    # Check if xmake
    xmake_path = current_working_dir / "xmake.lua"
    if xmake_path.exists():
        error("xmake is not supported yet.")
        return 1

    # Check if C files are found
    c_files = list(current_working_dir.glob("*.{c,cpp,cc}"))
    c_files.extend(list(current_working_dir.glob("src/*.{c,cpp,cc}")))
    if len(c_files) == 0:
        error("No C files found in the current directory, aborting.")
        return 1

    config = get_config()
    compiler_cmd = config["commands"]["compiler_command"]
    compiler_args = config["commands"]["compiler_flags"]
    if target_name is not None:
        compiler_args.append(f"-o {target_name}")

    c_files_str = " ".join([str(it) for it in c_files])
    compiler_args.append(c_files_str)

    # Check for header file directories
    possible_header_dirs = [
        "includes", "include", "inc", "headers", "header",
        "libft", "libft/includes", "libft/include", "libft/inc", "libft/headers", "libft/header",
    ]
    for it in possible_header_dirs:
        if (current_working_dir / it).exists():
            compiler_args.append(f"-I./{it}")

    info(f"Running '{compiler_cmd} {' '.join(compiler_args)}'")
    process = subprocess.run([compiler_cmd, *compiler_args])
    if process.returncode != 0:
        error("Failed to compile.")
        return process.returncode
    success("Successfully compiled.")
    return 0


create("compile", "compiles your code to a binary file", __parser, __exec, aliases=["make", "build"])
