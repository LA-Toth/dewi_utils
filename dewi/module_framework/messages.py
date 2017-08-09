# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import enum
import typing

CORE_CATEGORY = 'Core'

_levels = {
    'd': '     debug     ',
    'i': ' .   INFO    . ',
    'w': ' *  WARNING  * ',
    'e': ' *** ERROR *** '
}


class Level(enum.Enum):
    DEBUG = _levels['d']
    INFO = _levels['i']
    WARNING = _levels['w']
    ERROR = _levels['e']


class Message:
    def __init__(self,
                 level: Level, category: str, sub_category: str, message: str,
                 *,
                 hint: typing.Optional[typing.List[str]] = None,
                 details: typing.Optional[typing.List[str]] = None):
        self.level = level
        self.category = category
        self.subcategory = sub_category
        self.message = message
        self.hint = hint
        self.details = details


class Messages:
    """
     @type _messages typing.Dict[Level, typing.List[Message]]
     """

    def __init__(self):
        self._messages = dict()
        for level in Level:
            self._messages[level] = list()

    def add(self, level: Level, category: str, sub_category: str, message: str,
            *,
            hint: typing.Optional[typing.Union[typing.List[str], str]] = None,
            details: typing.Optional[typing.Union[typing.List[str], str]] = None):
        if isinstance(hint, str):
            hint = [hint]
        if isinstance(details, str):
            details = [details]
        self._messages[level].append(Message(level, category, sub_category, message, hint=hint, details=details))

    @property
    def messages(self) -> typing.Dict[Level, typing.List[Message]]:
        return self._messages

    def print_without_category(self):
        for level in Level:
            for msg in self._messages[level]:
                print("[{}] {}".format(level.value, msg.message))
