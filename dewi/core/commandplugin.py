# Copyright 2017-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections
import types
import typing

from dewi.core.command import Command
from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class CommandPlugin(Plugin):
    command: typing.Type[Command]

    def get_description(self) -> str:
        return 'Command plugin of: ' + self.command.description

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}

    def load(self, c: Context):
        c.commands.register_class(self.command)

    @classmethod
    def create(cls, command: typing.Type[Command]) -> typing.Type[Plugin]:
        class_name = command.__name__
        if class_name.endswith('Command'):
            class_name = class_name[:-len('Command')]
        class_name += 'Plugin'

        cls_dict = {
            'command': command
        }

        return types.new_class(class_name, (CommandPlugin,), {}, lambda ns: ns.update(cls_dict))
