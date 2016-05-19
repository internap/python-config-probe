[![Build Status](https://travis-ci.org/internap/python-config-probe.svg?branch=master)](https://travis-ci.org/internap/python-config-probe)
[![PyPI version](https://badge.fury.io/py/python-config-probe.svg)](http://badge.fury.io/py/python-config-probe)


Mission
=======

Provide an auto-discovery process of configurations for simple code use. Given a path and a list of pattern,
the result config will be a shortcut to any config.

## Usage

Setup:

    config = probe(
        path="path/to/my/files",
        patterns=["path/(*)/file.yaml"]
    )

Use it:

    print config.mynamespace.key

## Parameters

- **path**

    Initial path to probe.  Patterns will be tested against the file structure underneath the path
    and it will be ignored in determining the namespacing.

- **patterns**

    A list of file paths containing (or not) placeholders "(\*)" o find where the configuration files are located.

    Each placeholder in the path will result in a namespace in the resulting config.  So let's say you have a pattern

        dir1/(*)/dir2/(*).yaml

    If this pattern finds the file : "dir1/**ns1**/dir2/**file**.yaml" that contains "key: 'value'", the resulting
    config will be

        config.ns1.file.key == "value"

    now if the pattern was

        dir1/ns1/dir2/file.yaml

    for the same file, the resulting config would simply be

        config.key == "value"

    so you can use placeholders "(\*)" to namespace the resulting config and use "\*" without the parenthesis
    to have a variable path without the namespacing

        dir1/(*)/dir2/*.yaml
        config.ns1.key == "value"

## Mocking the probing

Your unit test can have your code use fake_probe instead to which to give a dict and it will appear as if it
was just probed. Example:

    config = fake_probe({
        "ns1": {
            "file": {
                "key": "value"
            }
        }
    })
    # then
    config.ns1.file.key == "value"

Contributing
============

Feel free to raise issues and send some pull request, we'll be happy to look at them!
