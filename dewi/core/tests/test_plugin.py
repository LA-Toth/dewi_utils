# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3
from dewi.loader.tests import TestLoadable


class TestPlugin(TestLoadable):
    def test_plugin(self):
        self.assert_loadable('dewi.core.CorePlugin')
