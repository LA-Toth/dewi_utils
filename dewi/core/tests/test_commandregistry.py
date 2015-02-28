# Copyright 2012-2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import argparse

from dewi.core.command import Command
from dewi.core.commandregistry import CommandRegistry, CommandRegistryException, ClassDescriptor,\
    ClassDescriptorWithModuleName,\
    ClassDescriptorWithModuleNameAndCommandClassMember,\
    ClassDescriptorWithModuleAndClassName, ClassDescriptorWithConcreteClass,\
    ClassNotFound, ClassIsNotSubclassOfCommand, CommandRegistrar

import dewi.tests

# disabling C0103 pylint error, because it is triggered due to limitation of the test,
# the test tests real-world scenarios within itself...


class Command1:
    name = 'command-1'


class Command2:
    name = 'command-2'


class test_commandregistry:  # pylint: disable=C0103
    name = 'test-command-registry'


command_class = Command2  # pylint: disable=C0103


class CommandRegistryTest(dewi.tests.TestCase):

    def set_up(self):
        self.tested = CommandRegistry()

    def assert_registry_exception_raises(self, *args):
        self.assert_raises(CommandRegistryException, *args)

    def assert_class_not_found(self, *args):
        self.assert_raises(ClassNotFound, *args)

    def test_initialized_as_empty(self):
        self.assert_equal(self.tested.get_command_count(), 0, "Freshly created command registry is non-empty")
        self.assert_registry_exception_raises(self.tested.get_command_class_descriptor, "anything")

    def test_invalid_descriptor_type_cause_exceptions(self):
        self.assert_registry_exception_raises(self.tested.register_command_class, "something", 42)
        self.assert_registry_exception_raises(self.tested.register_command_class, "something", self)

    def test_registered_class_descriptor_can_be_retrieved(self):
        name = "something"
        descriptor = ClassDescriptor()
        self.tested.register_command_class(name, descriptor)

        other_descriptor = self.tested.get_command_class_descriptor(name)
        self.assert_equal(descriptor, other_descriptor)

    def test_registered_name_cannot_be_overriden(self):
        name = "something"
        descriptor = ClassDescriptor()
        self.tested.register_command_class(name, descriptor)

        self.assert_registry_exception_raises(self.tested.get_command_class_descriptor, descriptor)

    def test_command_can_be_registered_with_different_names_and_the_names_can_be_fetched(self):
        descriptor = ClassDescriptor()
        self.tested.register_command_class("first", descriptor)
        self.tested.register_command_class("second", descriptor)

        self.assert_equal(sorted(["first", "second"]), sorted(self.tested.get_command_names()))

    def test_class_descriptors_get_class_is_not_implemented(self):
        descriptor = ClassDescriptor()
        self.assert_raises(NotImplementedError, descriptor.get_class)

    def test_class_descriptors_get_name_is_not_implemented(self):
        descriptor = ClassDescriptor()
        self.assert_raises(NotImplementedError, descriptor.get_name)

    def test_class_descriptor_with_module_name_only_returns_class_with_same_name(self):
        descriptor = ClassDescriptorWithModuleName(__name__)
        self.assert_equal(test_commandregistry, descriptor.get_class())
        self.assert_equal('test-command-registry', descriptor.get_name())

    def test_class_descriptor_with_module_name_and_class_name_returns_expected_class(self):
        descriptor = ClassDescriptorWithModuleAndClassName(__name__, 'Command1')
        self.assert_equal(Command1, descriptor.get_class())
        self.assert_equal('command-1', descriptor.get_name())

    def test_class_descriptor_with_module_name_and_class_name_throws_exception_when_class_not_found(self):
        descriptor = ClassDescriptorWithModuleAndClassName(__name__, 'Command123243')
        self.assert_class_not_found(descriptor.get_class)

    def test_class_descriptor_with_module_name_and_command_class_returns_expected_class(self):
        descriptor = ClassDescriptorWithModuleNameAndCommandClassMember(__name__)
        self.assert_equal(Command2, descriptor.get_class())
        self.assert_equal('command-2', descriptor.get_name())

    def test_class_descriptor_with_module_name_and_command_class_throws_exception_when_class_not_found(self):
        descriptor = ClassDescriptorWithModuleNameAndCommandClassMember('os')
        self.assert_class_not_found(descriptor.get_class)

    def test_class_descriptor_with_concrete_class_returns_expected_class(self):
        class LocalCommand(Command):
            name = 'local-command'

            def run(self, args: argparse.Namespace):
                pass

        descriptor = ClassDescriptorWithConcreteClass(LocalCommand)
        self.assert_equal(LocalCommand, descriptor.get_class())
        self.assert_equal('local-command', descriptor.get_name())

    def test_class_descriptor_with_concrete_class_rejects_non_subclass_of_command(self):
        class LocalCommand:
            pass

        self.assert_raises(ClassIsNotSubclassOfCommand, ClassDescriptorWithConcreteClass, LocalCommand)


class TestCommandRegistrar(dewi.tests.TestCase):

    def set_up(self):
        self.__registry = CommandRegistry()
        self.__registrar = CommandRegistrar(self.__registry)

    def test_registration_of_a_simple_command(self):
        class LocalCommand(Command):
            name = 'local-command'

            def run(self, args: argparse.Namespace):
                pass

        self.__registrar.register_class(LocalCommand)
        self.assert_equal(1, self.__registry.get_command_count())
        self.assert_equal(['local-command'], self.__registry.get_command_names())
        self.assert_equal(LocalCommand, self.__registry.get_command_class_descriptor('local-command').get_class())

    def test_registration_of_a_command_with_aliases(self):
        class LocalCommand(Command):
            name = 'local-command'
            aliases = ['lc', 'a', 'b42']

            def run(self, args: argparse.Namespace):
                pass

        self.__registrar.register_class(LocalCommand)
        self.assert_equal(4, self.__registry.get_command_count())
        self.assert_equal({'local-command', 'a', 'b42', 'lc'}, set(self.__registry.get_command_names()))
        self.assert_equal(LocalCommand, self.__registry.get_command_class_descriptor('local-command').get_class())
        self.assert_equal(LocalCommand, self.__registry.get_command_class_descriptor('b42').get_class())

    def test_registration_fails_if_not_a_command_is_registered(self):
        self.assert_raises(ClassIsNotSubclassOfCommand, self.__registrar.register_class, CommandRegistry)
