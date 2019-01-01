# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/


import dewi.tests
from dewi.utils.string import rjust, ljust, center


class StringTest(dewi.tests.TestCase):
    def test_rjust_width_only(self):
        self.assert_equal('  abc', rjust('abc', 5))
        self.assert_equal('abc', rjust('abc', 2))

    def test_rjust_single_char(self):
        self.assert_equal('**abc', rjust('abc', 5, '*'))
        self.assert_equal('abc', rjust('abc', 2, '*'))

    def test_rjust_multi_char(self):
        self.assert_equal('<>abc', rjust('abc', 5, '<>'))
        self.assert_equal('<><abc', rjust('abc', 6, '<>'))
        self.assert_equal('abc', rjust('abc', 2, '<>'))

    def test_ljust_width_only(self):
        self.assert_equal('abc  ', ljust('abc', 5))
        self.assert_equal('abc', ljust('abc', 2))

    def test_ljust_single_char(self):
        self.assert_equal('abc**', ljust('abc', 5, '*'))
        self.assert_equal('abc', ljust('abc', 2, '*'))

    def test_ljust_multi_char(self):
        self.assert_equal('abc<>', ljust('abc', 5, '<>'))
        self.assert_equal('abc<><', ljust('abc', 6, '<>'))
        self.assert_equal('abc', ljust('abc', 2, '<>'))


    def test_center_width_only(self):
        self.assert_equal(' abc ', center('abc', 5))
        self.assert_equal(' abc  ', center('abc', 6))
        self.assert_equal('abc', center('abc', 2))

    def test_center_single_char(self):
        self.assert_equal('*abc*', center('abc', 5, '*'))
        self.assert_equal('*abc**', center('abc', 6, '*'))
        self.assert_equal('**abc**', center('abc', 7, '*'))
        self.assert_equal('abc', center('abc', 2, '*'))

    def test_center_multi_char(self):
        self.assert_equal('<abc<', center('abc', 5, '<>'))
        self.assert_equal('<abc<>', center('abc', 6, '<>'))
        self.assert_equal('<>abc<>', center('abc', 7, '<>'))
        self.assert_equal('<>abc<><', center('abc', 8, '<>'))
        self.assert_equal('<><abc<><', center('abc', 9, '<>'))
        self.assert_equal('abc', center('abc', 2, '<>'))
