import argparse
import sys
import time
import traceback
from typing import Callable

from fart.commands import get_command_data, load_commands
from fart.config import load_config
from fart.launcher import hijack_streams, restore_streams
from fart.utils import log, error, fatal


def main() -> int:
    print("Loading F.A.R.T...")
    load_config()
    load_commands()

    # required because argparse is cringe
    restore_streams()

    parser = argparse.ArgumentParser(exit_on_error=True, formatter_class=CustomFormatter)
    parser.add_argument("-v", "--version", dest="version", help="show the program's version number and exit",
                        action="store_true")
    # Aliases
    # TODO

    # Subcommands
    commands_parser = parser.add_subparsers(title="subcommands",
                                            dest='subcommand', description="description custom")
    # custom_description: str = ""

    subcommand_execs: dict[
        str,
        tuple[Callable[[argparse.ArgumentParser, argparse.Namespace], int], argparse.ArgumentParser]
    ] = {}
    for cmd in get_command_data():
        cmd_parser = commands_parser.add_parser(cmd.name, help=cmd.description)
        if cmd.creation_callback is not None:
            cmd.creation_callback(cmd_parser)
        subcommand_execs[cmd.name] = (cmd.run_callback, cmd_parser)

    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    args = parser.parse_args()

    hijack_streams()
    # log(args)
    if args.version:
        from importlib.metadata import version
        log("Running fart-cli", end=" ")
        log(version("fart"))
        return 0

    if args.subcommand is None:
        parser.print_help(file=sys.__stdout__)
        return 0

    start_time = time.time()
    print(f"Running subcommand '{args.subcommand}'...")
    target, parser = subcommand_execs[args.subcommand]
    code: int
    # noinspection PyBroadException
    try:
        code = target(parser, args)
    except Exception as e:
        error(f"An error occurred while running subcommand '{args.subcommand}', aborting.")
        fatal(traceback.format_exc())
        code = -3
    print(f"Finished subcommand '{args.subcommand}' in {round(time.time() - start_time, 2)} seconds, return code: {code}.")

    return code


# noinspection PyShadowingBuiltins
class CustomFormatter(argparse.HelpFormatter):
    def __init__(self,
                 prog,
                 indent_increment=2,
                 max_help_position=24,
                 width=None):
        super().__init__(prog, indent_increment, max_help_position, width)

    def format_help(self) -> str:
        help = self._root_section.format_help()
        if help:
            help = self._long_break_matcher.sub('\n\n', help)
            help = help.strip('\n') + '\n'
        print("what the fuck:\n" + help + "\n---- end ---")
        return help
