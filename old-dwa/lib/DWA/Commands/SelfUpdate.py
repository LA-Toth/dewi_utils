from DWA.Core.Command import Command
from DWA.Core.State import plugin_registry
from DWA.Core.CommandRegistry import CommandRegistryException


class SelfUpdateCommand(Command):
    aliases = ['su']

    def __init__(self):
        super().__init__()

        self.parser.add_argument('-p', '--plugins', dest='plugins', action='store_true', help='Update plugin list, available commands')

    def _perform_command(self):
        try:
            return self.__load_plugins()
        except CommandRegistryException as e:
            print("selfupdate: error: " + str(e))
            return 1

    def __load_plugins(self):
        plugin_registry.load_plugins()
