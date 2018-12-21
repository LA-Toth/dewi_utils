# Copyright 2017-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi.core.context import Context
from dewi.loader.plugin import Plugin

from steven.commands.xssh import XSshCommand


class CommandsPlugin(Plugin):
    def get_description(self) -> str:
        return "Steve: A set of tools for Support"

    def load(self, c: Context):
        self._r(c, XSshCommand)
