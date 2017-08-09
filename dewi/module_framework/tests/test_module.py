# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

from unittest.mock import Mock, call

import dewi.tests
from dewi.config.config import Config
from dewi.module_framework.messages import Level, Messages
from dewi.module_framework.module import Module


class ModuleTest(dewi.tests.TestCase):

    def test_module_wraps_config_set(self):
        cfg = Mock(Config)

        m = Module(cfg, Messages())
        m.set('an.entry', 42)
        m.set('path', 'str-value')

        self.assert_equal(
            [call.set('an.entry', 42), call.set('path', 'str-value')],
            cfg.mock_calls
        )

    def test_module_wraps_config_get(self):
        cfg = Mock(Config)
        cfg.get.return_value = 3

        m = Module(cfg, Messages())
        self.assert_equal(3, m.get('an.entry'))
        self.assert_equal(
            [call.get('an.entry')],
            cfg.mock_calls
        )

    def test_module_wraps_messages_add(self):
        msgs = Mock(Messages)
        m = Module(Config(), msgs)
        m.add_message(Level.INFO, 'category', 'subcat', 'a message')

        self.assert_equal(
            [call.add(Level.INFO, 'category', 'subcat', 'a message', details=None, hint=None)],
            msgs.mock_calls
        )
