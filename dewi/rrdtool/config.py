# Copyright 2017-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import typing
from collections import defaultdict

import yaml
from yaml.dumper import Dumper

from dewi.config.node import Node


class NodeWithName(Node):
    def __init__(self):
        self.name: str = None


class DefaultDict(defaultdict):
    def __init__(self, default_factory: typing.Type[NodeWithName]):
        super().__init__(default_factory)

    def __missing__(self, key):
        obj = super().__missing__(key)
        obj.name = key
        return obj


class Field(NodeWithName):
    """
    Represents a line or field in a munin Graph
    """

    def __init__(self):
        super().__init__()
        self.options: typing.Dict[str, str] = dict()
        self.filename: str = None


class Plugin(NodeWithName):
    def __init__(self):
        super().__init__()
        self.category: str = None
        self.title: str = None
        self.period: str = None
        self.options: typing.Dict[str, str] = dict()
        self.fields: typing.Dict[str, Field] = DefaultDict(Field)
        self.field_order: typing.List[str] = list()


class Host(NodeWithName):
    def __init__(self):
        super().__init__()
        self.plugins: typing.Dict[str, Plugin] = DefaultDict(Plugin)


class Domain(NodeWithName):
    def __init__(self):
        super().__init__()
        self.hosts: typing.Dict[str, Host] = DefaultDict(Host)


class GraphConfig(Node):
    def __init__(self):
        self.domains: typing.Dict[str, Domain] = DefaultDict(Domain)

    @property
    def hosts(self) -> typing.Iterator[typing.Tuple[str, str, str]]:
        for domain in self.domains:
            for host in self.domains[domain].hosts:
                yield domain, host

    @property
    def plugins(self) -> typing.Iterator[typing.Tuple[str, str, str]]:
        for domain in self.domains:
            for host in self.domains[domain].hosts:
                for plugin in self.domains[domain].hosts[host].plugins:
                    yield domain, host, plugin

    @property
    def fields(self) -> typing.Iterator[typing.Tuple[str, str, str, str]]:
        for domain in self.domains:
            for host in self.domains[domain].hosts:
                for plugin in self.domains[domain].hosts[host].plugins:
                    for field in self.domains[domain].hosts[host].plugins[plugin].fields:
                        yield domain, host, plugin, field


def represent_node(dumper: Dumper, data: DefaultDict):
    return dumper.represent_dict(data)


yaml.add_multi_representer(DefaultDict, represent_node)
