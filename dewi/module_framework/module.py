# Copyright 2016 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import typing

from dewi.module_framework.config import Config
from dewi.module_framework.messages import Messages, Level


class Module:
    def __init__(self, config: Config, messages: Messages, *, add_messages_to_config: bool = False):
        self._config = config
        self._messages = messages
        if add_messages_to_config:
            self.add_message = self._add_message_to_config_too

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

    def _add_message(self, level: Level, category, message: str):
        self._messages.add(level, category, message)

    def _add_message_to_config_too(self, level: Level, category, message: str):
        self._messages.add(level, category, message)
        self._config.append(
            '_messages',
            dict(
                level=level.name,
                category=category,
                message=message,
            )
        )

    add_message = _add_message
