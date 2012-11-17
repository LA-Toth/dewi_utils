import unittest

from DWA.Config.YamlConfig import YamlConfig
import tempfile
import os
from DWA.Core.State import get_dir


class TestYamlConfig(unittest.TestCase):
    def setUp(self):
        self.tested = YamlConfig()
        self.config = { 'a' : 3 , 'b' : 43, 'd' : { 'foo' : 1, 'bar': [4, 5]}}

    def testSaveAndOpenWorks(self):
        (handle, filename) = tempfile.mkstemp(prefix="dwa_test_yml_", text=True)
        self.tested.open(filename)
        self.tested.set_config(self.config)
        self.tested.write()
        self.tested.close()
        self.tested.set_config([42])
        self.assertSequenceEqual([42], self.tested.get_config(), "YamlConfig contains bad data")
        self.tested.open(filename)
        self.assertSequenceEqual(self.config, self.tested.get_config(), "Unable to reread content")
        self.tested.close()
        os.close(handle)

    def testFreshlyCreatedInstanceContainsDict(self):
        self.assertIsInstance(self.tested.config, dict, "YamlConfig is badly initialized, dict is expected")
        self.assertIsInstance(self.tested.get_config(), dict, "YamlConfig is badly initialized, dict is expected")
        self.assertEqual(self.tested.config, dict(), "YamlConfig doesn't contain any empty dict")

    def testOpenFallsBackToDict(self):
        (handle, filename) = tempfile.mkstemp(prefix="dwa_test_yml_", text=True)
        self.tested.open(filename)
        self.tested.set_config(self.config)
        self.assertSequenceEqual(self.config, self.tested.get_config(), "Unable to get content")
        self.tested.write()
        self.tested.close()
        self.tested.open(get_dir('foo.bar/what&-c,&>#^#'))
        self.assertEqual(self.tested.config, dict(), "YamlConfig doesn't contain any empty dict")
        self.tested.close()
        os.close(handle)

    def testClearInitializesConfigToDict(self):
        self.tested.set_config(self.config)
        self.assertSequenceEqual(self.config, self.tested.get_config(), "Unable to get content")
        self.tested.clear()
        self.assertEqual(self.tested.config, dict(), "YamlConfig doesn't contain any empty dict")

    def testGetterBasedOnKnownValues(self):
        self.tested.set_config(self.config)
        self.assertEqual([4, 5], self.tested.get('d.bar'), "Query failed")
        self.assertEqual(None, self.tested.get('foo.bar'), "Query of non-existent element failed")

    def testSetter(self):
        self.tested.set('foo.bar.baz', self.config)
        self.assertSequenceEqual(self.config, self.tested.get('foo.bar.baz'), "Setting failed")
        self.assertSequenceEqual({ 'bar' : { 'baz' : self.config }}, self.tested.get('foo'))
        self.assertEqual(1, len(self.tested.config))

    def testEmptyFileLoadedAsDict(self):
        (handle, filename) = tempfile.mkstemp(prefix="dwa_test_yml_", text=True)
        self.tested.open(filename)
        self.assertDictEqual(dict(), self.tested.get_config())
        os.close(handle)
