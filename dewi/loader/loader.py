# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections
import importlib
from dewi.core.context import Context


class PluginLoaderError(Exception):
    pass


class PluginLoader:

    def __init__(self):
        self.__loaded_plugins = dict()

    def load(self, plugin_names: collections.Iterable) -> Context:
        dependency_graph = {}
        for name in plugin_names:
            plugin = self.__get_plugin(name)
            dependency_graph[name] = plugin.get_dependencies()

        self.__build_dependency_graph(dependency_graph)

        dependency_list = []
        visited_list = []
        self.__build_dependency_list(dependency_graph, visited_list, dependency_list, dependency_graph.keys())

        context = Context()
        for plugin_name in dependency_list:
            self.__get_plugin(plugin_name).load(context)

        return context

    def __get_plugin(self, name: str):
        if name not in self.__loaded_plugins:
            plugin = self.__load_plugin(name)
            self.__loaded_plugins[name] = plugin
        return self.__loaded_plugins[name]

    def __load_plugin(self, name: str):
        try:
            module_name, class_name = name.rsplit('.', 1)
            module = importlib.import_module(module_name)
        except (ImportError, ValueError) as e:
            raise PluginLoaderError("Plugin '{}' is not found or cannot be imported; error='{}'".format(name, e))

        try:
            plugin_class = getattr(module, class_name)
        except AttributeError:
            raise PluginLoaderError("Plugin '{}' is not found".format(name))
        return plugin_class()

    def __build_dependency_graph(self, dependency_graph: dict):
        finished = False
        while not finished:
            changed = False
            for dependencies in dependency_graph.values():
                for dependency in dependencies:
                    if dependency not in self.__loaded_plugins:
                        plugin = self.__get_plugin(dependency)
                        dependency_graph[dependency] = plugin.get_dependencies()
                        changed = True
                if changed:
                    break

            if not changed:
                finished = True

    def __build_dependency_list(
            self,
            dependency_graph: dict,
            visited_nodes: list,
            dependency_list: list,
            plugin_names: collections.Iterable):
        for name in plugin_names:
            if name in dependency_list:
                continue

            if name in visited_nodes:
                raise PluginLoaderError("Circular depedency in graph")
            visited_nodes.append(name)

            dependencies = dependency_graph[name]
            self.__build_dependency_list(dependency_graph, visited_nodes, dependency_list, dependencies)
            dependency_list.append(name)

    @property
    def loaded_plugins(self) -> frozenset:
        return frozenset(self.__loaded_plugins)
