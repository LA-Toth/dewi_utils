import unittest

from DWA.Utils.Format import add_frame


class TestFormat(unittest.TestCase):
    def __generate_str(self, s):
        return '#' * 70 + '\n' + s + '#' * 70 + "\n"

    def test_add_frame(self):
        pairs = [
            ('', self.__generate_str('# \n')),
            ('a\nb', self.__generate_str('# a\n# b\n')),
            ('  a\n#b c  \nd\n',
               self.__generate_str('#   a\n# #b c  \n# d\n# \n')),
        ]

        for (str, expected) in pairs:
            self.assertEquals(expected, add_frame(str))
