# -*- coding: utf-8 -*-
import subprocess
import sys
import time
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from fart.config import DATA_DIR
from fart.utils import error, warn, info

MODULES_DIR: Path = DATA_DIR / "modules"
__modules: list[Path] = []


def load_modules():
    print("Loading modules...")
    for file in MODULES_DIR.iterdir():
        if file.is_dir():
            print(f"Trying to load {file.name}...")
            try:
                spec = spec_from_file_location("fart.module." + file.name, file / "__init__.py")
                module = module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                __modules.append(file)
            except Exception as e:
                if "No such file" in str(e) and "__init__.py" in str(e):
                    warn(f"Module {file.name} does not have an __init__.py file, skipping...")
                else:
                    error(f"Failed to load {file.name}")
                    print(e)


def add_module(target: str) -> bool:
    print("Checking if `git` is installed...")
    process = subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        print("`git --version` returned non-zero exit code")
        error("`git` is not installed on your machine.")
        return False

    if target.count("/") == 1 and "http" not in target:
        warn("Assuming that the target is a GitHub repository ID, fixing...")
        target = f"https://github.com/{target}"
    elif "git@" in target:
        warn("Assuming that the target is an SSH URI, fixing...")
        target = target.replace("git@", "https://").replace(":", "/")

    repo_name: str = target.split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    modules_dir = DATA_DIR / "modules"
    repo_dir = modules_dir / repo_name
    if repo_dir.exists():
        error(f"Module {repo_name} already exists.")
        return False
    modules_dir.mkdir(parents=True, exist_ok=True)

    info(f"Fetching from {target}...")
    start_time: float = time.time()
    process = subprocess.run(["git", "clone", target, str(repo_dir)])
    if process.returncode != 0:
        error(f"Failed to fetch from {target}")
        repo_dir.rmdir()
        return False
    info(f"Successfully fetched from {target} (took {time.time() - start_time:.2f}s)")
    return True
