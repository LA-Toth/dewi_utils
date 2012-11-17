import unittest
from DWA.Core.Aliases import Aliases
from DWA.Config.YamlConfig import YamlConfig


class TestAliases(unittest.TestCase):
    def setUp(self):
        self.alias_config = { 'apple' : 'pine', 'shellfunc' : '!command with args'}
        self.config = YamlConfig()
        self.config.set_config({'dwa' : {'alias' : self.alias_config }})
        self.tested = Aliases(self.config)

    def testGetAvailableAliasesSameAsExpected(self):
        self.assertEqual(['apple', 'shellfunc'], self.tested.get_alias_names(), "List of available aliases differs")

    def testGetAliases(self):
        self.assertEqual('pine', self.tested.get_alias('apple'))
        self.assertEqual('!command with args', self.tested.get_alias('shellfunc'))
