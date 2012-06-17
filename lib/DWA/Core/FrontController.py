import DWA.Core.Exceptions as Exceptions
from DWA.Core.State import main_command_registry

class FrontController(object):
    def __init__(self, command_registry=None):
        if not command_registry:
            command_registry = main_command_registry
        self.__command_registry = command_registry


    def _get_command_name(self, args):
        if len(args) == 0:
            raise Exceptions.DWAException()
        return args[0]

    def _create_command(self, args):
        name = self._get_command_name(args)
        command_class = self.__command_registry.get_command_class(name)
        return command_class()

    def _create_and_perform(self, args):
        command = self._create_command(args)
        return command.perform(args[1:])


    process_args = _create_and_perform

