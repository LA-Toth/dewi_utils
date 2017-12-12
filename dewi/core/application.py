# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import collections
import sys
import traceback

from dewi.core import CommandRegistrar
from dewi.core.command import Command
from dewi.core.commandregistry import CommandRegistry
from dewi.core.context import Context
from dewi.loader.loader import PluginLoader
from dewi.loader.plugin import Plugin


class DewiPlugin(Plugin):
    def get_description(self) -> str:
        return "DEWI application plugin"

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin', 'dewi.commands.CommandsPlugin'}

    def load(self, c: Context):
        pass


def _list_comands(prog_name: str, command_registry: CommandRegistry, *, all_commands: bool = False):
    max_length = 0
    commands = dict()
    for name in command_registry.get_command_names():
        desc = command_registry.get_command_class_descriptor(name)
        command = desc.get_class()
        command_name = desc.get_name()

        if name == command_name:
            cmdname = name
        else:

            if not all_commands:
                continue
            cmdname = '{0}      - alias of {1}'.format(name, command_name)

        if len(cmdname) > max_length:
            max_length = len(cmdname)

        commands[name] = (cmdname, command.description)

    format_str = "  {0:<" + str(max_length) + "}   -- {1}"

    print(f'Available {prog_name.capitalize()} Commands.')
    for name in sorted(commands):
        cmdname, description = commands[name]
        print(format_str.format(cmdname, description))


class ListAllCommand(Command):
    name = 'list-all'
    description = 'Lists all available command with aliases'

    def run(self, args: argparse.Namespace):
        context: Context = args._context_
        command_registry: CommandRegistry = context['commandregistry']
        _list_comands(args._program_name_, command_registry, all_commands=True)


class ListCommand(Command):
    name = 'list'
    description = 'Lists all available command with their names only'

    def run(self, args: argparse.Namespace):
        context: Context = args._context_
        command_registry: CommandRegistry = context['commandregistry']
        _list_comands(args._program_name_, command_registry)


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
        parser.add_argument('--wait', action='store_true', help='Wait for user input before terminating application')
        parser.add_argument(
            '--print-backtraces', action='store_true',
            help='Print backtraces of the exceptions')
        parser.add_argument('--debug', '-d', action='store_true', help='Enable print/log debug messages')
        parser.add_argument('command', nargs='?', help='Command to be run', default='list')
        parser.add_argument(
            'commandargs', nargs=argparse.REMAINDER, help='Additonal options and arguments of the specified command',
            default=[], )
        return parser.parse_args(args)

    def run(self, args: collections.Iterable):
        app_ns = self.__parse_app_args(args)
        if app_ns.debug:
            app_ns.print_backtraces = True

        plugins = app_ns.plugin or ['dewi.core.application.DewiPlugin']
        plugins.append('dewi.core.commandregistry.CommandRegistryPlugin')

        try:
            context = self.__loader.load(set(plugins))
            command_name = app_ns.command

            command_registry: CommandRegistry = context['commandregistry']
            command_registrar: CommandRegistrar = context['commands']

            command_registrar.register_class(ListAllCommand)
            command_registrar.register_class(ListCommand)

            if command_name in command_registry:

                command_class = command_registry.get_command_class_descriptor(command_name).get_class()
                command = command_class()
                parser = argparse.ArgumentParser(
                    description=command.description,
                    prog='{} {}'.format(self.__program_name, command_name))

                command.register_arguments(parser)
                ns = parser.parse_args(app_ns.commandargs)
                ns._running_command_ = command_name
                ns._debug_ = app_ns.debug
                ns._print_backtraces_ = app_ns.print_backtraces
                ns._parser = parser
                ns._context_ = context
                ns._program_name_ = self.__program_name
                sys.exit(command.run(ns))

            else:
                print(f"ERROR: The command '{command_name}' is not known.\n")
                print('Available commands with aliases:')
                for name in sorted(command_registry.get_command_names()):
                    print('  {:30s}   -- {}'.format(
                        name,
                        command_registry.get_command_class_descriptor(name).get_class().description))
                sys.exit(1)

        except SystemExit:
            self.__wait_for_termination_if_needed(app_ns)
            raise
        except BaseException as exc:
            if app_ns.print_backtraces:
                einfo = sys.exc_info()
                tb = traceback.extract_tb(einfo[2])
                tb_str = 'An exception occured:\n  Type: %s\n  Message: %s\n\n' % \
                         (einfo[0].__name__, einfo[1])
                for t in tb:
                    tb_str += '  File %s:%s in %s\n    %s\n' % (t.filename, t.lineno, t.name, t.line)
                print(tb_str)
            print(exc, file=sys.stderr)
            self.__wait_for_termination_if_needed(app_ns)
            sys.exit(1)

    def __wait_for_termination_if_needed(self, app_ns):
        if app_ns.wait:
            print("\nPress ENTER to continue")
            input("")
