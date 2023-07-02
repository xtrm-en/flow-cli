# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser, Namespace

from fart.commands import create
from fart.test.tester import run_test
from fart.utils import error, info, log


def __parser(parser: ArgumentParser) -> None:
    parser.add_argument("tests", help="the test(s) to run", nargs="*")


def __test_picker(test_path: str):
    pass


def __exec(_: ArgumentParser, namespace: Namespace) -> int:
    if len(namespace.tests) > 0:
        info(f"Running tests '{', '.join(namespace.tests)}'")
        for test in namespace.tests:
            run_test(test)
        return 0

    cwd = os.getcwd()
    info(f"Looking for testable files in '{cwd}'...")

    print("Looking for testable git repositories")
    testable_roots: list[str] = []
    for root, dirs, files in os.walk(cwd):
        if ".git" in dirs:
            print(f"Found git repository at '{root}'")
            git_dir = os.path.join(root, ".git")
            git_config = os.path.join(git_dir, "config")
            if not os.path.exists(git_config):
                error(f"Could not find git config at '{git_config}'")
                continue

            url: str
            with open(git_config, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip().startswith("url = "):
                        url = line.strip()[6:].strip()
                        print(f"Found git url '{url}'")
                        break
                else:
                    error("Could not find git url. (" + git_config + ")")
                    continue
            # 42 project URI
            if "vogsphere" in url.lower():
                testable_roots.append(root)

    if len(testable_roots) == 0:
        error("Could not find any testable git repository.")
        return 1

    if len(testable_roots) > 1:
        info("Found multiple testable git repositories.")
        for test_root in testable_roots:
            info(f"Found testable git repository at '{test_root}'")

    for test_root in testable_roots:
        info(f"Looking for tests in '{test_root}'")

    return 0


create("test", "tests your code", __parser, __exec)
