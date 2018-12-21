# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections
import typing

from dewi.core.command import Command
from dewi.core.context import Context


class Plugin:
    """
    A plugin is an extension of DEWI.
    By default it depends on CorePlugin, which has no dependency.
    """

    def get_description(self) -> str:
        raise NotImplementedError

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}

    def load(self, c: Context):
        raise NotImplementedError

    @staticmethod
    def _r(c: Context, t: typing.Type[Command]):
        """
        Registers a Command type into commommandregistry.

        >> from dewi.commands.edit import EditCommand
        >> from dewi.core.context import Context
        >> from dewi.loader.plugin import Plugin
        >>
        >>
        >>  class EditPlugin(Plugin):
        >>      def get_description(self) -> str:
        >>          return 'Provides "edit" command wrapping "vim"'
        >>
        >>      def load(self, c: Context):
        >>          self._r(c, EditCommand)
        >>
        """
        c.commands.register_class(t)
