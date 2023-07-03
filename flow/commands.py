# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from os import listdir
from os.path import dirname, realpath
from pathlib import Path
from typing import Callable, Optional

from flow.utils import warn

from flow.modules import get_modules


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

    # Find all commands
    commands = []
    for commands_dir in [
        Path(dirname(realpath(__file__))) / "subcommands",
        *map(lambda p: Path(p / "subcommands"), get_modules())
    ]:
        if not commands_dir.exists():
            continue
        print(f"Searching for commands in '{commands_dir}'...")
        for command_file in commands_dir.iterdir():
            command = command_file.name
            if command.endswith(".py") and not command.startswith("__"):
                raw_cmd = command[:-3]
                if raw_cmd not in commands:
                    commands.append(raw_cmd)
                else:
                    warn(f"Command '{raw_cmd}' already exists, skipping...")
    print(f"Fetched {len(commands)} command" + ("s" if len(commands) != 1 else "") + ".")

    # Import everything
    for command in sorted(commands):
        print(f"Importing '{command}'")
        # noinspection PyBroadException
        try:
            __import__(f"flow.subcommands.{command}")
        except (ImportError, ModuleNotFoundError):
            imported: bool = False
            for module in get_modules():
                # noinspection PyBroadException
                try:
                    __import__(f"{module.name}.subcommands.{command}")
                    imported = True
                    break
                except (ImportError, ModuleNotFoundError):
                    pass
                except Exception:
                    warn(f"Failed to import command '{command}', check debug logs for errors.")
                    import traceback
                    print(traceback.format_exc())
            if not imported:
                warn(f"Failed to import command '{command}', not found.")
        except Exception:
            warn(f"Failed to import command '{command}', check debug logs for errors.")
            import traceback
            print(traceback.format_exc())


def create_alias(name: str, description: str, creation_callback: Callable[[ArgumentParser], None],
                 run_callback: Callable[[ArgumentParser, Namespace], int], visible: bool = True) -> None:
    create(name, description, creation_callback, run_callback, is_alias=True, visible=visible)


def create(name: str, description: str, creation_callback: Callable[[ArgumentParser], None],
           run_callback: Callable[[ArgumentParser, Namespace], int], is_alias: bool = False, visible: bool = True,
           aliases: list[str] = None) -> None:
    if aliases is None:
        aliases = []
    print(
        f"Creating command '{name}'\n\tDescription: '{description}'\n\tAlias: {is_alias}\n\tVisible: {visible}\n\tAliases: {', '.join(aliases)}")
    __cmd_data.append(CommandData([name, *aliases], description, creation_callback, run_callback, is_alias, visible))
