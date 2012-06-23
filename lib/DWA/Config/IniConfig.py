# vim: sts=4 ts=8 et ai

import configparser


class IniConfig(object):

    def __init__(self):
        self.__config_file = None
        self.__parser = configparser.RawConfigParser()

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
        self.__config_file = cfgfile
        self.__parser.read(self.__config_file)

    def write(self):
        file_ = open(self.__config_file, 'wb')
        self.__parser.write(file_)
        file_.close()

    def close(self):
        pass

    def has(self, section, option):
        section = self.__section_from_dotted(section)
        return self.__parser.has_option(section, option);

    def set(self, section, option, value):
        section = self.__section_from_dotted(section)
        if not self.__parser.has_section(section):
            self.__parser.add_section(section)
        self.__parser.set(section, option, value)

    def get(self, section, option):
        section = self.__section_from_dotted(section)
        if not self.__parser.has_section(section):
            return None
        try:
            return self.__parser.get(section, option)
        except configparser.NoOptionError:
            return None

    def get_or_default_value(self, section, option, default_value):
        res = self.get(section, option)
        return res if res != None else default_value

    def remove(self, section, option):
        section = self.__section_from_dotted(section)
        if not self.__parser.has_section(section): return
        if not self.__parser.has_option(section, option): return
        self.__parser.remove_option(section, option)

    def get_options(self, section):
        section = self.__section_from_dotted(section)
        if not self.__parser.has_section(section):
            return []
        else:
            return self.__parser.options(section)

    def get_sections(self):
        return [self.__section_to_dotted(s) for s in self.__parser.sections()]
