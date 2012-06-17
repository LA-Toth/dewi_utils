
__all__ = ['get_dir', 'set_dir', 'main_command_registry']
from DWA.Core.CommandRegistry import CommandRegistry
root_dir = '/tmp'

main_command_registry = CommandRegistry()


def get_dir(name):
    if len(name) and name[0] == '/':
        name = name[1:]
    return '{}/{}'.format(root_dir, name)


def set_root_dir(new_root_dir):
    global root_dir
    root_dir = new_root_dir
