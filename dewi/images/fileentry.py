# Copyright (C) 2017 Tóth, László Attila
# Distributed under the terms of GNU General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/
import os
import time


class FileEntry:
    SUFFIXES = ['KB', 'MB', 'GB', 'TB', 'PB']

    def __init__(self, orig_path: str, basename: str, uppercase_basename: str, mod_date: int, file_size: int):
        self.orig_path = orig_path
        self.basename = basename
        self.uppercase_basename = uppercase_basename
        self.mod_date = mod_date
        self.size = file_size
        self._mod_date = time.localtime(mod_date)

    @property
    def new_name(self) -> str:
        return os.path.join(self.target_dir_part, self.uppercase_basename)

    @property
    def target_dir_part(self) -> str:
        return os.path.join(*[
            str(self._mod_date.tm_year),
            '{:02d}'.format(self._mod_date.tm_mon),
            '{:02d}'.format(self._mod_date.tm_mday)
        ])

    def __str__(self):
        return str(self.__dict__)

    def print(self):
        print('Current self   : ' + self.orig_path)
        print(' -- directory  : ' + os.path.dirname(self.orig_path))
        print(' -- new name   : ' + self.uppercase_basename)
        print(' -- new path   : ' + self.new_name)
        print(' -- filesize   : ' + self._format_size())
        print(' -- mod.date   : ' + self._format_date())

    def _format_size(self):
        size = self.size / 1000
        suffix_id = 0

        while size > 1000:
            size /= 1000
            suffix_id += 1

        return f'{size} {self.SUFFIXES[suffix_id]} ({self.size})'

    def _format_date(self, ):
        return time.strftime('%Y-%m-%d %H:%M:%S - %A', self._mod_date)
