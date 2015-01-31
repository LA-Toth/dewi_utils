# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

from dewi.core.context import Context, ContextEntryNotFound, ContextEntryAlreadyRegistered

import dewi.tests


class ContextTest(dewi.tests.TestCase):
    def set_up(self):
        self.context = Context()

    def test_that_context_is_empty_initially(self):
        self.assert_equal(0, len(self.context))

    def test_register_an_element_and_can_be_queried(self):
        class Something:
            pass

        a_thing = Something()
        self.context.register('a.name', a_thing)
        self.assert_equal(1, len(self.context))
        self.assert_equal(a_thing, self.context['a.name'])

    def test_that_exception_raised_if_entry_is_not_found(self):
        self.assert_raises(ContextEntryNotFound, self.context.__getitem__, 'something')

    def test_that_a_name_cannot_be_registered_twice(self):
        class Something:
            pass

        a_thing = Something()
        self.context.register('a.name', a_thing)
        self.assert_raises(ContextEntryAlreadyRegistered, self.context.register, 'a.name', 42)

    def test_that_an_already_registered_entry_can_be_unregistered(self):
        self.context.register('a.name', 42)
        self.context.unregister('a.name')
        self.assert_equal(0, len(self.context))

    def test_that_unregistering_unknown_entry_raises_exception(self):
        self.assert_raises(ContextEntryNotFound, self.context.unregister, 'a.name')
