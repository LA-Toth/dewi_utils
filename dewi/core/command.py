import collections


class Command:
    name = ''

    def perform(self, args: collections.Iterable):
        raise NotImplementedError
