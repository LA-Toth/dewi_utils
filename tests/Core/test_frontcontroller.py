import unittest

from DWA.Core.FrontController import FrontController
from DWA.Core.Exceptions import DWAException
from DWA.Core.CommandRegistry import CommandRegistry
from DWA.Config.YamlConfig import YamlConfig
from DWA.Core.Aliases import Aliases

class BasicCommand(object):
    def __init__(self):
        self.args = None
        self.called = False
        self.called_as = None

    def perform(self, args):
        self.called = True
        self.args = args
        self.called_as = self.__class__.__name__


class Command1(BasicCommand):
    pass


class Command2(BasicCommand):
    pass


class TestFrontControllerBasics(unittest.TestCase):
    def setUp(self):
        self.command_registry = CommandRegistry()
        self.tested = FrontController(self.command_registry)

    def testGetCommandNameReturnsFirstMemberOList(self):
        self.assertEquals(self.tested._get_command_name(['foo']), 'foo' )
        self.assertEquals(self.tested._get_command_name(['foo', 'bar']), 'foo' )

    def testGetCommandNameFailsOnNonEmptyArray(self):
        self.assertRaises(DWAException, self.tested._get_command_name, [])


class TestFrontCollerWithoutAliases(unittest.TestCase):
    def setUp(self):
        self.command_registry = CommandRegistry()
        self.main_config = YamlConfig()
        self.aliases = Aliases(self.main_config)
        self.tested = FrontController(self.command_registry, self.aliases)
        self.command_registry.register_command_class("cmd1", Command1)
        self.command_registry.register_command_class("cmd2", Command2)
        self.command_registry.register_command_class("alias1", Command1)
        self.command_registry.register_command_class("basic", BasicCommand)
        self.command_registry.register_command_class("testcl", BasicCommand)

    def testCreatedObjectsAreFromExpectedClass(self):
        self.assertIsInstance(self.tested._create_command(['cmd1']), Command1, "Created command object's class differs from expected")
        self.assertIsInstance(self.tested._create_command(['alias1']), Command1, "Created command object's class differs from expected")
        self.assertIsInstance(self.tested._create_command(['cmd2']), Command2, "Created command object's class differs from expected")
        self.assertIsInstance(self.tested._create_command(['basic']), BasicCommand, "Created command object's class differs from expected")

    def testSimilarNamesAreTheExpected(self):
        self.assertSequenceEqual((False, ['testcl']), self.tested.process_args(['testclt']))

    def testCreateAndPerformPassesArgsProperly(self):
        done = False
        class TestCommand(BasicCommand):
            tester = self

            def perform(self, args):
                super().perform(args)
                self.tester.assertEquals(self.called_as, "TestCommand")
                self.tester.assertSequenceEqual(self.args, ["p1", "p2", "foo"])
                nonlocal done
                done = True
                return [done, args[0]]

        self.command_registry.register_command_class("testcls", TestCommand)
        self.assertSequenceEqual(self.tested._create_and_perform(["testcls", "p1", "p2", "foo"]), [True, 'p1'], "Bad return value", list)
        self.assertEqual(done, True, "TestCommand's perform method is not called")
        done = False
        self.assertSequenceEqual(self.tested.process_args(["testcls", "p1", "p2", "foo"]), [True, [True, 'p1']], "Bad return value")
        self.assertEqual(done, True, "TestCommand's perform method is not called")


class TestFrontCollerWithAliases(unittest.TestCase):
    def setUp(self):
        self.command_registry = CommandRegistry()
        self.main_config = YamlConfig()
        self.alias_config = { 'apple' : 'testcls p1', 'shellfunc' : '!command with args'}
        self.main_config.set_config({ 'dwa' :  { 'alias' :  self.alias_config }})
        self.aliases = Aliases(self.main_config)
        self.tested = FrontController(self.command_registry, self.aliases)
        self.command_registry.register_command_class("cmd1", Command1)
        self.command_registry.register_command_class("cmd2", Command2)
        self.command_registry.register_command_class("alias1", Command1)
        self.command_registry.register_command_class("basic", BasicCommand)

    def testSimilarNamesAreExpected(self):
        self.assertSequenceEqual((False, ['alias1', 'shellfunc']), self.tested.process_args(['testclt']))

    def testSimilarNamesWithLocalRegistrationAreTheExpected(self):
        self.command_registry.register_command_class("testcl", BasicCommand)
        self.command_registry.register_command_class("testcls", BasicCommand)
        self.assertSequenceEqual((False, ['testcls']), self.tested.process_args(['testclt']))

    def testAliasOfCommand(self):
        done = False
        class TestCommand(BasicCommand):
            tester = self

            def perform(self, args):
                super().perform(args)
                self.tester.assertEquals(self.called_as, "TestCommand")
                self.tester.assertSequenceEqual(self.args, ["p1", "p2", "foo"])
                nonlocal done
                done = True
                return [done, args[0]]

        self.command_registry.register_command_class("testcls", TestCommand)
        self.assertSequenceEqual(self.tested.process_args(['apple', 'p2', 'foo']), [True, [True, 'p1']], 'Bad return value')
        self.assertEqual(done, True, "TestCommand's perform method is not called")

    def testShellAlias(self):
        self.assertEqual(self.tested.process_args(['shellfunc']), 1, 'Bad return value of shell alias')
