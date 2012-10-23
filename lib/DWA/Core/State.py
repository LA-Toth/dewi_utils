from DWA.Config.YamlConfig import YamlConfig

__all__ = ['get_dir', 'set_dir', 'main_command_registry', 'main_config', 'register_command_class']
from DWA.Core.CommandRegistry import CommandRegistry, ClassDescriptorWithConcreteClass

root_dir = '/tmp'

main_command_registry = CommandRegistry()
main_config = YamlConfig()


def get_dir(name):
    if len(name) and name[0] == '/':
        name = name[1:]
    return '{}/{}'.format(root_dir, name)


def set_root_dir(new_root_dir):
    global root_dir
    root_dir = new_root_dir


def register_command_class(name, cls):
    global main_command_registry
    main_command_registry.register_command_class(name, ClassDescriptorWithConcreteClass(cls))


main_config.open(get_dir('/etc/config.yml'))
