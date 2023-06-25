import toml
from xdg_base_dirs import xdg_config_home

CONFIG_FILE = xdg_config_home() / "fart" / "config.toml"

COMPILER_FLAGS_PRESETS: dict[str, list[str]] = {
    "none": [],
    "default": ["-Wall", "-Wextra", "-Werror"],
    "hardened": ["-Wall", "-Wextra", "-Werror", "-Wpedantic"],
    "hardcore": ["-Wall", "-Wextra", "-Werror", "-Wpedantic", "-Wno-unused-parameter", "-Wno-unused-variable",
                 "-Wno-unused-function", "-Wno-unused-but-set-variable", "-Wno-unused-but-set-parameter",
                 "-Wno-unused-value", "-Wno-unused-label", "-Wno-unused-result", "-Wno-unused-local-typedefs",
                 "-Wno-unused-macros"]
}

DEFAULT_CONFIG = {
    "logging": {
        "log_symbols": "ascii",
        "log_brackets": True,
    },
    "commands": {
        "compiler_command": "gcc",
        "compiler_flags": COMPILER_FLAGS_PRESETS["default"],
        "norminette_command": "norminette",
        "norminette_flags": [],
    },
    "check": {
        "checks": ["norminette", "gcc"],
    },
}

POSSIBLE_VALUES = {
    "general.log_symbols": ["ascii", "unicode", "emojis"],
    "check.checks": ["norminette", "gcc"],
}

__config: dict = {}


def load_config() -> dict:
    print(f"Loading configuration from {CONFIG_FILE}")
    global __config

    if not CONFIG_FILE.exists():
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
    global __config

    CONFIG_FILE.write_text(toml.dumps(__config))


def get_config() -> dict:
    global __config
    return __config
