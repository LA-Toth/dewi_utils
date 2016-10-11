# Copyright 2016 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import enum
import typing

CORE_CATEGORY = 'core'


class Level(enum.Enum):
    DEBUG = 'debug'
    INFO = 'INFO'
    WARNING = '*WARNING*'
    ERROR = '**** ERROR ****'


class Message:
    def __init__(self, level: Level, category, message: str, details: typing.Optional[dict] = None):
        self.level = level
        self.category = category
        self.message = message
        self.details = details


class Messages:
    """
     @type _messages typing.Dict[Level, typing.List[Message]]
     """

    def __init__(self):
        self._messages = dict()
        for level in Level:
            self._messages[level] = list()

    def add(self, level: Level, category, message: str, details: typing.Optional[dict] = None):
        self._messages[level].append(Message(level, category, message, details))

    @property
    def messages(self) -> typing.Dict[Level, typing.List[Message]]:
        return self._messages

    def print_without_category(self):
        for level in Level:
            for msg in self._messages[level]:
                print("[{}] {}".format(level.value, msg.message))
