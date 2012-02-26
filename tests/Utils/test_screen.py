import unittest

from DWA.Utils.Screen import add_frame


class TestScreen(unittest.TestCase):
    def __generate_str(self, str):
        return '#' * 70 + '\n' + str + '#' * 70 + "\n"

    def test_add_frame(self):
        pairs = [
            ('', self.__generate_str('# \n')),
            ('a\nb', self.__generate_str('# a\n# b\n')),
            ('  a\n#b c  \nd\n',
               self.__generate_str('#   a\n# #b c  \n# d\n# \n')),
        ]

        for (str, expected) in pairs:
            self.assertEquals(expected, add_frame(str))
