# Copyright (c) 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import dewi.tests

from dewi.commands.edit.edit import convert_to_vim_args


class TestVimArgumentConverter(dewi.tests.TestCase):
    def test_empty_list_is_not_changed(self):
        self.assert_equal([], convert_to_vim_args([]))

    def test_filename_is_not_changed(self):
        self.assert_equal(['path/to/file34.txt'], convert_to_vim_args(['path/to/file34.txt']))

    def test_file_colon_number_is_converted_to_line_number(self):
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42']))
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42:']))

    def test_file_names_with_line_and_column_number_are_converted(self):
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42:12']))
        self.assert_equal(['path/to/file34.txt', '+42'], convert_to_vim_args(['path/to/file34.txt:42:12:']))

    def test_multiple_args_are_prefixed_by_p_option(self):
        self.assert_equal(
            ['-p', 'path/to/file34.txt:34', 'path/to/file35.txt'],
            convert_to_vim_args(['path/to/file34.txt:34', 'path/to/file35.txt']))
