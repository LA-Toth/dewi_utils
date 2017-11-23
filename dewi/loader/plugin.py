# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections
from dewi.core.context import Context


class Plugin:
    """
    A plugin is an extension of DEWI.
    """

    def get_description(self) -> str:
        raise NotImplementedError

    def get_dependencies(self) -> collections.Iterable:
        return ()

    def load(self, c: Context):
        raise NotImplementedError
