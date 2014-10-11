from DWA.Config.YamlConfig import YamlConfig
from DWA.Core.PluginRegistry import PluginRegistry

from .Dirs import get_dir
from DWA.Core.CommandRegistry import CommandRegistry, ClassDescriptorWithConcreteClass

__all__ = ['main_command_registry', 'main_config', 'register_command_class']


main_command_registry = CommandRegistry()
main_config = YamlConfig()
plugin_registry = None


def initialize():
    global plugin_registry
    plugin_registry = PluginRegistry(get_dir('etc'), main_command_registry)


def register_command_class(name, cls):
    global main_command_registry
    main_command_registry.register_command_class(name, ClassDescriptorWithConcreteClass(cls))


main_config.open(get_dir('/etc/config.yml'))
