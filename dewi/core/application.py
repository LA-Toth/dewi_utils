# Copyright 2015-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import collections
import sys
import traceback

from dewi.core.command import Command
from dewi.core.commandregistry import CommandRegistry
from dewi.core.context import Context
from dewi.core.logger import create_logger, LoggerType, LogLevel, log_debug
from dewi.loader.loader import PluginLoader
from dewi.loader.plugin import Plugin
from dewi.utils.levenstein import get_similar_names_to


class DewiPlugin(Plugin):
    def get_description(self) -> str:
        return "DEWI application plugin"

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin', 'dewi.commands.CommandsPlugin'}

    def load(self, c: Context):
        pass


def _list_comands(prog_name: str, command_registry: CommandRegistry, *, all_commands: bool = False):
    commands = dict()
    max_length = 0
    max_name_length = 0
    infix = '  - alias of '
    infix_len = len(infix)

    for name in command_registry.get_command_names():
        desc = command_registry.get_command_class_descriptor(name)
        command = desc.get_class()
        command_name = desc.get_name()

        if name == command_name:
            cmdname = name
            current_length = len(name)
        else:

            if not all_commands:
                continue
            cmdname = (name, command_name)
            current_length = len(name) + len(command_name) + infix_len

        if len(name) > max_name_length:
            max_name_length = len(name)

        if current_length > max_length:
            max_length = current_length

        commands[name] = (cmdname, command.description)

    format_str = "  {0:<" + str(max_length) + "}   -- {1}"
    alias_format_str = "{0:<" + str(max_name_length) + "}" + infix + "{1}"

    print(f'Available {prog_name.capitalize()} Commands.')
    for name in sorted(commands):
        cmdname, description = commands[name]
        if isinstance(cmdname, tuple):
            cmdname = alias_format_str.format(*cmdname)
        print(format_str.format(cmdname, description))


class ListAllCommand(Command):
    name = 'list-all'
    description = 'Lists all available command with aliases'

    def run(self, args: argparse.Namespace):
        context: Context = args._context_
        _list_comands(args._program_name_, context.command_registry, all_commands=True)


class ListCommand(Command):
    name = 'list'
    description = 'Lists all available command with their names only'

    def run(self, args: argparse.Namespace):
        context: Context = args._context_
        _list_comands(args._program_name_, context.command_registry)


class MainApplication:
    def __init__(self, loader: PluginLoader, program_name: str):
        self.__loader = loader
        self.__program_name = program_name

    def __parse_app_args(self, args: collections.Sequence):
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

        logging = parser.add_argument_group('Logging')
        logging.add_argument('-v', '--log-level', dest='log_level', help='Set log level, default: warning',
                             choices=[i.name.lower() for i in LogLevel], default='info')
        logging.add_argument('--log-syslog', dest='log_syslog', action='store_true',
                             help='Log to syslog. Can be combined with other log targets')
        logging.add_argument('--log-console', '--log-stdout', dest='log_console', action='store_true',
                             help='Log to STDOUT, the console. Can be combined with other targets.'
                                  'If no target is specified, this is used as default.')
        logging.add_argument('--log-file', dest='log_file', action='append',
                             help='Log to a file. Can be specified multiple times and '
                                  'can be combined with other options.')
        logging.add_argument('--no-log', '-l', dest='log_none', action='store_true',
                             help='Disable logging. If this is set, other targets are invalid.')

        parser.add_argument('command', nargs='?', help='Command to be run', default='list')
        parser.add_argument(
            'commandargs', nargs=argparse.REMAINDER, help='Additonal options and arguments of the specified command',
            default=[], )
        return parser.parse_args(args)

    def run(self, args: collections.Sequence):
        app_ns = self.__parse_app_args(args)
        if app_ns.debug:
            app_ns.print_backtraces = True
            app_ns.log_level = 'debug'

        if self._process_logging_options(app_ns):
            sys.exit(1)

        plugins = app_ns.plugin or ['dewi.core.application.DewiPlugin']
        plugins.append('dewi.core.CorePlugin')

        try:
            log_debug('Loading plugins')
            context = self.__loader.load(set(plugins))
            command_name = app_ns.command

            context.commands.register_class(ListAllCommand)
            context.commands.register_class(ListCommand)

            if command_name in context.command_registry:

                command_class = context.command_registry.get_command_class_descriptor(command_name).get_class()
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

                log_debug('Starting command', name=command_name)
                sys.exit(command.run(ns))

            else:
                print(f"ERROR: The command '{command_name}' is not known.\n")
                similar_names = get_similar_names_to(command_name, sorted(context.command_registry.get_command_names()))

                if similar_names:
                    print('Similar names - firstly based on command name length:')
                    for name in similar_names:
                        print('  {:30s}   -- {}'.format(
                            name,
                            context.command_registry.get_command_class_descriptor(name).get_class().description))
                else:
                    print('NO similar command name.')

                    print('Available commands with aliases:')
                    for name in sorted(context.command_registry.get_command_names()):
                        print('  {:30s}   -- {}'.format(
                            name,
                            context.command_registry.get_command_class_descriptor(name).get_class().description))
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

    def _process_logging_options(self, args: argparse.Namespace):
        if args.log_none:
            if args.log_syslog or args.log_file or args.log_console:
                print('ERROR: --log-none cannot be used any other log target,')
                print('ERROR: none of: --log-file, --log-console, --log-syslog')
                return 1
            create_logger(self.__program_name, LoggerType.NONE, args.log_level, filenames=[])
        else:
            logger_types = []
            if args.log_console:
                logger_types.append(LoggerType.CONSOLE)
            if args.log_file:
                logger_types.append(LoggerType.FILE)
            if args.log_syslog:
                logger_types.append(LoggerType.SYSLOG)

            if not logger_types:
                # Using default logger
                logger_types = LoggerType.CONSOLE

            create_logger(self.__program_name, logger_types, args.log_level, filenames=args.log_file)

    def __wait_for_termination_if_needed(self, app_ns):
        if app_ns.wait:
            print("\nPress ENTER to continue")
            input("")
