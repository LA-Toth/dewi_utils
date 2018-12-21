# Copyright 2017-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


import argparse
import os
import sqlite3
import subprocess
import time
import typing

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin


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
        year, month, day = [
            str(self._mod_date.tm_year),
            '{:02d}'.format(self._mod_date.tm_mon),
            '{:02d}'.format(self._mod_date.tm_mday)]
        return os.path.join(year, f'{year}-{month}', f'{year}-{month}-{day}')

    def __str__(self):
        return str(self.__dict__)


class FileDatabase:
    def __init__(self, filename: str):
        self.filename = filename
        self.in_memory = filename == ':memory:'

        self._conn = sqlite3.connect(self.filename)
        self._ensure_tables()

    def __del__(self):
        self._conn.close()

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
        c.execute('''CREATE INDEX IF NOT EXISTS photo_file_info_name_size_date
                            ON photo_file_info
                            (upper_basename, filesize, mod_date)
                     ''')
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS photo_file_info_uniq_entries
                            ON photo_file_info
                            (upper_basename, filesize, mod_date, checksum)
                     ''')
        self._conn.commit()

    def query_fileinfo(self, file_entry: FileEntry):
        c = self._conn.execute('SELECT rowid, * FROM photo_file_info'
                               ' WHERE upper_basename=? AND filesize=? AND mod_date=?',
                               [
                                   file_entry.uppercase_basename,
                                   file_entry.size,
                                   file_entry.mod_date,
                               ]
                               )

        return c.fetchone()

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

    def add_checksum(self, rowid: int, checksum: str):
        self._conn.execute('UPDATE photo_file_info SET checksum = ? WHERE rowid=?', [checksum, rowid])


class PhotoSorter:
    def __init__(self, source_dir: str, target_dir: str, pretend: bool = False):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.pretend = pretend
        self.db = FileDatabase(':memory:')
        self.moved = dict()
        self._selected_for_move = list()

    def run(self):
        for x in self._walk():
            # print(x.orig_path)
            from_db = self.db.query_fileinfo(x)
            if not from_db:
                self.db.insert(x)
                self._selected_for_move.append(x)
            else:
                hash_x = self._checksum(x.orig_path)
                if from_db[6]:
                    hash_other = from_db[6]
                else:
                    hash_other = self._checksum(from_db[1])
                if hash_x == hash_other:
                    print('Skip {} -- already found: {}'.format(x.orig_path, from_db[1]))
                else:
                    self.db.add_checksum(from_db[1], hash_other)
                    self.db.insert(x, hash_x)

        self._move()
        return 0

    def _walk(self) -> typing.Iterable[FileEntry]:
        for root, _, files in os.walk(self.source_dir):
            for name in files:
                full_path = os.path.join(root, name)

                if self._skip_file(name):
                    print('Skip: ' + full_path)
                    continue

                yield FileEntry(full_path, name, name.upper(), *self._mod_date_and_file_size(full_path))

    def _skip_file(self, name: str) -> bool:
        _, ext = os.path.splitext(name.lower())

        return ext not in ['.jpg', '.jpeg', '.cr2', '.mov', '.mp4', '.thm']

    def _mod_date_and_file_size(self, full_path: str) -> typing.Tuple[int, int]:
        f = os.stat(full_path)

        return int(f.st_mtime), f.st_size

    def _checksum(self, filename: str) -> str:
        r = subprocess.check_output(['md5sum', filename])
        return r.decode('UTF-8').split(' ')[0]

    def _move(self):
        for entry in self._selected_for_move:
            self._move_entry(entry)

    def _move_entry(self, entry: FileEntry):
        target_path = os.path.join(self.target_dir, entry.new_name)
        if target_path not in self.moved or (not self.pretend and not os.path.exists(target_path)):
            print("Moving {} to {}".format(entry.orig_path, target_path))
            self.moved[target_path] = True

            if not self.pretend:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                os.rename(entry.orig_path, target_path)
        else:
            base, ext = os.path.splitext(target_path)
            i = 1
            print("Target file already exists: " + target_path)
            while True:
                new_file_name = '{} {}{}'.format(base, i, ext)
                print("Try #{}: {}".format(i, new_file_name))
                if new_file_name not in self.moved:
                    print("Moving {} to {}".format(entry.orig_path, new_file_name))
                    self.moved[new_file_name] = True
                    if not self.pretend:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        os.rename(entry.orig_path, new_file_name)
                    break
                else:
                    i += 1


class PhotoSorterCommand(Command):
    name = 'sortphotos'
    aliases = ['sort-photos', 'sort-files', 'sortfiles', 'filesort']
    description = "Sort photos - or files - by its modification name and detect duplicates."

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '-s', '--source', '--source-directory', dest='source_dir', required=True,
            help='Source Directory of files (photos) to be checked and cleaned')
        parser.add_argument(
            '-d', '--destination', '--destination-directory', dest='dest_dir', required=True,
            help='Target Root Directory - Files will be copied to $TARGET/$YEAR/$YEAR-$MONTH/$YEAR-$MONTH-$DAY')
        parser.add_argument(
            '--pretend', dest='pretend', default=False, action='store_true',
            help='Pretend only, but do not move files')

    def run(self, args: argparse.Namespace):
        sorter = PhotoSorter(args.source_dir, args.dest_dir, args.pretend)
        sorter.run()


PhotoSorterPlugin = CommandPlugin.create(PhotoSorterCommand)
