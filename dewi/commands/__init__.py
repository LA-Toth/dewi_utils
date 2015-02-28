# Copyright (c) 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import collections

from dewi.commands.edit.edit import EditCommand
from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class FileManipulationPlugin(Plugin):
    def get_description(self) -> str:
        return "File manipulation commnads"

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}

    def load(self, c: Context):
        c['commands'].register_class(EditCommand)
