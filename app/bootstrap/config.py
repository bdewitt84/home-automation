import os
import re
from json import load
from typing import Callable, IO


def _interpolate_environment_variables(cfg: dict,
                                       env_loader: Callable[[str], str] = os.getenv,
                                       ) -> None:

    pattern=r"\${(.*?)}"
    re.compile(pattern)

    for key, val in cfg.items():
        if isinstance(val, dict):
            _interpolate_environment_variables(val, env_loader)
        elif isinstance(val, str):
            match = re.search(pattern, val)
            if match:
                env_var_name = match.group(1)
                env_val = env_loader(env_var_name)
                if env_val is None:
                    raise ValueError(f"{env_var_name} is not a valid environment variable.")
                else:
                    cfg[key] = env_val


def read_config(stream: IO[str],
                decoder: Callable[[IO[str]], dict] = load,
                parser: Callable[[dict], dict] = dict,
                ) -> dict:

    try:
        decoded = decoder(stream)
        parsed = parser(decoded)
    except Exception as e:
        raise RuntimeError(f"Critical failure reading config file: {e}") from e

    return parsed


def load_config_from_disk(path: str,
                          reader: Callable[[str, str], IO[str]] = open
                          ) -> dict:

    try:
        with reader(path, 'r') as f:
            config_data = read_config(f)

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")

    return config_data
