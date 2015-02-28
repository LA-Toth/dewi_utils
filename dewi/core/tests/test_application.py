# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import argparse

import dewi.tests

from dewi.core.application import MainApplication
from dewi.core.command import Command
from dewi.core.commandregistry import CommandRegistry, CommandRegistrar
from dewi.core.context import Context
from dewi.loader.loader import PluginLoader
from dewi.tests import redirect_outputs


class FakeCommand(Command):
    name = 'fake'
    description = 'A fake command for tests'
    arguments = None

    def __init__(self):
        FakeCommand.arguments = None

    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('arguments', nargs='*')

    def run(self, args: argparse.Namespace) -> int:
        arguments = args.arguments

        if arguments and arguments[0] == 'ERROR':
            raise RuntimeError("Fake Command Error")

        FakeCommand.arguments = list(arguments)
        return 42


class FakePluginLoader(PluginLoader):
    def __init__(self, command):
        # super() is not wanted to call here, its interface is overridden
        self.loaded = []
        self.command = command

    def load(self, plugins):
        context = Context()

        self.loaded.extend(plugins)

        context.register('commandregistry', CommandRegistry())
        context.register('commands', CommandRegistrar(context['commandregistry']))
        context['commands'].register_class(self.command)

        return context


class TestMainApplication(dewi.tests.TestCase):

    def set_up(self):
        self.command = FakeCommand()
        self.loader = FakePluginLoader(FakeCommand)
        self.application = MainApplication(self.loader, 'myprogram')

    def __invoke_application(self, args, *, expected_exit_value=1):
        with self.assert_raises(SystemExit) as context:
            self.application.run(args)

        self.assert_equal(expected_exit_value, context.exception.code)

    def __invoke_application_redirected(self, *args, **kwargs):
        with redirect_outputs() as redirection:
            self.__invoke_application(*args, **kwargs)

        return redirection

    def test_help_option(self):
        redirect = self.__invoke_application_redirected(['-h'], expected_exit_value=0)
        self.assert_in('myprogram [options] [command [command-args]]', redirect.stdout.getvalue())
        self.assert_equal('', redirect.stderr.getvalue())

        self.assert_equal(set(), set(self.loader.loaded))

    def test_loading_plugins_requires_a_command_to_run(self):
        redirect = self.__invoke_application_redirected(['-p', 'test'], expected_exit_value=2)
        self.assert_equal('', redirect.stdout.getvalue())
        self.assert_in('myprogram: error: the following arguments are required: command', redirect.stderr.getvalue())

        self.assert_equal(set(), set(self.loader.loaded))

    def test_command_run_method_is_called(self):
        redirect = self.__invoke_application_redirected(
            ['-p', 'test', 'fake', 'something', 'another'],
            expected_exit_value=42)
        self.assert_equal('', redirect.stdout.getvalue())
        self.assert_equal('', redirect.stderr.getvalue())
        self.assert_equal(['something', 'another'], FakeCommand.arguments)
        self.assert_equal({'dewi.core.commandregistry.CommandRegistryPlugin', 'test'}, set(self.loader.loaded))

    def test_command_run_method_exception_is_handled(self):
        redirect = self.__invoke_application_redirected(
            ['-p', 'test', 'fake', 'ERROR'],
            expected_exit_value=1)
        self.assert_equal('', redirect.stdout.getvalue())
        self.assert_in('Fake Command Error', redirect.stderr.getvalue())

    def test_unknown_command(self):
        redirect = self.__invoke_application_redirected(
            ['-p', 'test', 'unknown-name'],
            expected_exit_value=1)
        self.assert_equal('', redirect.stdout.getvalue())
        self.assert_in("Specified command class name is not found; name='unknown-name'", redirect.stderr.getvalue())

    def test_run_help_of_command(self):
        redirect = self.__invoke_application_redirected(
            ['-p', 'test', 'fake', '-h'],
            expected_exit_value=0)
        self.assert_in('myprogram fake [-h]', redirect.stdout.getvalue())
        self.assert_equal('', redirect.stderr.getvalue())
        self.assert_equal({'dewi.core.commandregistry.CommandRegistryPlugin', 'test'}, set(self.loader.loaded))
