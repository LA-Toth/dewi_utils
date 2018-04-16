# Copyright 2015-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi.core.commandregistry import CommandRegistry, CommandRegistrar
from dewi.core.context import Context

from dewi.loader.plugin import Plugin


class CorePlugin(Plugin):
    def get_description(self):
        return "Core features of DEWI"

    def load(self, c: Context):
        pass
