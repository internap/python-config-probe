import glob
import json

import os
import yaml
from munch import munchify

NAMESPACE_PLACEHOLDER = "(*)"


def probe(path, patterns):
    config = {}

    for pattern in patterns:

        glob_pattern = pattern.replace(NAMESPACE_PLACEHOLDER, "*")
        for config_file in glob.glob(os.path.join(path, glob_pattern)):
            relevant_part_of_the_path = config_file[len(path) + 1:]
            path_parts, ext = os.path.splitext(relevant_part_of_the_path)
            path_matchers, _ = os.path.splitext(pattern)

            namespaces = _deduce_namespaces(path_matchers, path_parts)

            with open(config_file) as f:
                new_values = _parsers[ext](f)

            _add_to_configuration(config, namespaces, new_values)

    return munchify(config)


def fake_probe(content):
    return munchify(content)


_parsers = {
    ".yaml": lambda f: yaml.load(f),
    ".json": lambda f: json.load(f),
}


def _deduce_namespaces(path_matchers, path_parts):
    namespaces = []
    path_parts, current_part = os.path.split(path_parts)
    path_matchers, matcher = os.path.split(path_matchers)
    while current_part is not "":
        if matcher == NAMESPACE_PLACEHOLDER:
            namespaces.append(current_part)

        path_parts, current_part = os.path.split(path_parts)
        path_matchers, matcher = os.path.split(path_matchers)
    return reversed(namespaces)


def _add_to_configuration(config, namespaces, new_values):
    current_level = config
    for ns in namespaces:
        if ns not in current_level:
            current_level[ns] = {}
        current_level = current_level[ns]

    current_level.update(new_values)
