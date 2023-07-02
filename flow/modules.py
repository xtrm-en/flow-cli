# -*- coding: utf-8 -*-
import subprocess
import sys
import time
from pathlib import Path

from flow.config import DATA_DIR
from flow.utils import error, warn, info

MODULES_DIR: Path = DATA_DIR / "modules"
__modules: list[Path] = []


def load_modules():
    if not MODULES_DIR.exists():
        MODULES_DIR.mkdir(parents=True, exist_ok=True)
    for file in MODULES_DIR.iterdir():
        if file.is_dir():
            sys.path.insert(1, str(file))
            __modules.append(file)
    print(f"Loaded {len(__modules)} modules.")


def get_modules() -> list[Path]:
    return __modules


def get_modules_data() -> list[tuple[str, str]]:
    data: list[tuple[str, str]] = []
    for module_dir in get_modules():
        module_name: str = module_dir.name
        module_version: str = "unknown"

        git_dir = module_dir / ".git"
        if git_dir.exists():
            with open(git_dir / "HEAD") as head_file:
                head = head_file.read().strip()
                if head.startswith("ref: "):
                    branch = head[5:]
                    with open(git_dir / branch) as branch_file:
                        module_version = branch_file.read().strip()[:9]
                else:
                    module_version = head[:9]
                module_version = "git-" + module_version
        data.append((module_name, module_version))
    return data


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


def remove_module(target: str) -> bool:
    if target.count("/") > 0:
        error("Target must be a module name, not a repository ID/URL.")
        return False
    target_dir = MODULES_DIR / target
    if not target_dir.exists():
        error(f"Module {target} does not exist.")
        return False
    info(f"Removing module {target}...")
    start_time: float = time.time()

    def delete_dir(directory: Path):
        for file in directory.iterdir():
            if file.is_dir():
                delete_dir(file)
            else:
                file.unlink(missing_ok=True)
        directory.rmdir()

    try:
        delete_dir(target_dir)
        info(f"Successfully removed module {target} (took {time.time() - start_time:.2f}s)")
    except IOError as e:
        error(f"Failed to remove module {target}: {e}")
        return False
    return True
