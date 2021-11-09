# Copyright 2012-2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
# vim: sts=4 ts=8 et ai

# vim: ts=8 sts=4 et ai

import os

from dewi_core.config.iniconfig import IniConfig

import dewi_core.testcase
from dewi_utils.config import ConfigLoader, InvalidMetaConfig, ConfigWriter


class TestConfigModule(dewi_core.testcase.TestCase):

    def set_up(self):
        self.cfg_file ='/tmp/test-cfg-mod.config'
        self.settings = [
            ['remote.origin', 'branch', 'master'],
            ['remote.origin', 'b', 'other'],
            ['stew', 'aliasx', 'apple'],
        ]

    def test_cfg_init(self):
        cfg =IniConfig()
        self.assert_is_none(cfg.config_file)
        self.assert_is_not_none(cfg.parser)

    def _verify_config(self, config):
        settings_sections_options = {}
        # Verify values
        for (section, option, value) in self.settings:
            cfg_value = config.get(section, option)
            self.assert_equal(cfg_value, value)

        # Fill settings_sections_options
        for (section, option, value) in self.settings:
            if section not in settings_sections_options:
                settings_sections_options[section] = []
            if option not in settings_sections_options[section]:
                settings_sections_options[section].append(option)

        # Verify that no extra value is stored
        self.assert_equal(sorted(settings_sections_options.keys()), sorted(config.get_sections()))
        for section, options in settings_sections_options.items():
            self.assert_equal(sorted(options), sorted(config.get_options(section)))

    def test_set_get_save_load(self):
        # Test assumes it
        self.assert_false(os.path.exists(self.cfg_file))
        cfg =IniConfig()
        cfg.open(self.cfg_file)
        for (section, option, value) in self.settings:
            cfg.set(section, option, value)

        self._verify_config(cfg)

        # Before the first write it can't exist
        self.assert_false(os.path.exists(self.cfg_file))
        cfg.write()
        self.assert_true(os.path.exists(self.cfg_file))

        with open(self.cfg_file, 'r') as f:
            content = f.read()
        # In fact, it is 67, but it cannot be guaranteed
        self.assert_true(len(content) > 1)

        # let's open it
        new_config =IniConfig()
        new_config.open(self.cfg_file)
        self._verify_config(new_config)
        os.unlink(self.cfg_file)

    def test_overwrite_and_delete(self):
        # Saving because the order of test functions is not guaranteed
        saved_settings = list(self.settings)
        # Test assumes it
        self.assert_false(os.path.exists(self.cfg_file))
        cfg =IniConfig()
        cfg.open(self.cfg_file)
        for (section, option, value) in self.settings:
            cfg.set(section, option, value)

        self._verify_config(cfg)

        self.settings[0][2] += " Something not too useful"
        cfg.set(self.settings[0][0], self.settings[0][1], self.settings[0][2])
        self._verify_config(cfg)

        cfg.remove(self.settings[1][0], self.settings[1][1])
        del self.settings[1]
        self._verify_config(cfg)

        self.settings = saved_settings

    def test_other_functions(self):
        # Test assumes it
        self.assert_false(os.path.exists(self.cfg_file))
        cfg =IniConfig()
        cfg.open(self.cfg_file)

        # testing has
        self.assert_false(cfg.has('an', 'apple'))
        cfg.set('an', 'apple', 'is red')
        self.assert_equal(cfg.get('an', 'apple'), 'is red')
        self.assert_true(cfg.has('an', 'apple'))
        cfg.remove('an', 'apple')
        self.assert_false(cfg.has('an', 'apple'))

        # cfg must not be empty
        cfg.set('an', 'apple', 'is red')
        self.assert_equal(cfg.get('an', 'apple'), 'is red')

        # testing default return values
        self.assert_equal(cfg.get_sections(), ['an'])
        self.assert_equal(cfg.get_options('an'), ['apple'])
        self.assert_equal(cfg.get_options('death star'), [])
        self.assert_equal(cfg.get('siths', 'darth vader'), None)

        cfg.set('an apple', 'is red', '!%@#""' + "\nangry bird")
        self.assert_equal(cfg.get('an apple', 'is red'), '!%@#""' + "\nangry bird")
        self.assert_equal(cfg.get_or_default_value('an apple', 'is red', 'green'), '!%@#""' + "\nangry bird")
        self.assert_equal(cfg.get_or_default_value('an apple', 'is not red', 'green'), 'green')

    def test_write_without_open_fails(self):
        cfg =IniConfig()
        self.assert_raises(Exception, cfg.write)


class _LoaderWriterSetConfigMixin:

    def test_set_a_valid_config(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'inverse-bool',
                'default': False
            },
            'a_node': {
                'type': 'node',
                'an_int': {
                    'entry': 'an.int_entry',
                    'type': 'int',
                    'default': 0
                }
            }
        }
        self._tested.set_meta_config(dict(meta_config))
        self.assert_equal(meta_config, self._tested.meta_config)

    def test_set_non_config_raises_exception(self):
        config = dict(a='b', c=42)
        self.assert_raises(InvalidMetaConfig, self._tested.set_meta_config, config)

    def test_set_an_invalid_type_raises_exception(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'bool',
                'default': False
            },
            'a_node': {
                'type': 'node',
                'an_int': {
                    'entry': 'an.int_entry',
                    'type': 'invalidtype',
                    'default': 0
                }
            }
        }
        self.assert_raises(InvalidMetaConfig, self._tested.set_meta_config, meta_config)


class TestConfigLoader(dewi_core.testcase.TestCase, _LoaderWriterSetConfigMixin):

    def set_up(self):
        self._tested = ConfigLoader()

    def test_load_a_string_entry(self):
        meta_config = {
            'sample_text': {
                'entry': 'an.example',
                'type': 'string',
                'default': 'something'
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()

        self.assert_equal(dict(sample_text='something'), self._tested.load(config))

        config.set('an', 'example', 'some text')
        self.assert_equal(dict(sample_text='some text'), self._tested.load(config))

    def test_load_an_int_entry(self):
        meta_config = {
            'an_int': {
                'entry': 'an.example',
                'type': 'int',
                'default': 42
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()

        self.assert_equal(dict(an_int=42), self._tested.load(config))

        config.set('an', 'example', '33')
        self.assert_equal(dict(an_int=33), self._tested.load(config))

    def test_load_a_bool_entry(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'bool',
                'default': True
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()

        self.assert_equal(dict(a_bool=True), self._tested.load(config))

        config.set('an', 'example', 'no')
        self.assert_equal(dict(a_bool=False), self._tested.load(config))

        config.set('an', 'example', 'yes')
        self.assert_equal(dict(a_bool=True), self._tested.load(config))

    def test_load_an_inverse_bool_entry(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'inverse-bool',
                'default': False
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()

        self.assert_equal(dict(a_bool=False), self._tested.load(config))

        config.set('an', 'example', 'no')
        self.assert_equal(dict(a_bool=True), self._tested.load(config))

        config.set('an', 'example', 'yes')
        self.assert_equal(dict(a_bool=False), self._tested.load(config))

    def test_load_nodes(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'inverse-bool',
                'default': False
            },
            'a_node': {
                'type': 'node',
                'an_int': {
                    'entry': 'an.int_entry',
                    'type': 'int',
                    'default': 0
                },
                'another_node': {
                    'type': 'node',
                    'a_string': {
                        'entry': 'a.string',
                        'type': 'string',
                        'default': 'default string-value'
                    },
                }
            }
        }
        self._tested.set_meta_config(meta_config)
        config =IniConfig()
        config.set('an', 'example', 'no')
        config.set('an', 'int_entry', '42')

        self.assert_equal(
            dict(a_bool=True, a_node=dict(an_int=42, another_node=dict(a_string='default string-value'))),
            self._tested.load(config)
        )


class TestConfigWriter(dewi_core.testcase.TestCase, _LoaderWriterSetConfigMixin):

    def set_up(self):
        self._tested = ConfigWriter()

    def test_write_a_string_entry_which_is_not_set(self):
        meta_config = {
            'sample_text': {
                'entry': 'an.example',
                'type': 'string',
                'default': 'something'
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()
        self._tested.write(dict(), config)
        self.assert_equal('the-default-value', config.get_or_default_value('an', 'example', 'the-default-value'))

    def test_write_a_string_entry(self):
        meta_config = {
            'sample_text': {
                'entry': 'an.example',
                'type': 'string',
                'default': 'something'
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()
        self._tested.write(dict(sample_text='some text'), config)
        self.assert_equal('some text', config.get_or_default_value('an', 'example', 'unexpected-default-value'))

    def test_write_an_int_entry(self):
        meta_config = {
            'an_int': {
                'entry': 'an.example',
                'type': 'int',
                'default': 42
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()
        self._tested.write(dict(), config)
        self.assert_equal('the-default-value', config.get_or_default_value('an', 'example', 'the-default-value'))

        self._tested.write(dict(an_int=45), config)
        self.assert_equal('45', config.get_or_default_value('an', 'example', 'unexpected-default-value'))

    def test_write_a_bool_entry(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'bool',
                'default': True
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()

        self._tested.write(dict(), config)
        self.assert_equal('the-default-value', config.get_or_default_value('an', 'example', 'the-default-value'))

        self._tested.write(dict(a_bool=True), config)
        self.assert_equal('yes', config.get_or_default_value('an', 'example', 'unexpected-default-value'))

        self._tested.write(dict(a_bool=False), config)
        self.assert_equal('no', config.get_or_default_value('an', 'example', 'unexpected-default-value'))

    def test_write_an_inverse_bool_entry(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'inverse-bool',
                'default': False
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()

        self._tested.write(dict(), config)
        self.assert_equal('the-default-value', config.get_or_default_value('an', 'example', 'the-default-value'))

        self._tested.write(dict(a_bool=False), config)
        self.assert_equal('yes', config.get_or_default_value('an', 'example', 'unexpected-default-value'))

        self._tested.write(dict(a_bool=True), config)
        self.assert_equal('no', config.get_or_default_value('an', 'example', 'unexpected-default-value'))

    def test_write_nodes(self):
        meta_config = {
            'a_bool': {
                'entry': 'an.example',
                'type': 'inverse-bool',
                'default': False
            },
            'a_node': {
                'type': 'node',
                'an_int': {
                    'entry': 'an.int_entry',
                    'type': 'int',
                    'default': 0
                },
                'another_node': {
                    'type': 'node',
                    'a_string': {
                        'entry': 'a.string',
                        'type': 'string',
                        'default': 'default string-value'
                    },
                }
            }
        }

        self._tested.set_meta_config(meta_config)
        config =IniConfig()

        self._tested.write(dict(), config)
        self.assert_equal('the-default-value', config.get_or_default_value('an', 'example', 'the-default-value'))

        self._tested.write(dict(a_bool=False, a_node=dict(another_node=dict(a_string='some_value'))), config)
        self.assert_equal('yes', config.get_or_default_value('an', 'example', 'unexpected-default-value'))
        self.assert_equal('the-default-value', config.get_or_default_value('an', 'int_entry', 'the-default-value'))
        self.assert_equal('some_value', config.get_or_default_value('a', 'string', 'unexpected-default-value'))
