# Copyright 2016 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import re


class Parser(object):
    def __init__(self):
        self.__pattern = re.compile(
            r'^(?P<date>\d+-\d+-\d+)T(?P<time>\d\d:\d\d:\d\d)\+[0-9]+:[0-9]+ ' +
            r'(?P<host>[-_.0-9a-zA-Z]+) (?P<app>[-_./0-9a-zA-Z]+)(\[(?P<pid>[0-9]+)\])?: (?P<msg>.*)$'
        )

        self._date_time_pattern = re.compile(
            r'^(?P<date>\d+-\d+-\d+)T(?P<time>\d\d:\d\d:\d\d)\+[0-9]+:[0-9]+'
        )

    def parse_date(self, line):
        parsed = self._date_time_pattern.match(line)

        if not parsed:
            print(line)
            return None
        else:
            return parsed

    def parse(self, line):
        parsed = self.__pattern.match(line)

        if not parsed:
            return None
        else:
            return parsed
