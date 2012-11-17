import unittest

from mock import Mock
import os
from DWA.Core.PluginRegistry import Plugin, PluginRegistry
from DWA.Config.YamlConfig import YamlConfig
from DWA.Core.State import get_dir
from DWA.Core.CommandRegistry import CommandRegistry

_sample_config = {'a': 42, 'b': [1, 2, {'c': 3}]}


class YamlConfigStub(YamlConfig):
    def _open(self):
        pass

    def write(self):
        pass


class PluginTest(unittest.TestCase):
    def setUp(self):
        class PluginRegistryMock():
            pass
        self.__registry = PluginRegistryMock()

        self.mock = Mock()
        self.__plugin_name = "plugname"
        self.__plugin_location = "/tmp"
        self.__plugin_basepath = 'lib/'
        self.tested = Plugin(self.__registry, self.__plugin_name, self.__plugin_location,  self.__plugin_basepath)

    def test_name_config_and_location(self):
        self.assertEqual(self.__plugin_name, self.tested.get_name())
        self.assertEqual(self.__plugin_location, self.tested.get_location())
        self.assertEqual(self.__plugin_basepath, self.tested.get_basepath())

    def test_register_a_concrete_class(self):
        class X:
            pass

        self.__registry._register_command_class = self.mock
        self.tested.register_command_class('Name', X)
        self.mock.assert_called_once_with(self.tested, 'Name', X)

    def test_register_a_module_where_class_has_same_name(self):
        self.__registry._register_command_module = self.mock
        self.tested.register_command_module('foo', 'A.B.CheckoutCommand')
        self.mock.assert_called_once_with(self.tested, 'foo', 'A.B.CheckoutCommand')

    def test_register_a_module_with_cmdclass_attribute(self):
        self.__registry._register_command_with_module_and_cmdclass_attribute = self.mock
        self.tested.register_command_with_module_and_cmdclass_attribute('apple', 'A.B.installed.X')
        self.mock.assert_called_once_with(self.tested, 'apple', 'A.B.installed.X')

    def test_register_command_with_module_name_and_class_name(self):
        self.__registry._register_command_with_module_and_class_name = self.mock
        self.tested.register_command_with_module_and_class_name('apple', 'A.X', 'XCommand')
        self.mock.assert_called_once_with(self.tested, 'apple', 'A.X', 'XCommand')

    def test_register_commands(self):
        commands_type = Plugin.TYPE_MODULE_AND_CLASS_HAS_SAME_NAME
        self.__registry._register_commands = self.mock
        self.tested.register_commands('MyPlugin.Commands', commands_type)
        self.mock.assert_called_once_with(self.tested, 'MyPlugin.Commands', commands_type)


class PluginRegistryBasicTest(unittest.TestCase):
    def setUp(self):
        self.mock = Mock()
        self.tested = PluginRegistry('/nonexistent', CommandRegistry())

    def test_new_plugin_can_be_registered(self):
        self.tested.register('myplugin-name', '/tmp', 'lib')
        registered_plugin = self.tested.get_plugin('myplugin-name')
        self.assertNotEqual(None, registered_plugin)
        self.assertEqual(1, self.tested.count())

    def test_freshly_created_plugin_registry_is_empty(self):
        self.assertEqual(0, self.tested.count())


class PluginRegistryFunctionalTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists(get_dir('samples/etc/plugins.py')):
            os.unlink(get_dir('samples/etc/plugins.py'))
        self.mock = Mock()
        self.tested = PluginRegistry(get_dir('samples/etc'), CommandRegistry())

# This test would fail
#    def test_plugins_can_be_loaded(self):
#        self.tested.load_plugins()
#        self.assertTrue(os.path.exists(get_dir('samples/etc/plugins.py')))
