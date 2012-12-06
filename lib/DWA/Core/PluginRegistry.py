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


class CommandListGenerator(object):

    def __init__(self, command_list):
        self.command_list = command_list
        self.main_name_to_command_map = {}
        self.aliases_to_command_map = {}

    def generate(self):
        self.__preprocess_lists_and_check_unicity()
        self._update()

    def __preprocess_lists_and_check_unicity(self):
        for cmd in self.command_list:
            if cmd['name'] in self.main_name_to_command_map:
                raise DWAException("Cannot register two commands with the same name; command='{command}', "
                                   "original_plugin='{original}', current_plugin='{current}'".format(
                                                        command=cmd['name'],
                                                        original=self.main_name_to_command_map[cmd['name']]['plugin_name'],
                                                        current=cmd['plugin_name']))
            self.main_name_to_command_map[cmd['name']] = cmd

            for alias in cmd['aliases']:
                if alias in self.aliases_to_command_map:
                    orig = self.aliases_to_command_map[alias]
                    print("Warning, already registered alias, it is ignored; alias='{alias}', original='{orig_cmd} in {orig_plugin}', "
                          "current='{current_cmd} in {current_plugin}'".format(alias=alias, orig_cmd=orig['name'], orig_plugin=orig['plugin_name'],
                                                                               current_cmd=cmd['name'], current_plugin=cmd['plugin_name']))
                else:
                    self.aliases_to_command_map[alias] = cmd

        for (alias, cmd) in self.aliases_to_command_map.items():
            if alias in self.main_name_to_command_map:
                orig = self.main_name_to_command_map[alias]
                print("Warning, alias conflicts with a registered command name, it is ignored; alias='{alias}', original='{orig_cmd} in {orig_plugin}', "
                      "current='{current_cmd} in {current_plugin}'".format(alias=alias, orig_cmd=orig['name'], orig_plugin=orig['plugin_name'],
                                                                            current_cmd=cmd['name'], current_plugin=cmd['plugin_name']))

    def _update(self):
        raise NotImplementedError()


class CommandListFileGenerator(CommandListGenerator):
    def __init__(self, filename, command_list, path):
        super().__init__(command_list)
        self.filename = filename
        self.path = path

    def _update(self):
        with open(self.filename, 'w') as f:
            self.__write_to_opened_file(f)

    def __write_to_opened_file(self, f):
        prefix = ' ' * 4
        print("from DWA.Core.State import main_command_registry", file=f)
        print("from DWA.Core.CommandRegistry import ClassDescriptorWithModuleAndClassName", file=f)
        print("import sys", file=f)
        print("", file=f)
        print("", file=f)
        print("def load_commands():", file=f)
        print(prefix + "sys.path.extend({})".format(self.path), file=f)

        for name in self.main_name_to_command_map:
            cmd = self.main_name_to_command_map[name]
            print(prefix + "descriptor = ClassDescriptorWithModuleAndClassName('{}', '{}')".format(cmd['module_name'], cmd['class_name']), file=f)
            print(prefix + "main_command_registry.register_command_class('{}', descriptor)".format(name), file=f)
        for alias in self.aliases_to_command_map:
            cmd = self.aliases_to_command_map[alias]
            print(prefix + "descriptor = ClassDescriptorWithModuleAndClassName('{}', '{}')".format(cmd['module_name'], cmd['class_name']), file=f)
            print(prefix + "main_command_registry.register_command_class('{}', descriptor)".format(alias), file=f)


class ToolsCommandUpdater(CommandListGenerator):
    def __init__(self, filename, command_list, target_directory):
        super().__init__(command_list)
        self.filename = filename
        self.target_directory = target_directory

    def _update(self):
        with open(self.filename, 'w') as f:
            self.__file = f
            self.__write_to_opened_file()
        self.__update_symlinks()

    def __write_to_opened_file(self):
        print("commands = {", file=self.__file)
        for name in self.main_name_to_command_map:
            self.__write_main_command_descriptor(name)
        for alias in self.aliases_to_command_map:
            self.__write_alias_command_descriptor(alias)
        print("}", file=self.__file)

    def __write_main_command_descriptor(self, name):
        self.__write_command_descriptor(name, self.main_name_to_command_map[name], False)

    def __write_command_descriptor(self, name, descriptor, is_alias):
        prefix = ' ' * 4
        print(prefix + "'" + name + "': {", file=self.__file)
        info = {'name': descriptor['name'], 'description': descriptor['description'], 'is_alias': is_alias}
        self.__write_command_descriptor_body(info)
        print(prefix + "},", file=self.__file)

    def __write_command_descriptor_body(self, info):
        prefix = ' ' * 8
        for (key, value) in info.items():
            if type(value) == str:
                value = "'{}'".format(value)
            print(prefix + "'{}': {},".format(key, value), file=self.__file)

    def __write_alias_command_descriptor(self, name):
        self.__write_command_descriptor(name, self.aliases_to_command_map[name], True)

    def __update_symlinks(self):
        for name in self.main_name_to_command_map:
            self.__update_symlink_for_command(name, self.main_name_to_command_map[name])
        for alias in self.aliases_to_command_map:
            self.__update_symlink_for_command(alias, self.aliases_to_command_map[alias])

    def __update_symlink_for_command(self, name, command):
        print("Unsupported function:")
        print("ln -nfs '{command_directory}' '{base_directory}/{name}'".format(command_directory=command['directory'],
                                                                                    base_directory=self.target_directory,
                                                                                    name=name))


class PluginRegistry(object):
    def __init__(self, config_directory, command_registry):
        self.__config_directory = config_directory
        self.__plugins_py_file_name = self.__config_directory + '/plugins.py'
        self.__activated_plugin_directory = self.__config_directory + '/plugins/activated'
        self.__command_registry = command_registry

        self.__plugins = {}
        self.__loaded_commands = []
        self.__loaded_tools_commands = []
        self.__plugin_lib_dirs = []

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
        plugin_names = self.__get_plugin_name_list()
        self.__load_plugins(plugin_names)
        self.__verify_loaded_commands()
        generator = CommandListFileGenerator(Dirs.get_dir('/lib/DWA/Var/commandlist.py'), self.__loaded_commands, self.__plugin_lib_dirs)
        generator.generate()
        updater = ToolsCommandUpdater(Dirs.get_dir('/lib/DWA/Var/toolscommandlist.py'),
                                      self.__loaded_tools_commands,
                                      Dirs.get_dir('/lib/DWA/ToolsCommand/installedcommands'))
        updater.generate()

    def __get_plugin_name_list(self):
        listing = os.listdir(self.__activated_plugin_directory)
        result = list()
        for file in listing:
            if file[-4:] == '.yml' and os.path.isfile(self.__activated_plugin_directory + '/' + file):
                if file not in ['base.yml', 'core.yml']:
                    result.append(file[:-4])
        return result

    def __load_plugins(self, plugin_names):
        plugin_names = ['core'] + sorted(plugin_names)
        for name in plugin_names:
            config = YamlConfig()
            filename = self.__activated_plugin_directory + '/' + name + '.yml'
            config.open(filename)
            if name == 'core':
                directory = Dirs.get_root_dir()
            else:
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

        if name != 'core':
            plugin_libdir = directory + '/' + libdir
            sys.path.append(plugin_libdir)
            self.__plugin_lib_dirs.append(plugin_libdir)
        else:
            plugin_libdir = Dirs.get_dir('/lib')

        if command_module_type[:5] == 'TYPE_':
            command_module_type = command_module_type[5:]

        if command_module_type == 'MODULE_NAME_WITH_COMMAND_SUFFIX_IS_THE_COMMAND_CLASS_NAME':
            self.__load_commands_with_module_and_class_name(plugin,
                                                            '{pluginlibdir}/{modulename}'.format(pluginlibdir=plugin_libdir,
                                                                                                 modulename=command_module_name.replace('.', '/')),
                                                            command_module_name)
        else:
            raise DWAException("This command type is not yet supported; plugin_name='{}', type='{}'".format(name, command_module_type))

        if config.get('source.toolscommandmodule') is None:
            return
        tools_command_module_type = config.get('source.toolscommandmodule.type', 'SEPARATED_MODULES')
        tools_command_module_name = config.get('source.toolscommandmodule.name')

        if tools_command_module_type[:5] == 'TYPE_':
            tools_command_module_type = tools_command_module_type[5:]

        if tools_command_module_type != 'SEPARATED_MODULES':
            raise DWAException("The source.toolscommandmodule.type cannot be other than SEPARATED MODULES; type='{}'".format(tools_command_module_type))

        self.__load_tools_commands(plugin,
                                   '{pluginlibdir}/{modulename}'.format(pluginlibdir=plugin_libdir,
                                                                        modulename=tools_command_module_name.replace('.', '/')),
                                    tools_command_module_name)

    def __load_commands_with_module_and_class_name(self, plugin, directory, base_module_name):
        listing = ['']
        try:
            listing = sorted(os.listdir(directory))
        except OSError:
            print("Plugin directory listing failure; directory='{}'".format(directory))
        for file in listing:
            if file != '__init__.py' and os.path.isfile(directory + '/' + file) and file[-3:] == '.py':
                command_name = file[:-3]
                self.__register_command_with_module_and_class_name(plugin,
                                                                   command_name.lower(),
                                                                   base_module_name + '.' + command_name,
                                                                   command_name + 'Command')

    def __register_command_with_module_and_class_name(self, plugin, command_name, module_name, class_name):
        try:
            module = self.__load_module(module_name)
            command_class = None
            try:
                command_class = getattr(module, class_name)
            except AttributeError:
                return
            self.__loaded_commands.append({'plugin_name': plugin.get_name(),
                                           'module_name': module_name,
                                           'class_name': class_name,
                                           'name': command_name,
                                           'aliases': list(command_class.aliases)})
        except ImportError:
            pass

    def __load_module(self, module_name):
        __import__(module_name)
        return sys.modules[module_name]

    def __load_tools_commands(self, plugin, directory, base_module_name):
        listing = ['']
        try:
            listing = sorted(os.listdir(directory))
        except OSError:
            print("Plugin directory listing failure; directory='{}'".format(directory))
        for toolsdir in listing:
            if os.path.isdir(directory + '/' + toolsdir) and toolsdir != '__pycache__':
                self.__register_tools_command(plugin, directory + '/' + toolsdir, '{}.{}'.format(base_module_name, toolsdir))

    def __register_tools_command(self, plugin, directory, module_name):
        try:
            module = self.__load_module(module_name)
            command_name = None
            aliases = None
            description = '(no description)'
            try:
                command_name = getattr(module, 'name')
                aliases = getattr(module, 'aliases')
                if hasattr(module, 'description'):
                    description = getattr(module, 'description')
            except AttributeError:
                return
            self.__loaded_tools_commands.append({'plugin_name': plugin.get_name(),
                                                 'directory': directory,
                                                 'name': command_name,
                                                 'aliases': list(aliases),
                                                 'description': description})
        except ImportError:
            pass

    def __verify_loaded_commands(self):
        for command in self.__loaded_commands:
            if command['module_name'] == 'DWA.Commands.SelfUpdate' and command['name'] == 'selfupdate' and \
                    'su' in command['aliases']:
                return
        raise DWAException("Selfupdate command is not found. Rejecting update of plugin information")

    def _register_command_with_module_and_class_name(self, plugin, name, module_name, class_name):
        descriptor = ClassDescriptorWithModuleAndClassName(module_name, class_name)
        self.__command_registry.register_command_class(name, descriptor)
