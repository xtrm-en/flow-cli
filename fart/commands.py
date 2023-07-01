# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

from os import listdir
from os.path import dirname, realpath
from typing import Callable, Optional


@dataclass
class CommandData:
    names: list[str]
    description: str
    creation_callback: Optional[Callable[[ArgumentParser], None]]
    run_callback: Callable[[ArgumentParser, Namespace], int]
    alias: bool
    visible: bool


__cmd_data: list[CommandData] = []


def get_command_data() -> list[CommandData]:
    """Returns a list of all command data objects."""
    return __cmd_data


def load_commands() -> None:
    """Loads all commands from the commands directory."""

    # Get the path to the commands directory
    commands_dir = dirname(realpath(__file__)) + "/subcommands"

    # Find all commands
    print(f"Searching for commands in '{commands_dir}'...")
    commands = []
    for command in listdir(commands_dir):
        if command.endswith(".py") and not command.startswith("__"):
            commands.append(command[:-3])
    print(f"Fetched {len(commands)} command" + ("s" if len(commands) != 1 else "") + ".")

    # Import everything
    for command in commands:
        print(f"Importing '{command}'")
        __import__(f"fart.subcommands.{command}")


def create_alias(name: str, description: str, creation_callback: Callable[[ArgumentParser], None],
                 run_callback: Callable[[ArgumentParser, Namespace], int], visible: bool = True) -> None:
    create(name, description, creation_callback, run_callback, is_alias=True, visible=visible)


def create(name: str, description: str, creation_callback: Callable[[ArgumentParser], None],
           run_callback: Callable[[ArgumentParser, Namespace], int], is_alias: bool = False, visible: bool = True, aliases: list[str] = None) -> None:
    if aliases is None:
        aliases = []
    print(f"Creating command '{name}'\n\tDescription: '{description}'\n\tAlias: {is_alias}\n\tVisible: {visible}\n\tAliases: {', '.join(aliases)}")
    __cmd_data.append(CommandData([name, *aliases], description, creation_callback, run_callback, is_alias, visible))
