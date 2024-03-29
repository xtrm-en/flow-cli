import importlib.metadata
from argparse import ArgumentParser, Namespace
import sys
import time
import traceback
from typing import Callable

from flow.commands import get_command_data, load_commands
from flow.config import load_config, is_first_launch
from flow.launcher import hijack_streams, restore_streams
from flow.modules import load_modules, get_modules_data, get_modules, log_modules
from flow.setup import initial_setup
from flow.utils import log, error, fatal, success, info


def main() -> int:
    print("Loading flow-cli...")
    load_modules()
    load_config()
    load_commands()

    # required because argparse is cringe
    restore_streams()

    parser = ArgumentParser(exit_on_error=True, add_help=False)
    # Reimplement the `help` argument to override the default help message
    parser.add_argument("--help", "-h", dest="help", help="show this help message and exit", action="store_true")
    parser.add_argument("--version", "-v", dest="version", help="show the program's version number and exit",
                        action="store_true")

    # Subcommands
    replace_target: str = "{DESCRIPTION}"
    commands_parser = parser.add_subparsers(title="subcommands",
                                            dest='command', description=replace_target)
    execs: dict[
        str,
        tuple[Callable[[ArgumentParser, Namespace], int], ArgumentParser]
    ] = {}
    for cmd in get_command_data():
        for name in cmd.names:
            cmd_parser = commands_parser.add_parser(name, help=cmd.description)
            if cmd.creation_callback is not None:
                cmd.creation_callback(cmd_parser)
            execs[name] = (cmd.run_callback, cmd_parser)

    args: Namespace = parser.parse_args()

    hijack_streams()

    if is_first_launch():
        if not initial_setup():
            error("An error occured in the initial setup, aborting...")
            return -1

    if args.version:
        from importlib.metadata import metadata
        data = metadata("flow")
        authors: list[str] = sorted(
            [*data.get_all("Author"), *[it.split("<")[0].strip() for it in data.get_all("Author-email")]]
        )

        success("Running flow-cli v" + data.get("Version"))
        log(" " * 4 + "by " + ", ".join(authors))

        log_modules()

        return 0

    if args.command is None or args.help:
        def create_desc() -> str:
            """Create a custom description format to hold aliases and subcommands as separate categories/groups."""

            def spacing(provided: str) -> str:
                return " " * (22 - len(provided))
            subcommand_helps: list[str] = [
                (" " * 2 + c.names[0] + spacing(c.names[0]) + c.description) for c in get_command_data() if not c.alias and c.visible
            ]
            alias_helps: list[str] = [
                (" " * 2 + c.names[0] + spacing(c.names[0]) + c.description) for c in get_command_data() if c.alias
            ]

            return "\n".join(subcommand_helps) + ("\n" * 2) + "aliases:\n" + "\n".join(alias_helps) + "\n"

        def replace_first_line(text: str, replace_with: str) -> str:
            lines: list[str] = text.split("\n")
            first_index: int = -1
            second_index: int = -1
            line_index = 0
            for i in range(3):
                try:
                    first_index = lines[line_index].index('{')
                    second_index = lines[line_index].index('}')
                    break
                except ValueError:
                    line_index += 1
            if first_index != -1 and second_index != -1:
                lines[line_index] = lines[line_index][:first_index] + replace_with + lines[line_index][second_index+1:]
            return "\n".join(lines)

        help_str: str = parser.format_help()
        help_str = replace_first_line(help_str, "<subcommand or alias>")

        index: int = help_str.find(replace_target)
        assert index != -1
        overwritten_help: str = help_str[:index-2] + create_desc()
        sys.__stdout__.write(overwritten_help)
        return 0

    start_time = time.time()
    print(f"Running subcommand '{args.command}'...")
    target, parser = execs[args.command]
    code: int
    # noinspection PyBroadException
    try:
        code = target(parser, args)
    except Exception:
        error(f"An error occurred while running subcommand '{args.command}', aborting.")
        fatal(traceback.format_exc())
        code = -3
    print(f"Finished subcommand '{args.command}' in {round(time.time() - start_time, 2)} seconds, return code: {code}.")

    return code
