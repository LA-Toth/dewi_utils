import collections
from dewi.core.command import Command
from dewi.core.commandregistry import ClassDescriptorWithConcreteClass
from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class SampleCommand(Command):
    name = 'sample'

    def perform(self, args: collections.Iterable):
        return 42


class SamplePlugin(Plugin):
    def load(self, c: Context):
        c['commandregistry'].register_command_class(
            SampleCommand.name,
            ClassDescriptorWithConcreteClass(SampleCommand))

    def get_description(self) -> str:
        return "plugin description"

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}
