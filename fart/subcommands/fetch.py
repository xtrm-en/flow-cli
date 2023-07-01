# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace

from fart.commands import create
from fart.config import DATA_DIR
from fart.utils import error, info

import subprocess
import time


def __parser(parser: ArgumentParser):
    parser.add_argument("target", help="the url/repository id to fetch from")


def __exec(_: ArgumentParser, args: Namespace) -> int:
    target: str = args.target

    print("Checking if `git` is installed...")
    process = subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        print("`git --version` returned non-zero exit code")
        error("`git` is not installed on your machine.")
        return 1

    if target.count("/") == 1 and "http" not in target:
        info("Assuming that the target is a GitHub repository ID")
        target = f"https://github.com/{target}"

    info(f"Fetching from {target}...")

    repo_name: str = target.split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    modules_dir = DATA_DIR / "modules"
    repo_dir = modules_dir / repo_name
    if repo_dir.exists():
        error(f"Module {repo_name} was already fetched.")
        return 1
    modules_dir.mkdir(parents=True, exist_ok=True)

    start_time: float = time.time()
    process = subprocess.run(["git", "clone", target, str(repo_dir)], stdout=subprocess.STDOUT, stderr=subprocess.STDOUT)
    if process.returncode != 0:
        error(f"Failed to fetch from {target}")
        repo_dir.rmdir()
        return 1
    info(f"Successfully fetched from {target} (took {time.time() - start_time:.2f}s)")

    return 0


create("fetch", "fetches a remote module from a git url", __parser, __exec)
