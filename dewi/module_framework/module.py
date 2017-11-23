# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import typing

from dewi.config.config import Config
from dewi.module_framework.messages import Level, Messages


class GenericModule:
    def __init__(self,
                 config: Config,
                 messages: Messages,
                 *,
                 add_messages_to_config: bool = False,
                 messages_config_key: typing.Optional[str] = None):
        self._config = config
        self._messages = messages
        self._messages_config_key = messages_config_key or 'messages'
        self._save_msg_to_cfg = add_messages_to_config

    def set(self, entry: str, value):
        self._config.set(entry, value)

    def append(self, entry: str, value):
        self._config.append(entry, value)

    def get(self, entry: str):
        return self._config.get(entry)

    def add_message(self,
                    level: Level, category: str, sub_category: str, message: str,
                    *,
                    hint: typing.Optional[typing.Union[typing.List[str], str]] = None,
                    details: typing.Optional[typing.Union[typing.List[str], str]] = None):

        self._messages.add(level, category, sub_category, message, hint=hint, details=details)

        if self._save_msg_to_cfg:
            msg_dict = dict(
                level=level.name,
                category=category,
                sub_category=category,
                message=message,
            )

            if hint:
                if isinstance(hint, str):
                    hint = [hint]
                msg_dict['hint'] = hint

            if details:
                if isinstance(details, str):
                    details = [details]
                msg_dict['details'] = details

            self._config.append(
                '{}.{}.{}'.format(self._messages_config_key, category, sub_category),
                msg_dict
            )


class Module(GenericModule):
    def require(self) -> typing.List[str]:
        """A list of tags that should be provided by another module."""
        return []

    def provide(self) -> str:
        """
        Provides a tag identifying current module.

        Multiple modules can have same tag, but each of them must have different filter tag if ModuleRunner is in use.
        """
        raise NotImplementedError()

    def get_filter_tags(self) -> typing.List[str]:
        """
        Prefilter the module for instance by OS or by product name depending on the client of module framework.

        If ModuleRunner is in use, each different filter tag must contain unique provided tag list:
        if two modules have both same filter tag and both have the same provided tag, it is an error.
        """
        return []

    def run(self):
        pass
