# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
import subprocess

from fart.commands import create
from fart.config import DATA_DIR
from fart.utils import error, info, success


def __parser(parser: ArgumentParser):
    parser.add_argument("--no-change-vol", help="don't change the volume", dest="no_change_vol", action="store_true")


def __exec(_: ArgumentParser, args: Namespace) -> int:
    change_volume: bool = not args.no_change_vol
    sound_path: Path = DATA_DIR / "fart.ogg"
    if not sound_path.exists():
        info("Farting in progress...")
        process = subprocess.run(["wget", "https://test.xtrm.me/lmao/fart.ogg", "-O", str(sound_path)], capture_output=True)
        if process.returncode != 0:
            error("Failed to download fart.ogg, no farting allowed...")
            return 1
    commands: list[str] = [
        "pactl set-sink-mute 0 1", "pactl set-sink-mute 0 0",
        *(["pactl set-sink-volume 0 125%", "pactl set-sink-volume 0 150%"] if change_volume else []),
        "paplay " + str(sound_path),
    ]
    for cmd in commands:
        info(f"Running '{cmd}'")
        os.system(cmd)
    success("Farted successfully")
    return 0


create("fart", "farts hehehehe", __parser, __exec, visible=False)
