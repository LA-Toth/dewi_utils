# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import argparse
import collections
import sys

from dewi.core.context import Context
from dewi.loader.loader import PluginLoader
from dewi.loader.plugin import Plugin


class DewiPlugin(Plugin):
    def get_description(self) -> str:
        return "DEWI application plugin"

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin', 'dewi.commands.FileManipulationPlugin'}

    def load(self, c: Context):
        pass


class MainApplication:
    def __init__(self, loader: PluginLoader, program_name: str):
        self.__loader = loader
        self.__program_name = program_name

    def __parse_app_args(self, args: collections.Iterable):
        parser = argparse.ArgumentParser(
            prog=self.__program_name,
            usage='%(prog)s [options] [command [command-args]]')
        parser.add_argument(
            '-p', '--plugin', help='Load this plugin. This option can be specified more than once.',
            default=[], action='append')
        parser.add_argument('command', nargs=1, help='Command to be run')
        parser.add_argument(
            'commandargs', nargs=argparse.REMAINDER, help='Additonal options and arguments of the specified command',
            default=[],)
        return parser.parse_args(args)

    def run(self, args: collections.Iterable):
        app_ns = self.__parse_app_args(args)

        plugins = app_ns.plugin or ['dewi.core.application.DewiPlugin']
        plugins.append('dewi.core.commandregistry.CommandRegistryPlugin')
        try:
            context = self.__loader.load(set(plugins))
            command_name = app_ns.command[0]

            command_class = context['commandregistry'].get_command_class_descriptor(command_name).get_class()
            command = command_class()
            parser = argparse.ArgumentParser(
                description=command.description,
                prog='{} {}'.format(self.__program_name, command.name))

            command.register_arguments(parser)
            ns = parser.parse_args(app_ns.commandargs)
            sys.exit(command.run(ns))
        except SystemExit:
            raise
        except BaseException as exc:
            print(exc, file=sys.stderr)
            sys.exit(1)

        sys.exit(0)
