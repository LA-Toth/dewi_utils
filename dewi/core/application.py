# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import collections
from dewi.core.commandregistry import CommandRegistryException

from dewi.core.context import Context
from dewi.loader.loader import PluginLoader, PluginLoaderError
from dewi.loader.plugin import Plugin


class DewiPlugin(Plugin):
    def get_description(self) -> str:
        return "DEWI application plugin"

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}

    def load(self, c: Context):
        pass


class MainApplication:
    def run(self, plugins: collections.Iterable, args: collections.UserList):
        if len(args) < 1:
            print("Required parameter, command is missing")
            return 1

        loader = PluginLoader()
        try:
            context = loader.load(set(plugins))
            command_name = args[0]
            desc = context['commandregistry'].get_command_class_descriptor(command_name)
            return desc.get_class()().perform(args[1:])
        except (CommandRegistryException, PluginLoaderError) as exc:
            print(str(exc))
            return 1
