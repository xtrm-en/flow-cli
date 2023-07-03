# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser, Namespace

from flow.commands import create
from flow.modules import add_module, remove_module, update_module, log_modules
from flow.utils import error


def __parser(parser: ArgumentParser):
    subparsers = parser.add_subparsers(title="module", dest="subcommand")

    add_parser = subparsers.add_parser("add", help="fetches a remote module from a git url")
    add_parser.add_argument("target", help="the git url to fetch the module from")

    remove_parser = subparsers.add_parser("remove", help="removes a module from the local modules directory")
    remove_parser.add_argument("target", help="the name of the module to remove")

    update_parser = subparsers.add_parser("update", help="updates your modules")
    update_parser.add_argument("target", help="the name of the module to update", nargs="?")

    subparsers.add_parser("list", help="lists all installed modules")


def __exec(parser: ArgumentParser, args: Namespace) -> int:
    if args.subcommand is None:
        parser.print_help(file=sys.__stdout__)
        return 1
    if args.subcommand == "add":
        return 0 if add_module(args.target) else 1
    if args.subcommand == "remove":
        return 0 if remove_module(args.target) else 1
    if args.subcommand == "update":
        return 0 if update_module(args.target) else 1
    if args.subcommand == "list":
        log_modules()
        return 0
    error(f"Unknown subcommand: {args.subcommand}")
    return 1


create("module", "manages flow modules", __parser, __exec)
