# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections
import typing

from dewi.module_framework.module import Module


class DuplicatedProvidedModule(KeyError):
    def __init__(self, provided_tag: str, filter_tag: str, module_name: str, previous_module_name: str):
        super().__init__(
            "Duplicated provided value '{}' filtered by '{}; new module: '{}', previous module: '{}'".format(
                provided_tag, filter_tag, module_name, previous_module_name))


class NotProvidedDependency(ValueError):
    def __init__(self, name: str, module_name: str):
        super().__init__("Dependency '{}' is not provided, but required by '{}'".format(name, module_name))


class CircularDependency(ValueError):
    def __init__(self, module_name: str):
        super().__init__("Circular dependency found at module '{}'".format(module_name))


class ModuleRunner:
    """Runs a set of modules in their dependency order"""

    NO_REQUIREMENT = None

    def __init__(self):
        self._modules: typing.MutableSet[Module] = set()
        self._module_name_to_module_map = dict()
        self._ordered_modules: typing.List[Module] = list()

    def add(self, module: Module):
        self._modules.add(module)

    def run(self, filter_tag: typing.Optional[str] = None):
        self._order_modules(filter_tag)

        for m in self._ordered_modules:
            self._module_name_to_module_map[m].run()

    def _order_modules(self, filter_tag: typing.Optional[str] = None):
        provided, requirements = self._collect_requirements_and_provided_values()

        dependency_graph = self._build_dependency_graph(provided, requirements, filter_tag)
        visited_list = []
        self.__build_dependency_list(dependency_graph, visited_list, dependency_graph.keys())

    def _collect_requirements_and_provided_values(self):
        requirements = {}
        provided = dict()
        for m in self._modules:
            name = m.__module__ + '.' + m.__class__.__name__
            self._module_name_to_module_map[name] = m
            for filter_tag in (m.get_filter_tags() or [None]):
                if filter_tag not in provided:
                    provided[filter_tag] = dict()
                    requirements[filter_tag] = dict()

                m_provided = m.provide()

                if m_provided in provided[filter_tag]:
                    raise DuplicatedProvidedModule(m_provided, filter_tag, name, provided[filter_tag][m_provided])

                provided[filter_tag][m_provided] = name
                requirements[filter_tag][name] = m.require() or [self.NO_REQUIREMENT]

        return provided, requirements

    def _build_dependency_graph(self, provided: dict, requirements: dict, filter_tag: typing.Optional[str] = None):
        # All of the modules should be loaded if they are valid modules filtered by filter_tag

        if filter_tag not in requirements:
            # filter tag is not known, continuing anyway with non-filtered modules
            filter_tag = None

        dependency_graph = self._prepare_dependency_graph(filter_tag, provided, requirements)

        finished = False
        while not finished:
            changed = False
            for name, dependencies in dependency_graph.items():
                for dependency in dependencies:
                    if not dependency['is_module']:
                        if dependency['value'] in provided[filter_tag]:
                            mod_name = provided[filter_tag][dependency['value']]
                            dependency['value'] = mod_name
                            dependency['is_module'] = True
                            changed = True
                            if mod_name not in dependency_graph:
                                dependency_graph[mod_name] = [dict(is_module=False, value=x)
                                                              for x in requirements[filter_tag][mod_name]]
                                break
                        elif filter_tag and dependency['value'] in provided[None]:
                            mod_name = provided[None][dependency['value']]
                            dependency['value'] = mod_name
                            dependency['is_module'] = True
                            changed = True
                            if mod_name not in dependency_graph:
                                dependency_graph[mod_name] = [dict(is_module=False, value=x)
                                                              for x in requirements[None][mod_name]]
                                break
                        elif dependency['value'] is None:
                            dependency['is_module'] = True
                            changed = True
                        else:
                            raise NotProvidedDependency(dependency['value'], name)
                if changed:
                    break

            if not changed:
                finished = True

        return dependency_graph

    def _prepare_dependency_graph(self, filter_tag: str, provided: dict, requirements: dict):
        dependency_graph = {}

        if filter_tag in requirements:
            # First, all modules having filter_tag
            for name, req in requirements[filter_tag].items():
                dependency_graph[name] = [dict(is_module=False, value=x) for x in req]

        # Second, all modules that are not have the same filter tag and don't have filter tag
        if filter_tag:
            for p, name in provided[None].items():
                if p not in provided[filter_tag]:
                    dependency_graph[name] = [dict(is_module=False, value=x) for x in requirements[None][name]]

        return dependency_graph

    def __build_dependency_list(
            self,
            dependency_graph: dict,
            visited_nodes: list,
            dep_names: collections.Iterable):

        for name in dep_names:
            if name is None or name in self._ordered_modules:
                continue

            if name in visited_nodes:
                raise CircularDependency(name)

            visited_nodes.append(name)

            dependencies = [x['value'] for x in dependency_graph[name]]
            self.__build_dependency_list(dependency_graph, visited_nodes, dependencies)
            self._ordered_modules.append(name)
