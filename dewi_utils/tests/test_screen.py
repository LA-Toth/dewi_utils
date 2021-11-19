# Copyright 2012-2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import dewi_core.testcase
from dewi_utils.screen import add_frame


class ScreenTest(dewi_core.testcase.TestCase):
    def _generate_str(self, s):
        return '#' * 80 + '\n' + s + '#' * 80 + "\n"

    def test_add_frame(self):
        pairs = [
            ('', self._generate_str('# \n')),
            ('a\nb', self._generate_str('# a\n# b\n')),
            ('  a\n#b c  \nd\n',
             self._generate_str('#   a\n# #b c  \n# d\n# \n')),
        ]

        for (s, expected) in pairs:
            self.assertEquals(expected, add_frame(s))
