import unittest
from DWA.Core.CommandRegistry import CommandRegistry, CommandRegistryException

class Test(unittest.TestCase):

    def setUp(self):
        self.tested = CommandRegistry()

    def test_initialized_as_empty(self):
        self.assertEqual(self.tested.get_command_count(), 0, "Freshly created command registry is non-empty")
        self.assertRaises(CommandRegistryException, self.tested.get_command_class, "anything")

    def testCommandClassCanBeAddedAndAndRetreived(self):
        class Cls(object):
            pass

        self.tested.register_command_class("foo", Cls)
        self.assertEqual(self.tested.get_command_class("foo"), Cls, "Registered class cannot be retrieved")

    def testCommandClassCanBeRegisteredMultipleTimesIfNameDiffers(self):
        class Cls(object):
            pass

        self.tested.register_command_class("foo", Cls)
        self.tested.register_command_class("bar", Cls)
        self.assertEqual(self.tested.get_command_class("foo"), Cls, "Registered class cannot be retrieved")
        self.assertEqual(self.tested.get_command_class("bar"), Cls, "Second Registered class cannot be retrieved")

    def testRegisteredClassNamesCanBeFetched(self):
        self.tested.register_command_class("foo", object)
        self.tested.register_command_class("bar", object)
        self.assertEqual(sorted(self.tested.get_command_names()), sorted(['foo', 'bar']), "Command names differ")

    def testOneNameCannotBeReRegistered(self):
        class Cls(object):
            pass

        class Cls2(object):
            pass

        self.tested.register_command_class("foo", Cls)
        self.assertRaises(CommandRegistryException, self.tested.register_command_class, "foo", Cls2)
        self.assertEqual(self.tested.get_command_class("foo"), Cls, "Registered class cannot be retrieved")
