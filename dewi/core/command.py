# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import collections


class Command:
    name = ''
    aliases = list()

    def perform(self, args: collections.Iterable):
        raise NotImplementedError
