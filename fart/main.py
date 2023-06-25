import argparse
from fart.commands import get_command_data, load_commands
from fart.config import load_config
from fart.launcher import hijack_streams, restore_streams
from fart.utils import log, set_unicode_symbols
import time


def main() -> None:
    print("Loading F.A.R.T...")
    config = load_config()

    set_unicode_symbols(config["logging"]["log_symbols"])

    load_commands()

    # required because argparse is cringe
    restore_streams()

    global_args = argparse.ArgumentParser(exit_on_error=True)
    global_args.add_argument("-v", "--version", dest="version", help="show the program's version number and exit",
                             action="store_true")

    # Subcommands
    commands_parser = global_args.add_subparsers(title="subcommands", help='available subcommands',
                                                 dest='subcommand')
    subcommand_execs = {}
    for cmd in get_command_data():
        cmd_parser = commands_parser.add_parser(cmd.name, help=cmd.description)
        if cmd.creation_callback is not None:
            cmd.creation_callback(cmd_parser)
        subcommand_execs[cmd.name] = cmd.run_callback

    args = global_args.parse_args()

    if args.version:
        hijack_streams()
        from importlib.metadata import version
        log("Running fart-cli", end=" ")
        log(version("fart"))
        return

    if args.subcommand is None:
        global_args.print_help()
        return

    hijack_streams()

    start_time = time.time()
    print(f"Running subcommand '{args.subcommand}'...")
    subcommand_execs[args.subcommand](args)
    print(f"Finished subcommand '{args.subcommand}' in {round(time.time() - start_time, 2)} seconds.")
