# vim: sts=4 ts=8 et ai
import collections
import configparser
import os


class IniConfig:

    def __init__(self):
        self.config_file = None
        self.parser = configparser.RawConfigParser()

    def __section_from_dotted(self, section):
        s = section.split('.', 1)
        if len(s) == 2:
            return '%s "%s"' % tuple(s)
        else:
            return section

    def __section_to_dotted(self, section):
        s = section.split('"')
        if len(s) == 3:
            return '%s.%s' % (s[0][:-1], s[1])
        else:
            return section

    def open(self, cfgfile):
        self.config_file = cfgfile
        self.parser.read(self.config_file, encoding='UTF-8')

    def write(self):
        if self.config_file is None:
            raise StewError("Unable to save config file because file name is unset")
        file_ = open(self.config_file, 'wt')
        self.parser.write(file_)
        file_.close()

    def close(self):
        pass

    def has(self, section, option):
        section = self.__section_from_dotted(section)
        return self.parser.has_option(section, option)

    def set(self, section, option, value):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, option, value)

    def get(self, section, option):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            return None
        try:
            return self.parser.get(section, option)
        except configparser.NoOptionError:
            return None

    def get_or_default_value(self, section, option, default_value):
        res = self.get(section, option)
        return res if res is not None else default_value

    def remove(self, section, option):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            return
        if not self.parser.has_option(section, option):
            return
        self.parser.remove_option(section, option)

    def get_options(self, section):
        section = self.__section_from_dotted(section)
        if not self.parser.has_section(section):
            return []
        else:
            return self.parser.options(section)

    def get_sections(self):
        return [self.__section_to_dotted(s) for s in self.parser.sections()]


class _ConfigLoaderWriter:
    def __init__(self, callbacks: collections.Mapping, meta_config: (collections.Mapping, None) = None):
        self._meta_config = meta_config or dict()
        self._callbacks = callbacks

    def set_meta_config(self, meta_config: collections.Mapping):
        self.__check_config(meta_config)
        self._meta_config = meta_config

    def __check_config(self, meta_config: collections.Mapping):
        for key in meta_config:
            self.__check_item_entry_with_type(meta_config, key)

    def __check_item_entry_with_type(self, meta_config_entry, key):
        if not isinstance(key, str):
            raise InvalidMetaConfig()
        if not isinstance(meta_config_entry[key], collections.Mapping):
            raise InvalidMetaConfig()
        self.__check_item_entry(meta_config_entry[key])

    def __check_item_entry(self, meta_config_entry: collections.Mapping):
        if 'type' not in meta_config_entry:
            raise MissingKeys({'type'})
        if meta_config_entry['type'] == 'node':
            for key in set(meta_config_entry.keys()) - {'type'}:
                self.__check_item_entry_with_type(meta_config_entry, key)
        else:
            self.__check_entry_type(meta_config_entry)

            if meta_config_entry['type'] not in self._callbacks:
                raise InvalidConfigType()

    def __check_entry_type(self, meta_config_entry):
        expected_keys = {'type', 'entry', 'default'}
        keys = set(meta_config_entry.keys())
        if len(expected_keys) < len(keys):
            raise ExtraKeys(keys - expected_keys)
        elif len(expected_keys) < len(keys):
            raise MissingKeys(expected_keys - keys)
        elif expected_keys - keys:
            raise MissingKeys(expected_keys - keys)
        elif keys - expected_keys:
            raise ExtraKeys(keys - expected_keys)

    @property
    def meta_config(self) -> collections.Mapping:
        return self._meta_config

    def _get_section_option(self, meta_config_entry):
        section, option = meta_config_entry['entry'].rsplit('.', 1)
        return section, option


class ConfigLoader(_ConfigLoaderWriter):
    def __init__(self, meta_config: (collections.Mapping, None) = None):
        super().__init__(
            {
                'string': self.__load_string_item,
                'int': self.__load_int_item,
                'bool': self.__load_bool_item,
                'inverse-bool': self.__load_inverse_bool_item,
                'node': self.__load_node,
            },
            meta_config
        )

    def load(self, config: IniConfig) -> collections.Mapping:
        result = dict()
        for key, value in self.meta_config.items():
            result[key] = self.__load_item(value, config)

        return result

    def __load_item(self, meta_config_entry: collections.Mapping, config: IniConfig):
        return self._callbacks[meta_config_entry['type']](meta_config_entry, config)

    def __load_string_item(self, meta_config_entry: collections.Mapping, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        value = config.get_or_default_value(section, option, meta_config_entry['default'])
        return str(value)

    def __load_int_item(self, meta_config_entry: collections.Mapping, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        value = config.get_or_default_value(section, option, meta_config_entry['default'])
        return int(value)

    def __load_bool_item(self, meta_config_entry: collections.Mapping, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        value = config.get_or_default_value(section, option, meta_config_entry['default'])
        return _convert_to_bool(value)

    def __load_inverse_bool_item(self, meta_config_entry: collections.Mapping, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        if not config.has(section, option):
            return meta_config_entry['default']
        else:
            value = config.get(section, option)
            return not _convert_to_bool(value)

    def __load_node(self, meta_config_entry: collections.Mapping, config: IniConfig):
        keys = set(meta_config_entry.keys()) - {'type'}
        node = dict()
        for key in keys:
            node[key] = self.__load_item(meta_config_entry[key], config)
        return node


class ConfigWriter(_ConfigLoaderWriter):
    def __init__(self, meta_config: (collections.Mapping, None) = None):
        super().__init__(
            {
                'string': self.__write_string_entry,
                'int': self.__write_int_entry,
                'bool': self.__write_bool_entry,
                'inverse-bool': self.__write_inverse_bool_entry,
                'node': self.__write_node,
            },
            meta_config
        )

    def write(self, new_config: collections.Mapping, config: IniConfig):
        for key, value in self.meta_config.items():
            if key in new_config:
                self.__write_item(value, new_config[key], config)

    def __write_item(self, meta_config_entry: collections.Mapping, new_config, config: IniConfig):
        return self._callbacks[meta_config_entry['type']](meta_config_entry, new_config, config)

    def __write_string_entry(self, meta_config_entry: collections.Mapping, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, new_config)

    def __write_int_entry(self, meta_config_entry: collections.Mapping, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, str(new_config))

    def __write_bool_entry(self, meta_config_entry: collections.Mapping, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, _convert_from_bool(new_config))

    def __write_inverse_bool_entry(self, meta_config_entry: collections.Mapping, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, _convert_from_bool(not new_config))

    def __write_node(self, meta_config_entry: collections.Mapping, new_config, config: IniConfig):
        for key, value in meta_config_entry.items():
            if key in new_config:
                self.__write_item(value, new_config[key], config)


class InvalidMetaConfig(Exception):
    pass


class ExtraKeys(InvalidMetaConfig):
    pass


class MissingKeys(InvalidMetaConfig):
    pass


class InvalidConfigType(InvalidMetaConfig):
    pass


def _convert_to_bool(val):
    if not val:
        return False
    if isinstance(val, bool):
        return val
    lowered = val.lower()
    return lowered == 'y' or lowered == 'yes' or lowered == 't' or lowered == 'true'


def _convert_from_bool(val):
    return 'yes' if val else 'no'
