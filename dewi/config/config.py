# Copyright 2016-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import typing

import yaml


class InvalidEntry(KeyError):
    pass


class Config:
    def __init__(self):
        self._config = dict()

    def get_config(self):
        return dict(self._config)

    def overwrite_config(self, config: dict):
        self._config = config

    def _top_level_unsafe_set(self, key: str, value):
        self._config[key] = value

    def set(self, entry: str, value):
        c, key = self._get_container_and_key(entry)

        if key in c and isinstance(c[key], (dict, list, set)):
            raise InvalidEntry("The '{}' entry should not refer either a dict, list or set".format(entry))

        c[key] = value

    def _get_container_and_key(self, entry):
        parents = entry.split('.')
        key = parents.pop()
        c = self._config

        for parent in parents:
            if parent not in c:
                c[parent] = dict()

            c = c[parent]

        return c, key

    def append(self, list_entry: str, value):
        c, key = self._get_container_and_key(list_entry)

        if key not in c:
            c[key] = list()

        c[key].append(value)

    def add_to_set(self, list_entry: str, value):
        c, key = self._get_container_and_key(list_entry)

        if key not in c:
            c[key] = set()

        c[key].add(value)

    def get(self, entry: str):
        keys = entry.split('.')
        c = self._config

        try:
            for key in keys:
                c = c[key]
        except KeyError:
            return None

        return c

    def delete(self, list_entry: str):
        c, key = self._get_container_and_key(list_entry)
        del c[key]

    def dump(self, file, ignore: typing.Optional[typing.List[str]] = None):
        cfg = self._config
        if ignore:
            cfg = dict(cfg)
            for item in ignore:
                del cfg[item]

        yaml.dump(cfg, file, indent=4, default_flow_style=False)

    def print(self, file=None):
        self._print(self._config, '', file=file)

    def _print(self, config: dict, prefix: str, file=None):
        for k in sorted(config.keys()):
            v = config[k]

            if isinstance(v, dict):
                self._print(v, "{}{}.".format(prefix, k), file=file)
            else:
                print("{}{}: {}".format(prefix, k, v), file=file)
