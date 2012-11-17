import os

from DWA.Config.YamlConfig import YamlConfig
from DWA.Core.Exceptions import DWAException
from DWA.Core import Dirs
from DWA.Core.CommandRegistry import ClassDescriptorWithModuleAndClassName
import sys


class Plugin(object):
    """Stores information of a plugin and adds wrapper functions for the plugin registry
    For more details please visit <DWA>/doc/plugins.txt
    """

    TYPE_MODULE_AND_CLASS_HAS_SAME_NAME = 0
    TYPE_MODULE_NAME_WITH_COMMAND_SUFFIX_IS_THE_COMMAND_CLASS_NAME = 1
    TYPE_SEPARATED_MODULES = 2

    def __init__(self, plugin_registry, name, location, basepath):
        self.__registry = plugin_registry
        self.__name = name
        self.__location = location
        self.__basepath = basepath

    def get_name(self):
        return self.__name

    def get_location(self):
        return self.__location

    def get_basepath(self):
        return self.__basepath

    def register_command_class(self, name, cls):
        self.__registry._register_command_class(self, name, cls)

    def register_command_module(self, name, module_name):
        self.__registry._register_command_module(self, name, module_name)

    def register_command_with_module_and_cmdclass_attribute(self, name, module_name):
        self.__registry._register_command_with_module_and_cmdclass_attribute(self, name, module_name)

    def register_command_with_module_and_class_name(self, name, module_name, class_name):
        self.__registry._register_command_with_module_and_class_name(self, name, module_name, class_name)

    def register_commands(self, name, command_type):
        self.__registry._register_commands(self, name, command_type)


class PluginRegistry(object):
    def __init__(self, config_directory, command_registry):
        self.__config_directory = config_directory
        self.__plugins_py_file_name = self.__config_directory + '/plugins.py'
        self.__activated_plugin_directory = self.__config_directory + '/plugins/activated'
        self.__command_registry = command_registry

        self.__plugins = {}

    def register(self, name, location, basepath):
        """
        @name: the plugin's name in the registry
        @location: full path to a directory that contains the plugin
        @basepath: the relative path of the python source directory within the plugin.
                   It's usually 'lib'.
        """
        plugin = Plugin(self, name, location, basepath)
        self.__plugins[name] = plugin

    def get_plugin(self, name):
        try:
            return self.__plugins[name]
        except KeyError:
            return None

    def count(self):
        return len(self.__plugins)

    def load_plugins(self):
        self.__initialize_core_plugin()
        plugin_names = self.__get_plugin_name_list()
        self.__load_plugins(plugin_names)

    def __initialize_core_plugin(self):
        self.register('core', Dirs.get_root_dir(), 'lib/')
        plugin = self.get_plugin('core')
        basedir = Dirs.get_dir('lib/DWA/Commands')
        self.__load_commands_with_module_and_class_name(plugin, basedir, 'DWA.Commands')

    def __load_commands_with_module_and_class_name(self, plugin, directory, base_module_name):
        listing = []
        try:
            listing = os.listdir(directory)
        except OSError:
            print("Plugin directory listing failure; directory='{}'".format(directory))
        for file in listing:
            if file != '__init__.py' and os.path.isfile(directory + '/' + file) and file[-3:] == '.py':
                command_name = file[:-3]
                plugin.register_command_with_module_and_class_name(command_name.lower(),
                                                                   base_module_name + '.' + command_name,
                                                                   command_name + 'Command')

    def __get_plugin_name_list(self):
        listing = os.listdir(self.__activated_plugin_directory)
        result = list()
        for file in listing:
            if file[-4:] == '.yml' and os.path.isfile(self.__activated_plugin_directory + '/' + file):
                if file not in ['base.yml', 'core.yml']:
                    result.append(file[:-4])
        return result

    def __load_plugins(self, plugin_names):
        for name in plugin_names:
            config = YamlConfig()
            filename = self.__activated_plugin_directory + '/' + name + '.yml'
            config.open(filename)
            directory = os.path.normpath(os.path.dirname(os.path.realpath(os.path.abspath(filename))) + "/..")
            stored_name = config.get('name')
            if stored_name != name:
                raise DWAException("Plugin configuration is invalid, name mismatch; stored_name='{}', file_name='{}.yml'".format(stored_name, name))

            self.__load_plugin_based_on_config(config, directory)

    def __load_plugin_based_on_config(self, config, directory):
        name = config.get('name')
        basepath = config.get('source.basedirectory')
        self.register(name, directory, basepath)
        plugin = self.get_plugin(name)
        libdir = config.get('source.basedirectory')
        command_module_type = config.get('source.commandmodule.type')
        command_module_name = config.get('source.commandmodule.name')

        sys.path.append(directory + '/' + libdir)

        if command_module_type == 'TYPE_MODULE_NAME_WITH_COMMAND_SUFFIX_IS_THE_COMMAND_CLASS_NAME':
            self.__load_commands_with_module_and_class_name(plugin,
                                                            '{plugindir}/{libdir}/{modulename}'.format(plugindir=directory,
                                                                                                       libdir=libdir,
                                                                                                       modulename=command_module_name.replace('.', '/')),
                                                            command_module_name)
        else:
            raise DWAException("This command type is not yet supported; type='{}'".format(command_module_type))

    def _register_command_with_module_and_class_name(self, plugin, name, module_name, class_name):
        descriptor = ClassDescriptorWithModuleAndClassName(module_name, class_name)
        self.__command_registry.register_command_class(name, descriptor)
