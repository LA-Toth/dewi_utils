# Copyright 2018-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import dewi_core.testcase
from dewi_utils.string import center, ljust, rjust, convert_to_snake_case


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

    def test_snake_case(self):
        self.assert_equal('', convert_to_snake_case(''))
        self.assert_equal('a', convert_to_snake_case('a'))
        self.assert_equal('apple', convert_to_snake_case('apple'))
        self.assert_equal('python', convert_to_snake_case('Python'))
        self.assert_equal('camel_case_text', convert_to_snake_case('camelCaseText'))
        self.assert_equal('string_io', convert_to_snake_case('stringIO'))
        self.assert_equal('string_io', convert_to_snake_case('StringIO'))

    def test_snake_case_cant_parse_mixed_usage(self):
        # Yes, it cannot properly parse the original
        self.assert_equal('string_iobase', convert_to_snake_case('StringIOBase'))
