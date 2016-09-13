# Copyright 2016 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3


class InvalidEntry(KeyError):
    pass


class Config:
    def __init__(self):
        self._config = dict()

    def get_config(self):
        return dict(self._config)

    def set(self, entry: str, value):
        parents = entry.split('.')
        key = parents.pop()
        c = self._config

        for parent in parents:
            if parent not in c:
                c[parent] = dict()

            c = c[parent]

        if key in c and isinstance(c[key], (dict, tuple)):
            raise InvalidEntry("The '{}' entry should not refer either a dict or a list".format(entry))

        c[key] = value

    def get(self, entry: str):
        keys = entry.split('.')
        c = self._config

        try:
            for key in keys:
                c = c[key]
        except KeyError:
            return None

        return c

    def print(self, file=None):
        self._print(self._config, '', file=file)

    def _print(self, config: dict, prefix: str, file=None):
        for k in sorted(config.keys()):
            v = config[k]

            if isinstance(v, dict):
                self._print(v, "{}{}.".format(prefix, k), file=file)
            else:
                print("{}{}: {}".format(prefix, k, v), file=file)
