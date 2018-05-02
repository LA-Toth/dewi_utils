# Copyright 2015-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections

from dewi.core import CommandRegistry, CommandRegistrar


class ContextError(Exception):
    pass


class ContextEntryNotFound(ContextError):
    pass


class ContextEntryAlreadyRegistered(ContextError):
    pass


class Context(collections.Mapping):
    """
    A context is a generic purpose registry, which helps
    communicate between different parts of the code. Instead of a global variable
    or module is for storing object(s), the context can be used and passed around
    the necessary objects and functions.

    An example: a CommandRegistry object can be registered into this context.
    """

    def __init__(self):
        c = CommandRegistry()
        self.__entries = {
            'commands': CommandRegistrar(c),
            'commandregistry': c,
        }

    @property
    def command_registry(self) -> CommandRegistry:
        return self.__entries['commandregistry']

    @property
    def commands(self) -> CommandRegistrar:
        return self.__entries['commands']

    def register(self, name: str, value):
        """
        Registers an element into the context. It doesn't support overwriting already
        registered entries, in that case `ContextEntryAlreadyRegistered` will be raised.

        :param name: the name of the new entry
        :param value: the value of the new entry
       """
        if name in self.__entries:
            raise ContextEntryAlreadyRegistered("Context entry {!r} already registered".format(name))
        self.__entries[name] = value

    def unregister(self, name: str):
        """
        Unregisters an already registered entry
        :param name: The name of the entry to be unregistered
        """
        self.__check_entry(name)

        del self.__entries[name]

    def __check_entry(self, name: str):
        if name not in self.__entries:
            raise ContextEntryNotFound("Requested context entry {!r} is not registered".format(name))

    def __len__(self):
        return len(self.__entries)

    def __getitem__(self, item):
        self.__check_entry(item)

        return self.__entries[item]

    def __contains__(self, item):
        return item in self.__entries

    def __iter__(self):
        return iter(self.__entries)
