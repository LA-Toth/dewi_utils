# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import collections

from dewi.core.context import Context
from dewi.loader.loader import PluginLoader, PluginLoaderError
from dewi.loader.plugin import Plugin
import dewi.tests


class TestPlugin1(Plugin):
    def get_description(self) -> str:
        return "Sample description"

    def get_dependencies(self) -> collections.Iterable:
        return ()

    def load(self, c: Context):
        c.register('plugin1', 42)


class TestPlugin2a(Plugin):
    def get_description(self) -> str:
        return "Sample description"

    def get_dependencies(self) -> collections.Iterable:
        return ('dewi.loader.tests.test_loader.TestPlugin1',)

    def load(self, c: Context):
        c.register('plugin2a', 12)


class TestPlugin2b(Plugin):
    def get_description(self) -> str:
        return "Sample description"

    def get_dependencies(self) -> collections.Iterable:
        return ('dewi.loader.tests.test_loader.TestPlugin1',)

    def load(self, c: Context):
        c.register('plugin2b', 22)


class TestPlugin3(Plugin):
    def get_description(self) -> str:
        return "Sample description"

    def get_dependencies(self) -> collections.Iterable:
        return (
            'dewi.loader.tests.test_loader.TestPlugin2a',
            'dewi.loader.tests.test_loader.TestPlugin2b',
        )

    def load(self, c: Context):
        c.register('plugin3', 342)
        c.register('result', c['plugin2a'] + c['plugin2b'] + c['plugin1'])


class TestPluginWithInvalidDependencies1(Plugin):
    def get_description(self) -> str:
        return "Sample description"

    def get_dependencies(self) -> collections.Iterable:
        return (
            'dewi.loader2.tests2.test_loader2.TestPlugin1',
            'dewi.loader.tests.test_loader.TestPluginThatWillNeverExist',
        )

    def load(self, c: Context):
        c.register('pluginX', 2242)


class TestPluginO1(Plugin):
    def get_description(self):
        return "plugin with circular dependencies"

    def get_dependencies(self):
        return ('dewi.loader.tests.test_loader.TestPluginO2',)

    def load(self, c: Context):
        c.register('pluginO1', 2242)


class TestPluginO2(Plugin):
    def get_description(self):
        return "plugin with circular dependencies"

    def get_dependencies(self):
        return ('dewi.loader.tests.test_loader.TestPluginO1',)

    def load(self, c: Context):
        c.register('pluginO2', 2242)


class TestLoader(dewi.tests.TestCase):
    def set_up(self):
        self.loader = PluginLoader()

    def test_load_plugin_without_dependencies(self):
        context = self.loader.load({'dewi.loader.tests.test_loader.TestPlugin1'})
        self.assert_equal(42, context['plugin1'])

    def test_that_a_plugin_can_be_loaded_twice_and_the_second_is_ignored(self):
        context = self.loader.load(
            ['dewi.loader.tests.test_loader.TestPlugin1', 'dewi.loader.tests.test_loader.TestPlugin1'])
        self.assert_equal(42, context['plugin1'])

    def test_load_plugin_with_invalid_class_name(self):
        self.assert_raises(
            PluginLoaderError,
            self.loader.load, {'dewi.loader.tests.test_loader.TestPluginThatWillNeverExist'})

    def test_load_plugin_with_invalid_module_name(self):
        self.assert_raises(
            PluginLoaderError,
            self.loader.load, {'dewi.loader.tests42.test_loader.TestPluginThatWillNeverExist'})

    def test_load_plugin_without_module_name(self):
        self.assert_raises(
            PluginLoaderError,
            self.loader.load, {'J316'})

    def test_load_plugin_with_single_dependency(self):
        context = self.loader.load({'dewi.loader.tests.test_loader.TestPlugin2a'})
        self.assert_equal(12, context['plugin2a'])
        self.assert_equal(42, context['plugin1'])

    def test_that_multiple_plugins_can_be_loaded_at_once(self):
        context = self.loader.load(
            {'dewi.loader.tests.test_loader.TestPlugin2a', 'dewi.loader.tests.test_loader.TestPlugin2b'})
        self.assert_equal(12, context['plugin2a'])
        self.assert_equal(22, context['plugin2b'])

    def test_load_plugin_with_multiple_dependencies(self):
        context = self.loader.load({'dewi.loader.tests.test_loader.TestPlugin3'})
        self.assert_equal(342, context['plugin3'])
        self.assert_equal(76, context['result'])

    def test_load_plugin_with_invalid_dependency_list(self):
        self.assert_raises(
            PluginLoaderError,
            self.loader.load, {'dewi.loader.tests.test_loader.TestPluginWithInvalidDependencies1'})

    def test_circular_dependency(self):
        self.assert_raises(
            PluginLoaderError,
            self.loader.load, {'dewi.loader.tests.test_loader.TestPluginO1'})

    def test_loaded_plugin_property(self):
        self.assert_equal(set(), self.loader.loaded_plugins)
        self.loader.load({'dewi.loader.tests.test_loader.TestPlugin3'})
        self.assert_equal(
            {
                'dewi.loader.tests.test_loader.TestPlugin3',
                'dewi.loader.tests.test_loader.TestPlugin1',
                'dewi.loader.tests.test_loader.TestPlugin2a',
                'dewi.loader.tests.test_loader.TestPlugin2b',
            },
            self.loader.loaded_plugins
        )
