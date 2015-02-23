# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3
from dewi.core.commandregistry import CommandRegistry, CommandRegistrar
from dewi.core.context import Context

from dewi.loader.plugin import Plugin


class CorePlugin(Plugin):
    def get_description(self):
        return "Core features of DEWI"

    def load(self, c: Context):
        c.register('commandregistry', CommandRegistry())
        c.register('commands', CommandRegistrar(c['commandregistry']))
