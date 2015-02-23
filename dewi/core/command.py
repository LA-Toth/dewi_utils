import collections


class Command:
    name = ''
    aliases = list()

    def perform(self, args: collections.Iterable):
        raise NotImplementedError
