import collections
import sys
from dewi.core.command import Command


class CommandRegistryException(Exception):
    pass


class ClassNotFoundException(CommandRegistryException):
    pass


class ClassDescriptor(object):
    """
    Describes how to create a class based on specific values in subclasses.

    There is also a method that lets the class to be get - without instantiation of it.
    """

    def get_class(self):
        raise NotImplementedError()

    def get_name(self):
        raise NotImplementedError()


class ClassDescriptorWithModuleAndClassName(ClassDescriptor):
    """
    Both the module name and the command class name are specified
    """
    def __init__(self, module_name: str, class_name: str):
        super().__init__()
        self._module_name = module_name
        self._class_name = class_name

    def get_class(self) -> Command:
        module = self._get_module_object()
        try:
            return getattr(module, self._class_name)
        except AttributeError:
            raise ClassNotFoundException("Invalid class or attribute: {0}".format(self._class_name))

    def _get_module_object(self):
        __import__(self._module_name)
        return sys.modules[self._module_name]

    def get_name(self) -> str:
        return self.get_class().name


class ClassDescriptorWithModuleName(ClassDescriptorWithModuleAndClassName):
    """The module and the class has the same name (the module's last part at least)"""

    def __init__(self, module_name: str):
        super().__init__(module_name, module_name.split('.')[-1])

    def get_name(self) -> str:
        return self.get_class().name


class ClassDescriptorWithModuleNameAndCmdclassMember(ClassDescriptorWithModuleAndClassName):
    """
    The command is in a module that have specific layout, its __init__.py has commandlcass member. This member
    stores the command class.
    """
    def __init__(self, module_name: str):
        super().__init__(module_name, 'command_class')

    def get_name(self) -> str:
        return self._get_module_object().name


class ClassDescriptorWithConcreteClass(ClassDescriptor):
    """
    This descriptor stores the class itself, mainly used for testing.
    """
    def __init__(self, class_object: Command):
        super().__init__()
        self.class_object = class_object

    def get_class(self) -> Command:
        return self.class_object

    def get_name(self) -> str:
        return self.class_object.name


class CommandRegistry(object):
    '''
    Registry of command classes
    '''

    def __init__(self):
        self.__registry = dict()

    def __validate_name_and_class_descriptor(self, name: str, class_descriptor: ClassDescriptor):
        if name in self.__registry:
            raise CommandRegistryException("Command class name is already used; name='{0}'".format(name))
        if not isinstance(class_descriptor, ClassDescriptor):
            raise CommandRegistryException(
                "Command class descriptor's type differs from ClassDescriptor; "
                "type='{0}'".format(type(class_descriptor).__name__))

    def register_command_class(self, name: str, class_descriptor: ClassDescriptor):
        self.__validate_name_and_class_descriptor(name, class_descriptor)
        self.__registry[name] = class_descriptor

    def get_command_class_descriptor(self, name: str) -> ClassDescriptor:
        if name not in self.__registry:
            raise CommandRegistryException("Specified command class name is not found; name='{0}'".format(name))
        return self.__registry[name]

    def get_command_count(self) -> int:
        return len(self.__registry)

    def get_command_names(self) -> collections.Sequence:
        return list(self.__registry.keys())
