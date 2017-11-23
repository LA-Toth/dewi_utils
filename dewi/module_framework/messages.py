# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import enum
import typing

CORE_CATEGORY = 'Core'

_levels = {
    'd': '     debug     ',
    'i': ' .   INFO    . ',
    'w': ' *  WARNING  * ',
    'a': ' *** ALERT *** '
}


class Level(enum.Enum):
    DEBUG = _levels['d']
    INFO = _levels['i']
    WARNING = _levels['w']
    ALERT = _levels['a']


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

    @property
    def as_dict(self) -> dict:
        return dict(
            level=self.level.name,
            category=self.category,
            subcategory=self.subcategory,
            message=self.message,
            hint=self.hint,
            details=self.details
        )


class Messages:
    def __init__(self):
        self._messages: typing.Dict[str, typing.Dict[str, typing.List[Message]]] = dict()
        self._alerts: typing.List[str] = list()
        self._warnings: typing.List[str] = list()

    def add(self, level: Level, category: str, sub_category: str, message: str,
            *,
            hint: typing.Optional[typing.Union[typing.List[str], str]] = None,
            details: typing.Optional[typing.Union[typing.List[str], str]] = None):
        if isinstance(hint, str):
            hint = [hint]
        if isinstance(details, str):
            details = [details]

        self._add(level, category, sub_category, message, hint, details)

    def _add(self,
             level: Level, category: str, sub_category: str, message: str,
             hint: typing.Optional[typing.List[str]] = None,
             details: typing.Optional[typing.List[str]] = None):

        if category not in self._messages:
            self._messages[category] = dict()

        if sub_category not in self._messages[category]:
            self._messages[category][sub_category] = list()

        self._messages[category][sub_category].append(
            Message(level, category, sub_category, message, hint=hint, details=details))

        if level == Level.ALERT:
            self._alerts.append(message)
        elif level == Level.WARNING:
            self._warnings.append(message)

    @property
    def messages(self) -> typing.Dict[str, typing.Dict[str, typing.List[Message]]]:
        return self._messages

    @property
    def as_dict(self) -> typing.Dict[str, typing.Dict[str, typing.List[dict]]]:
        result = dict()
        for c in self._messages:
            result[c] = dict()
            for sc in self._messages[c]:
                result[c][sc] = list()
                for msg in self._messages[c][sc]:
                    result[c][sc].append(msg.as_dict)

        return result

    @property
    def alerts(self) -> typing.List[str]:
        return self._alerts

    @property
    def warnings(self) -> typing.List[str]:
        return self._warnings

    def print_without_category(self):
        for category in self._messages:
            msg_with_subcategories = self._messages[category]
            for subcategory in msg_with_subcategories:
                messages = msg_with_subcategories[subcategory]
                for msg in messages:
                    c = category
                    if category != subcategory:
                        c += ' :: ' + subcategory
                    print("[{}] {}:: {}".format(msg.level.value, c, msg.message))
