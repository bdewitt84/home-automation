# ./app/bootstrap/interpolator.py

from typing import Callable
import os
import re


def interpolate_environment_variables(cfg: dict,
                                       env_loader: Callable[[str], str] = os.getenv,
                                       ) -> None:
    pattern = re.compile(r"\${(.*?)}")

    for key, val in cfg.items():
        if isinstance(val, dict):
            interpolate_environment_variables(val, env_loader)
        elif isinstance(val, str):
            match = pattern.search(val)
            if match:
                env_var_name = match.group(1)
                env_val = env_loader(env_var_name)
                if env_val is None:
                    raise ValueError(f"{env_var_name} is not a valid environment variable.")
                else:
                    cfg[key] = env_val
