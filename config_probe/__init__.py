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

            with open(config_file) as f:
                result = _parsers[ext](f)

            path_parts, current_part = os.path.split(path_parts)
            path_matchers, matcher = os.path.split(path_matchers)
            while current_part is not "":
                if matcher == NAMESPACE_PLACEHOLDER:
                    result = {current_part: result}
                path_parts, current_part = os.path.split(path_parts)
                path_matchers, matcher = os.path.split(path_matchers)

            config.update(result)

    return munchify(config)


def fake_probe(content):
    return munchify(content)


_parsers = {
    ".yaml": lambda f: yaml.load(f),
    ".json": lambda f: json.load(f),
}
