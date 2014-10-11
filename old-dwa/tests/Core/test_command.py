import unittest

from DWA.Core.Command import Command
from DWA.Utils.ErrorRaisingArgumentParser import ErrorRaisingArgumentParser,\
    ArgumentParserError


class TestCommand(unittest.TestCase):
    def test_constructor(self):
        command = Command(argument_parser_class=ErrorRaisingArgumentParser)
        self.assertEquals('Basic command, base class', command.description)
        self.assertTrue(hasattr(command, 'parser'))
        self.assertEqual(command.get_name(), "unknown", "Base class's name was not properly deduced")

    def test_help(self):
        command = Command(argument_parser_class=ErrorRaisingArgumentParser)
        try:
            command.perform(['-h'])
            self.fail("Help screen was not shown")
        except ArgumentParserError as e:
            self.assertEqual(e.error_code, 0, "Printing help should be meant successful run: exit status zero")

    def test_manpage(self):
        called = False

        class ManCommand(Command):
            def _print_manpage(self):
                nonlocal called
                called = True

        command = ManCommand(argument_parser_class=ErrorRaisingArgumentParser)
        try:
            command.perform(['--help'])
            self.fail("Man page was not shown")
        except ArgumentParserError as e:
            self.assertEqual(e.error_code, 0, "Showing man page must mean successfully run program")

        self.assertTrue(called, "Man page should be 'printed'")

    def test_subclass_name_processed_properly(self):
        class MyCommand(Command):
            pass

        class LongerNameWithMoreStringAndThenTheStringCommand(Command):
            pass

        self.assertEqual(MyCommand.get_name(), "my")
        self.assertEqual(LongerNameWithMoreStringAndThenTheStringCommand.get_name(), "longernamewithmorestringandthenthestring")

    def test_perform_method_is_not_implemented(self):
        command = Command()
        self.assertRaises(NotImplementedError, command.perform, [])

    def test_overriden_perform_command_not_raises_NotImplementedError(self):
        class MyCommand(Command):
            def _perform_command(self):
                pass
        command = MyCommand()
        command.perform([])
        self.assertTrue(True)

    def test_overriden_perform_command_is_called_and_return_value_is_accessible(self):
        _called = False

        class MyCommand(Command):
            def _perform_command(self):
                nonlocal _called
                _called = True
                return 3.1415
        command = MyCommand()
        self.assertEquals(command.perform([]), 3.1415)
        self.assertTrue(_called)

    def test_perform_rejects_extra_arguments(self):
        command = Command(argument_parser_class=ErrorRaisingArgumentParser)
        try:
            command.perform(['-x', 'foo'])
            self.fail("Perform() finished without exception")
        except ArgumentParserError as e:
            self.assertEqual(e.error_code, 2)
