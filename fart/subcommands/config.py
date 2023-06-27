# -*- coding: utf-8 -*-
from argparse import ArgumentParser, Namespace

import inquirer

from fart.commands import create
from fart.config import get_config, save_config, COMPILER_FLAGS_PRESETS
from fart.utils import info, log, error, warn, prompt, parse, stringify


def __parser(parser: ArgumentParser) -> None:
    parser.add_argument("-l", "--list", dest="list", help="list all config values", action="store_true")
    parser.add_argument("-c", "--changed", dest="changed", help="list only changed config values", action="store_true")
    parser.add_argument("key", help="the key to change", nargs="?")
    parser.add_argument("value", help="the value to change the key to", nargs="?")


def list_all(flat: dict, flat_default: dict, changed_only: bool = False) -> None:
    info(f"Config values{' (changed)' if changed_only else ''}:", end="")
    found_one = False
    for key, value in flat.items():
        if changed_only and value == flat_default[key]:
            continue
        if not found_one:
            found_one = True
            log("")
        log(f"\t{key}: {stringify(value)}")
        if changed_only:
            log(f"\t\t(default: {stringify(flat_default[key])})")
    if not found_one:
        log(" (none)")


def __exec(_: ArgumentParser, namespace: Namespace) -> None:
    unflattened_config = get_config()

    def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def set_key(flattened_key: str, val: str) -> object:
        keys = flattened_key.split(".")
        current = unflattened_config
        default = get_config(default=True)
        for k in keys[:-1]:
            current = current[k]
            default = default[k]

        parsed_value = parse(val.strip(), type(default[keys[-1]]))
        current[keys[-1]] = parsed_value
        return parsed_value

    flat = flatten_dict(unflattened_config)
    flat_default = flatten_dict(get_config(default=True))

    changed_only: bool = namespace.changed
    if namespace.list:
        list_all(flat, flat_default, changed_only)
        return
    elif changed_only:
        warn("The '--changed' flag is only used with '--list'.")

    key: str = namespace.key
    if key is not None:
        value: object = flat.get(key)
        if value is None:
            error(f"Config key '{key}' does not exist.")
            return

        if namespace.value is not None:
            # TODO: check config#POSSIBLE_VALUES
            result = str(set_key(namespace.key, str(namespace.value)))
            save_config()
            info(f"Set config key '{namespace.key}' to '{result}'")
        else:
            info(f"Config key '{namespace.key}': {flat[namespace.key]}")
        return

    action: str = prompt([
        inquirer.List(
            "action",
            message="What do you want to do",
            choices=["Change a value", "Apply presets", "List all values", "List all changed values", "Exit"],
            carousel=True
        ),
    ])["action"]
    if action.startswith("List all "):
        changed_only = "changed" in action
        list_all(flat, flat_default, changed_only)
    elif action == "Apply presets":
        preset: str = prompt([
            inquirer.List(
                "preset",
                message="Which preset do you want to apply",
                choices=["Compiler Arguments", "Exit"],
                carousel=True
            ),
        ])["preset"]
        if preset == "Compiler Arguments":
            args: str = prompt([
                inquirer.List(
                    "args",
                    message="Pick your preset",
                    choices=[(k[0].upper() + k[1:].lower() + " (" + str(COMPILER_FLAGS_PRESETS[k]) + ")") for k in
                             COMPILER_FLAGS_PRESETS.keys()],
                ),
            ])["args"]
            arg_key = args.split(" ")[0].lower()
            unflattened_config["commands"]["compiler_flags"] = COMPILER_FLAGS_PRESETS[arg_key]
            save_config()
            info(f"Set config key 'commands.compiler_flags' to '{COMPILER_FLAGS_PRESETS[arg_key]}'")
        elif preset != "Exit":
            error("How did you get here?")
    elif action == "Change a value":
        target_dict = unflattened_config
        final_key: str = ""
        while True:
            result: str = prompt([
                inquirer.List(
                    "key",
                    message="Which key do you want to change",
                    choices=list(target_dict.keys()) + ["Exit"],
                    carousel=True
                ),
            ])["key"]
            if result == "Exit":
                break
            elif isinstance(target_dict[result], dict):
                target_dict = target_dict[result]
                final_key += result + "."
            else:
                final_key += result
                value: str = prompt([
                    inquirer.Text(
                        "value",
                        message="What do you want to change it to",
                        default=stringify(target_dict[result])
                    ),
                ])["value"]
                # TODO: check config#POSSIBLE_VALUES
                value = set_key(final_key, value)
                save_config()
                info(f"Set config key '{final_key}' to '{value}'")
                break
    elif action != "Exit":
        error("How did you get here?")


create("config", "change configuration values", __parser, __exec)
