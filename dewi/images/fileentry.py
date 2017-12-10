# Copyright 2017 Tóth, László Attila
# Distributed under the terms of the GNU Lesser General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

import os
import sys
import time
import typing


class FileEntry:
    SUFFIXES = ['KB', 'MB', 'GB', 'TB', 'PB']

    def __init__(self, orig_path: str, basename: str, uppercase_basename: str, mod_date: int, file_size: int,
                 checksum: typing.Optional[str] = None, id: typing.Optional[int] = None):
        self.orig_path = orig_path
        self.basename = basename
        self.uppercase_basename = uppercase_basename
        self.mod_date = mod_date
        self.size = file_size
        self.checksum = checksum
        self.id = id
        self._mod_date_ = None

    @property
    def _mod_date(self):
        if self._mod_date_ is None:
            self._mod_date_ = time.localtime(self.mod_date)

        return self._mod_date_

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

    @property
    def date_as_exif_data(self):
        return time.strftime('%Y:%m:%d %H:%M:%S', self._mod_date)

    @property
    def key(self):
        return (self.uppercase_basename, self.size, self.mod_date, self.checksum)

    @property
    def key_without_date(self):
        return (self.uppercase_basename, self.size, self.checksum)

    def __str__(self):
        return str(self.__dict__)

    def print(self, output_file=None):
        if not output_file:
            output_file = sys.stdout
        print('Entry Details  : ' + self.orig_path, file=output_file)
        print(' -- directory  : ' + os.path.dirname(self.orig_path), file=output_file)
        print(' -- new name   : ' + self.uppercase_basename, file=output_file)
        print(' -- new path   : ' + self.new_name, file=output_file)
        print(' -- filesize   : ' + self._format_size(), file=output_file)
        print(' -- mod.date   : ' + self._format_date(), file=output_file)
        print(' -- as EXIF    : ' + self.date_as_exif_data, file=output_file)

        if self.checksum:
            print(' -- cheksum    : ' + self.checksum, file=output_file)

    def _format_size(self):
        size = self.size / 1000
        suffix_id = 0

        while size > 1000:
            size /= 1000
            suffix_id += 1

        return f'{size} {self.SUFFIXES[suffix_id]} ({self.size})'

    def _format_date(self, ):
        return time.strftime('%Y-%m-%d %H:%M:%S - %A', self._mod_date)
