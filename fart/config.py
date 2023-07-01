import os
from pathlib import Path

import toml


def __config_home() -> Path:
    # Give a higher priority to those names
    if "posix" in os.name or "linux" in os.name or "bsd" in os.name or "aix" in os.name or "sunos" in os.name or "haiku" in os.name or "serenity" in os.name:
        from xdg_base_dirs import xdg_config_home
        return xdg_config_home()
    # Windows check
    if "win" in os.name or "nt" in os.name:
        return Path(os.getenv("APPDATA", os.path.expanduser("~")))

    # Fallback
    from xdg_base_dirs import xdg_config_home
    return xdg_config_home()


def __data_home() -> Path:
    # Give a higher priority to those names
    if "posix" in os.name or "linux" in os.name or "bsd" in os.name or "aix" in os.name or "sunos" in os.name or "haiku" in os.name or "serenity" in os.name:
        from xdg_base_dirs import xdg_data_home
        return xdg_data_home()
    # Windows check
    if "win" in os.name or "nt" in os.name:
        return Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~")))

    # Fallback
    from xdg_base_dirs import xdg_data_home
    return xdg_data_home()


PROGRAM_NAME: str = "fart"
CONFIG_DIR: Path = __config_home() / PROGRAM_NAME
CONFIG_FILE: Path = CONFIG_DIR / "config.toml"
DATA_DIR: Path = __data_home() / PROGRAM_NAME

COMPILER_FLAGS_PRESETS: dict[str, list[str]] = {"none": ["-O0", "-g"]}
COMPILER_FLAGS_PRESETS["default"] = [*COMPILER_FLAGS_PRESETS["none"], "-Wall", "-Wextra", "-Werror"]
COMPILER_FLAGS_PRESETS["hardened"] = [*COMPILER_FLAGS_PRESETS["default"], "-Wpedantic"]

POSSIBLE_VALUES = {
    "general.log_symbols": ["ascii", "unicode", "emoji"],
}

DEFAULT_CONFIG = {
    "logging": {
        "log_symbols": "ascii",
        "log_brackets": True,
    },
    "commands": {
        "compiler_command": "clang",
        "compiler_flags": COMPILER_FLAGS_PRESETS["default"],
        "norminette_command": "norminette",
        "norminette_flags": [],
        "valgrind_command": "valgrind",
        "valgrind_flags": ["--leak-check=full", "--show-leak-kinds=all", "--track-origins=yes", "--verbose",
                           "--log-file=valgrind-out.txt"],
    },
    "check": {
        "disabled_checks": [],
        "show_success": False,
    },
}

__config: dict = {}
__first_launch: bool = False


def load_config() -> dict:
    print(f"Loading configuration from {CONFIG_FILE}")
    global __config
    global __first_launch

    if not CONFIG_FILE.exists():
        __first_launch = True
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(toml.dumps(DEFAULT_CONFIG))

    __config = toml.loads(CONFIG_FILE.read_text())

    def fix_layer(layer: dict, against: dict) -> None:
        for key, value in against.items():
            if key not in layer:
                layer[key] = value
            elif isinstance(value, dict):
                print("Fixing config (" + key + ")")
                fix_layer(layer[key], against[key])

    print("Fixing config (root)")
    fix_layer(__config, DEFAULT_CONFIG)

    return __config


def save_config() -> None:
    print(f"Saving configuration to {CONFIG_FILE}")

    CONFIG_FILE.write_text(toml.dumps(__config))


def get_config(default: bool = False) -> dict:
    if default:
        return DEFAULT_CONFIG
    return __config


def is_first_launch() -> bool:
    return __first_launch
