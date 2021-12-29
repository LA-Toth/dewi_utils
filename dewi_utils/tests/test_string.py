# Copyright 2018-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import dewi_core.testcase
from dewi_utils.string import center, ljust, rjust


class StringTest(dewi_core.testcase.TestCase):
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
