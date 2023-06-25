from argparse import ArgumentParser, Namespace
from fart.commands import create
from fart.utils import info, log


def __parser(parser: ArgumentParser) -> None:
    parser.add_argument("key", help="the key to change", nargs="?")
    parser.add_argument("value", help="the value to change the key to", nargs="?")
    parser.add_argument("-l", "--list", dest="list", help="list all config values", action="store_true")


def __exec(namespace: Namespace) -> None:
    from fart.config import get_config
    config = get_config()

    def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    flatten = flatten_dict(config)

    if namespace.list:
        info("Config values:")
        for key, value in flatten.items():
            log(f"\t{key}: {value}")
        return


create("config", "change configuration values", __parser, __exec)
