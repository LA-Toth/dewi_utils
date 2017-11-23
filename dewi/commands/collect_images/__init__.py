# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import os
import sqlite3
import subprocess
import typing

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin
from dewi.images.filedb import FileDatabase
from dewi.images.fileentry import FileEntry


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

        return ext not in ['.jpg', '.jpeg', '.cr2', '.mov', '.thm', '.mp4']

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
    description = "Collect photos - or other files - into SQLite database with timestamp, size and MD5 checksum. " \
                  "Use 'select-images' for next step."

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


ImageCollectorPlugin = CommandPlugin.create(ImageCollectorCommand)
