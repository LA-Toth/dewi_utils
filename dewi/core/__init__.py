# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections

from dewi.core.commandregistry import CommandRegistry, CommandRegistrar
from dewi.core.context import Context

from dewi.loader.plugin import Plugin


class CorePlugin(Plugin):
    def get_description(self):
        return "Core features of DEWI"

    def get_dependencies(self) -> collections.Iterable:
        return ('dewi.core.commandregistry.CommandRegistryPlugin',)

    def load(self, c: Context):
        pass
