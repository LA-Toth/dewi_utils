from DWA.Core.Exceptions import DWAException

class CommandRegistryException(DWAException):
    pass

class CommandRegistry(object):
    '''
    Registry of command classes
    '''

    def __init__(self):
        self.__registry = dict()

    def register_command_class(self, name, cls):
        if name in self.__registry:
            raise CommandRegistryException("Command class name is already used; name='{}'".format(name))
        self.__registry[name] = cls

    def get_command_class(self, name):
        if name not in self.__registry:
            raise CommandRegistryException("Specified command class name is not found; name='{}'".format(name))
        return self.__registry[name]

    def get_command_count(self):
        return len(self.__registry)
