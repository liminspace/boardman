from typing import Any, Dict

import yaml


def get_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r") as f:
        return yaml.load(f.read(), yaml.CLoader)
