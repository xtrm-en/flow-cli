# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

from os import listdir
from os.path import dirname, realpath
from typing import Callable, Optional


@dataclass
class CommandData:
    name: str
    description: str
    creation_callback: Optional[Callable[[ArgumentParser], None]]
    run_callback: Callable[[ArgumentParser, Namespace], None]


__cmd_data: list[CommandData] = []


def get_command_data() -> list[CommandData]:
    """Returns a list of all command data objects."""
    return __cmd_data


def load_commands() -> None:
    """Loads all commands from the commands directory."""

    # Get the path to the commands directory
    commands_dir = dirname(realpath(__file__)) + "/subcommands"

    # Find all commands
    commands = []
    for command in listdir(commands_dir):
        if command.endswith(".py") and not command.startswith("__"):
            commands.append(command[:-3])
    print(f"Fetched {len(commands)} command" + ("s" if len(commands) != 1 else "") + ".")

    # Import everything
    for command in commands:
        print(f"Importing '{command}'")
        __import__(f"fart.subcommands.{command}")


def create(name: str, description: str, creation_callback: Callable[[ArgumentParser], None],
           run_callback: Callable[[ArgumentParser, Namespace], None]) -> None:
    __cmd_data.append(CommandData(name, description, creation_callback, run_callback))
