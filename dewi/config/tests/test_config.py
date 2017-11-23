# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import dewi.tests
from dewi.config.config import Config, InvalidEntry


class ConfigTest(dewi.tests.TestCase):
    def set_up(self):
        self.tested = Config()

    def test_creation(self):
        self.assert_equal(dict(), self.tested.get_config())

    def test_top_level_set_and_get(self):
        self.tested.set('an_entry', 'value')
        self.assert_equal(dict(an_entry='value'), self.tested.get_config())
        self.assert_equal('value', self.tested.get('an_entry'))

    def test_set_of_child_item(self):
        self.tested.set('parent.child', 42)
        self.assert_equal(dict(parent=dict(child=42)), self.tested.get_config())
        self.assert_equal(42, self.tested.get('parent.child'))

    def test_parent_cannot_be_overriden(self):
        self.tested.set('parent.child', 42)
        with self.assert_raises(InvalidEntry):
            self.tested.set('parent', 33)

    def test_set_of_a_list(self):
        self.tested.set('a_list.0', 42)
        self.assert_equal(dict(a_list={'0': 42}), self.tested.get_config())
        self.assert_equal(42, self.tested.get('a_list.0'))
