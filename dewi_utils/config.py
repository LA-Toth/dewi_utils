# Copyright 2009-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0
# vim: sts=4 ts=8 et ai


from dewi_core.config.iniconfig import IniConfig, convert_from_bool, convert_to_bool


class _ConfigLoaderWriter:
    def __init__(self, callbacks: dict, meta_config: dict | None = None):
        self._meta_config = meta_config or dict()
        self._callbacks = callbacks

    def set_meta_config(self, meta_config: dict):
        self.__check_config(meta_config)
        self._meta_config = meta_config

    def __check_config(self, meta_config: dict):
        for key in meta_config:
            self.__check_item_entry_with_type(meta_config, key)

    def __check_item_entry_with_type(self, meta_config_entry, key):
        if not isinstance(key, str):
            raise InvalidMetaConfig()
        if not isinstance(meta_config_entry[key], dict):
            raise InvalidMetaConfig()
        self.__check_item_entry(meta_config_entry[key])

    def __check_item_entry(self, meta_config_entry: dict):
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
    def meta_config(self) -> dict:
        return self._meta_config

    def _get_section_option(self, meta_config_entry):
        section, option = meta_config_entry['entry'].rsplit('.', 1)
        return section, option


class ConfigLoader(_ConfigLoaderWriter):
    def __init__(self, meta_config: dict | None = None):
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

    def load(self, config: IniConfig) -> dict:
        result = dict()
        for key, value in self.meta_config.items():
            result[key] = self.__load_item(value, config)

        return result

    def __load_item(self, meta_config_entry: dict, config: IniConfig):
        return self._callbacks[meta_config_entry['type']](meta_config_entry, config)

    def __load_string_item(self, meta_config_entry: dict, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        value = config.get_or_default_value(section, option, meta_config_entry['default'])
        return str(value)

    def __load_int_item(self, meta_config_entry: dict, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        value = config.get_or_default_value(section, option, meta_config_entry['default'])
        return int(value)

    def __load_bool_item(self, meta_config_entry: dict, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        value = config.get_or_default_value(section, option, meta_config_entry['default'])
        return convert_to_bool(value)

    def __load_inverse_bool_item(self, meta_config_entry: dict, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        if not config.has(section, option):
            return meta_config_entry['default']
        else:
            value = config.get(section, option)
            return not convert_to_bool(value)

    def __load_node(self, meta_config_entry: dict, config: IniConfig):
        keys = set(meta_config_entry.keys()) - {'type'}
        node = dict()
        for key in keys:
            node[key] = self.__load_item(meta_config_entry[key], config)
        return node


class ConfigWriter(_ConfigLoaderWriter):
    def __init__(self, meta_config: dict | None = None):
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

    def write(self, new_config: dict, config: IniConfig):
        for key, value in self.meta_config.items():
            if key in new_config:
                self.__write_item(value, new_config[key], config)

    def __write_item(self, meta_config_entry: dict, new_config, config: IniConfig):
        return self._callbacks[meta_config_entry['type']](meta_config_entry, new_config, config)

    def __write_string_entry(self, meta_config_entry: dict, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, new_config)

    def __write_int_entry(self, meta_config_entry: dict, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, str(new_config))

    def __write_bool_entry(self, meta_config_entry: dict, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, convert_from_bool(new_config))

    def __write_inverse_bool_entry(self, meta_config_entry: dict, new_config, config: IniConfig):
        section, option = self._get_section_option(meta_config_entry)
        config.set(section, option, convert_from_bool(not new_config))

    def __write_node(self, meta_config_entry: dict, new_config, config: IniConfig):
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
