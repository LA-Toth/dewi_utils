# Copyright (c) 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import collections

from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class StevenPlugin(Plugin):
    def get_description(self) -> str:
        return "Steven: An example application using DEWI"

    def get_dependencies(self) -> collections.Iterable:
        return {
            'dewi.core.CorePlugin',
            'dewi.commands.CommandsPlugin',
            'steven.commands.CommandsPlugin',
        }

    def load(self, c: Context):
        pass
