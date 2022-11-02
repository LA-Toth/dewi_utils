# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import collections.abc
from collections import defaultdict

import yaml
from yaml.dumper import Dumper

from dewi_core.config.node import Node


class NodeWithName(Node):
    name: str

    def __init__(self):
        self.name = None


class DefaultDict(defaultdict):
    def __init__(self, default_factory: type[NodeWithName]):
        super().__init__(default_factory)

    def __missing__(self, key):
        obj = super().__missing__(key)
        obj.name = key
        return obj


class Field(NodeWithName):
    """
    Represents a line or field in a munin Graph
    """
    options: dict[str, str]
    filename: str

    def __init__(self):
        super().__init__()
        self.options = dict()
        self.filename = None


class Plugin(NodeWithName):
    category: str
    title: str
    period: str
    options: dict[str, str]
    fields: dict[str, Field]
    field_order: list[str]

    def __init__(self):
        super().__init__()
        self.category = None
        self.title = None
        self.period = None
        self.options = dict()
        self.fields = DefaultDict(Field)
        self.field_order = list()


class Host(NodeWithName):
    plugins: dict[str, Plugin]

    def __init__(self):
        super().__init__()
        self.plugins: dict[str, Plugin] = DefaultDict(Plugin)


class Domain(NodeWithName):
    def __init__(self):
        super().__init__()
        self.hosts = DefaultDict(Host)


class GraphConfig(Node):
    domains: dict[str, Domain]

    def __init__(self):
        self.domains = DefaultDict(Domain)

    @property
    def hosts(self) -> collections.abc.Iterator[tuple[str, str, str]]:
        for domain in self.domains:
            for host in self.domains[domain].hosts:
                yield domain, host

    @property
    def plugins(self) -> collections.abc.Iterator[tuple[str, str, str]]:
        for domain in self.domains:
            for host in self.domains[domain].hosts:
                for plugin in self.domains[domain].hosts[host].plugins:
                    yield domain, host, plugin

    @property
    def fields(self) -> collections.abc.Iterator[tuple[str, str, str, str]]:
        for domain in self.domains:
            for host in self.domains[domain].hosts:
                for plugin in self.domains[domain].hosts[host].plugins:
                    for field in self.domains[domain].hosts[host].plugins[plugin].fields:
                        yield domain, host, plugin, field


def represent_node(dumper: Dumper, data: DefaultDict):
    return dumper.represent_dict(data)


yaml.add_multi_representer(DefaultDict, represent_node)
