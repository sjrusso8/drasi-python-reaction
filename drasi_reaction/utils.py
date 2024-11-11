import json
from io import TextIOWrapper
from typing import Any

import yaml


def json_query_configs(val: TextIOWrapper) -> Any:
    return json.load(val)


def yaml_query_configs(val: TextIOWrapper) -> Any:
    return yaml.safe_load(val)
