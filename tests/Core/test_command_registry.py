import unittest

from DWA.Core.CommandRegistry import CommandRegistry, CommandRegistryException, ClassDescriptor,\
    ClassDescriptorWithModuleName,\
    ClassDescriptorWithModuleNameAndCmdclassMember,\
    ClassDescriptorWithModuleAndClassName, ClassDescriptorWithConcreteClass,\
    ClassNotFoundException

class Command1:
    pass


class Command2:
    pass


class test_command_registry:
    pass


cmdclass = Command2


class CommandRegistryTest(unittest.TestCase):

    def setUp(self):
        self.tested = CommandRegistry()

    def assertRegistryExceptionRaises(self, *args):
        self.assertRaises(CommandRegistryException, *args)

    def assertClassNotFound(self, *args):
        self.assertRaises(ClassNotFoundException, *args)

    def test_initialized_as_empty(self):
        self.assertEqual(self.tested.get_command_count(), 0, "Freshly created command registry is non-empty")
        self.assertRegistryExceptionRaises(self.tested.get_command_class_descriptor, "anything")

    def test_invalid_descriptor_type_cause_exceptions(self):
        self.assertRegistryExceptionRaises(self.tested.register_command_class, "something", 42)
        self.assertRegistryExceptionRaises(self.tested.register_command_class, "something", self)

    def test_registered_class_descriptor_can_be_retrieved(self):
        NAME = "something"
        descriptor = ClassDescriptor()
        self.tested.register_command_class(NAME, descriptor)

        other_descriptor = self.tested.get_command_class_descriptor(NAME)
        self.assertEqual(descriptor, other_descriptor)

    def test_registered_name_cannot_be_overriden(self):
        NAME = "something"
        descriptor = ClassDescriptor()
        self.tested.register_command_class(NAME, descriptor)

        self.assertRegistryExceptionRaises(self.tested.get_command_class_descriptor, descriptor)

    def test_command_can_be_registered_with_different_names_and_the_names_can_be_fetched(self):
        descriptor = ClassDescriptor()
        self.tested.register_command_class("first", descriptor)
        self.tested.register_command_class("second", descriptor)

        self.assertEqual(sorted(["first", "second"]), sorted(self.tested.get_command_names()))

    def test_class_descriptors_get_class_is_not_implemented(self):
        descriptor = ClassDescriptor()
        self.assertRaises(NotImplementedError, descriptor.get_class)

    def test_class_descriptor_with_module_name_only_returns_class_with_same_name(self):
        descriptor = ClassDescriptorWithModuleName(__name__)
        self.assertEqual(test_command_registry, descriptor.get_class())

    def test_class_descriptor_with_module_name_and_class_name_returns_expected_class(self):
        descriptor = ClassDescriptorWithModuleAndClassName(__name__, 'Command1')
        self.assertEqual(Command1, descriptor.get_class())

    def test_class_descriptor_with_module_name_and_class_name_throws_exception_when_class_not_found(self):
        descriptor = ClassDescriptorWithModuleAndClassName(__name__, 'Command123243')
        self.assertClassNotFound(descriptor.get_class)

    def test_class_descriptor_with_module_name_and_cmdclass_returns_expected_class(self):
        descriptor = ClassDescriptorWithModuleNameAndCmdclassMember(__name__)
        self.assertEqual(Command2, descriptor.get_class())

    def test_class_descriptor_with_module_name_and_cmd_class_throws_exception_when_class_not_found(self):
        descriptor = ClassDescriptorWithModuleNameAndCmdclassMember('os')
        self.assertClassNotFound(descriptor.get_class)

    def test_class_descriptor_with_concrete_class_returns_expected_class(self):
        class LocalCommand(object):
            pass

        descriptor = ClassDescriptorWithConcreteClass(LocalCommand)
        self.assertEqual(LocalCommand, descriptor.get_class())
