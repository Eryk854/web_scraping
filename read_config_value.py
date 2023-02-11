import os.path
from typing import Any

import yaml


def read_config_value(key: str) -> Any:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "config.yaml")
    with open(path, "r") as file:
        value = yaml.load(file, Loader=yaml.FullLoader)
        value = value[key]
        return value