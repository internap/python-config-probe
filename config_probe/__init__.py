import collections
import glob
import json
import os

import yaml
from munch import Munch, iteritems

from config_probe.exceptions import ConfigNotFound

NAMESPACE_PLACEHOLDER = "(*)"


def probe(path, patterns):
    config = {}

    for pattern in patterns:

        glob_pattern = pattern.replace(NAMESPACE_PLACEHOLDER, "*")
        for config_file in glob.glob(os.path.join(path, glob_pattern)):
            relevant_part_of_the_path = config_file if os.path.isabs(pattern) else config_file[len(path) + 1:]
            path_parts, ext = os.path.splitext(relevant_part_of_the_path)
            path_matchers, _ = os.path.splitext(pattern)

            namespaces = _deduce_namespaces(path_matchers, path_parts)

            with open(config_file) as f:
                new_values = _parsers[ext](f)

            _add_to_configuration(config, namespaces, new_values)

    return _munchify(config)


def fake_probe(content):
    return _munchify(content)


_parsers = {
    ".yaml": lambda f: yaml.load(f) or {},
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

    _update(current_level, new_values)


def _update(config, values):
    for k, v in values.items():
        if k in config and isinstance(v, collections.Mapping):
            _update(config[k], v)
        else:
            config[k] = v


class _Munch(Munch):
    def __getattr__(self, k):
        try:
            return super(_Munch, self).__getattr__(k)
        except AttributeError as e:
            raise ConfigNotFound(e)


def _munchify(x):
    if isinstance(x, dict):
        return _Munch((k, _munchify(v)) for k,v in iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(_munchify(v) for v in x)
    else:
        return x
