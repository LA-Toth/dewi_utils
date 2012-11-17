from MyPlugin1.Helpers import get_hello_string
from DWA.Core.Command import Command


class HelloCommand(Command):
    def _perform_command(self):
        print(get_hello_string())
