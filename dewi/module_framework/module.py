# Copyright 2016 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import typing

from dewi.module_framework.messages import Messages, Level

from dewi.module_framework.config import Config


class Module:
    def __init__(self, config: Config, messages: Messages):
        self._config = config
        self._messages = messages

    def require(self) -> typing.List[str]:
        return ()

    def provide(self) -> str:
        raise NotImplementedError()

    def run(self):
        pass

    def set(self, entry: str, value):
        self._config.set(entry, value)

    def append(self, entry: str, value):
        self._config.append(entry, value)

    def get(self, entry: str):
        return self._config.get(entry)

    def add_message(self, level: Level, category, message: str):
        self._messages.add(level, category, message)
