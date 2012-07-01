import DWA.Core.Exceptions as Exceptions
from DWA.Core.State import main_command_registry
from DWA.Core.Aliases import Aliases
from DWA.Core.CommandRegistry import CommandRegistryException
from DWA.Utils.Algorithm import get_similar_names_to

class FrontController(object):
    def __init__(self, command_registry=None, aliases=None):
        if not command_registry:
            command_registry = main_command_registry
        if not aliases:
            aliases = Aliases()
        self.__command_registry = command_registry
        self.__aliases = aliases

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

    def _process_aliases(self, args):
        alias = self.__aliases.get_alias(args[0])
        if alias:
            if alias[0] == '!':
                # shell command
                #cmd = args[1:]
                #cmd[0:0] = [ newcmd[1:] ]
                #Utils.run_command(string.join(cmd))
                return (True, 1)
            args[0:1] = alias.split(' ')
        return (False, args)

    def process_args(self, args):
        cmd = args[0]
        finished, args = self._process_aliases(args)
        if finished:
            return args

        try:
            return (True, self._create_and_perform(args))
        except CommandRegistryException:
            command_list = self.__command_registry.get_command_names()
            command_list.extend(self.__aliases.get_alias_names())
            return (False, get_similar_names_to(cmd, command_list))
