# Copyright (c) 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import argparse
import collections
import os
import sqlite3
import subprocess
import time
import typing

from dewi.core.command import Command
from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class FileEntry:
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


class FileDatabase:
    def __init__(self, filename: str):
        self.filename = filename
        self.in_memory = filename == ':memory:'

        self._conn = sqlite3.connect(self.filename)
        self._ensure_tables()
        self._changed = False

    def _ensure_tables(self):
        c = self._conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS photo_file_info (
                            orig_filename text,
                            mod_date_as_dirname text,
                            upper_basename text,
                            filesize integer,
                            mod_date integer,
                            checksum text
                     )''')

        c.execute('''CREATE INDEX IF NOT EXISTS photo_orig_file_name_idx ON photo_file_info (orig_filename)''')
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS photo_file_info_uniq_rows
                                  ON photo_file_info
                                  (orig_filename, upper_basename, filesize, mod_date, checksum)
                           ''')
        self._conn.commit()

    def close(self):
        self.commit()
        self._conn.close()

    def commit(self):
        if self._changed:
            self._conn.commit()
            self._changed = False

    def insert(self, file_entry: FileEntry, checksum: typing.Optional[str] = None):
        self._conn.execute('INSERT INTO photo_file_info'
                           ' VALUES (?,?,?, ?,?,?)',
                           [
                               file_entry.orig_path,
                               file_entry.target_dir_part,
                               file_entry.uppercase_basename,
                               file_entry.size,
                               file_entry.mod_date,
                               checksum or '',
                           ])
        self._changed = True

    def iterate(self):
        c = self._conn.cursor()
        for row in c.execute('SELECT * FROM photo_file_info ORDER BY orig_filename'):
            yield row

    def __contains__(self, item: str):
        c = self._conn.cursor()
        t = (item,)
        return c.execute('SELECT orig_filename FROM photo_file_info WHERE orig_filename=?', t).fetchone() is not None


class ImageCollector:
    def __init__(self, source_dir: str, sqlite_filename: str, pretend: bool = False):
        self.source_dir = source_dir
        self.sqlite_filename = sqlite_filename
        self.pretend = pretend
        self.db = FileDatabase(sqlite_filename)
        self.moved = dict()
        self._selected_for_move = list()

    def run(self):
        for x in self._walk():
            self._process(x)

        self.db.close()
        return 0

    def _walk(self) -> typing.Iterable[FileEntry]:
        for root, dirs, files in os.walk(self.source_dir):
            print('Processing: {}'.format(root))
            for name in files:
                full_path = os.path.join(root, name)

                if self._skip_file(name):
                    # print('Skip: ' + full_path)
                    continue

                yield FileEntry(full_path, name, name.upper(), *self._mod_date_and_file_size(full_path))
            self.db.commit()

    def _skip_file(self, name: str) -> bool:
        _, ext = os.path.splitext(name.lower())

        return ext not in ['.jpg', '.jpeg', '.cr2', '.mov', '.thm']

    def _mod_date_and_file_size(self, full_path: str) -> typing.Tuple[int, int]:
        f = os.stat(full_path)

        return int(f.st_mtime), f.st_size

    def _checksum(self, filename: str) -> str:
        r = subprocess.check_output(['md5sum', filename])
        return r.decode('UTF-8').split(' ')[0]

    def _process(self, entry: FileEntry):
        if entry.orig_path in self.db:
            return
        try:
            self.db.insert(entry, self._checksum(entry.orig_path))
        except sqlite3.IntegrityError as e:
            print('File {} is already processed. Error: {}'.format(entry.orig_path, str(e)))


class ImageCollectorCommand(Command):
    name = 'collect-images'
    aliases = ['image-collector']
    parser_description = "Sort photos - or files - by its modification name and detect duplicates."

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '-s', '--source', '--source-directory', dest='source_dir', required=True,
            help='Source Directory of files (photos) to be checked and cleaned')
        parser.add_argument(
            '--sql', '--sqlite-db', '--db', '-d', dest='db', required=True,
            help='SQLite database to store data')

    def run(self, args: argparse.Namespace):
        sorter = ImageCollector(args.source_dir, args.db)
        sorter.run()


class ImageCollectorPlugin(Plugin):
    def get_description(self) -> str:
        return 'Command plugin of: ' + ImageCollectorCommand.description

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}

    def load(self, c: Context):
        c['commands'].register_class(ImageCollectorCommand)
