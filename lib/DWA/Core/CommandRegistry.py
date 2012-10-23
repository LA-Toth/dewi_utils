from DWA.Core.Exceptions import DWAException

import sys


class CommandRegistryException(DWAException):
    pass


class ClassNotFoundException(CommandRegistryException):
    pass


class ClassDescriptor(object):
    """Describes how to create a class based on specific values in subclasses.

        There is also a method that lets the class to be get - without instantiation of it.
    """

    def get_class(self):
        raise NotImplementedError()


class ClassDescriptorWithModuleAndClassName(ClassDescriptor):
    def __init__(self, module_name, class_name):
        super().__init__()
        self._module_name = module_name
        self._class_name = class_name

    def get_class(self):
        module = self.__get_module_object()
        try:
            return getattr(module, self._class_name)
        except AttributeError:
            raise ClassNotFoundException("Invalid class or attribute: {}".format(self._class_name))

    def __get_module_object(self):
        __import__(self._module_name)
        return sys.modules[self._module_name]


class ClassDescriptorWithModuleName(ClassDescriptorWithModuleAndClassName):
    """The module and the class has the same name (the module's last part at least)"""

    def __init__(self, module_name):
        super().__init__(module_name, module_name.split('.')[-1])


class ClassDescriptorWithModuleNameAndCmdclassMember(ClassDescriptorWithModuleAndClassName):
    def __init__(self, module_name):
        super().__init__(module_name, 'cmdclass')


class ClassDescriptorWithConcreteClass(ClassDescriptor):
    def __init__(self, class_object):
        super().__init__()
        self.class_object = class_object

    def get_class(self):
        return self.class_object


class CommandRegistry(object):
    '''
    Registry of command classes
    '''

    def __init__(self):
        self.__registry = dict()

    def __validate_name_and_class_descriptor(self, name, class_descriptor):
        if name in self.__registry:
            raise CommandRegistryException("Command class name is already used; name='{}'".format(name))
        if not isinstance(class_descriptor, ClassDescriptor):
            raise CommandRegistryException("Command class descriptor's type differs crom ClassDescriptor; "
                "type='{}'".format(type(class_descriptor).__name__))

    def register_command_class(self, name, class_descriptor):
        self.__validate_name_and_class_descriptor(name, class_descriptor)
        self.__registry[name] = class_descriptor

    def get_command_class_descriptor(self, name):
        if name not in self.__registry:
            raise CommandRegistryException("Specified command class name is not found; name='{}'".format(name))
        return self.__registry[name]

    def get_command_count(self):
        return len(self.__registry)

    def get_command_names(self):
        return list(self.__registry.keys())
