# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import os
import subprocess
import time
import typing

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin
from dewi.images.filedb import FileDatabase
from dewi.images.fileentry import FileEntry


class SafeEraserConfig:
    def __init__(self):
        self.sqlite_filename: str = None
        self.log_file: str = None
        self.dry_run = False
        self.exiftool = 'exiftool-5.26'


class Step:
    def __init__(self, func: callable, help: str):
        self.func = func
        self.help = help


class SafeEraser:
    MOD_DATE_MAX_DIFF = 5  # seconds between mtime and EXIF date/time original entry

    def __init__(self, config: SafeEraserConfig):
        self.config = config
        self.db = FileDatabase(self.config.sqlite_filename)
        self.log = open(self.config.log_file, 'a')
        self.copied: typing.Dict[str, FileEntry] = dict()
        self.safe_to_delete = list()
        self.known_rows = set()
        self.copied_hashes = dict()
        self.copied_hashes_without_date = dict()

        self.steps: typing.List[Step] = [
            Step(self._read_from_db, 'Read copied file entries'),
            Step(self._find_duplicates, 'Find duplicates of copied files from DB'),
            Step(self._erase_duplicates, 'Remove duplicates from file sytem'),
        ]

    def run(self):
        self._run_steps()

    def _run_steps(self):
        count = len(self.steps)
        current = 0

        for step in self.steps:
            current += 1
            print(f' * Step {current} of {count}: {step.help}')
            self.log.write(f' * Step {current} of {count}: {step.help}\n')
            step.func()

    def _read_from_db(self):
        for path, entry in self.db.iterate_target_path_entries():
            parts = path.split(os.path.sep)
            # parts is like (a, directory, name, to, somewhere, year, month, day, filename)
            # We drop year and remaining fields by now
            prefix = os.path.sep.join(parts[:-4])
            year, month, day, filename = parts[-4:]
            real_path = os.path.join(prefix, year, f'{year}-{month}', f'{year}-{month}-{day}', filename)
            if os.path.exists(real_path):
                print(f'Found {real_path}, original can be deleted from {entry.orig_path}', file=self.log)

                self.copied[real_path] = entry
                self.safe_to_delete.append(entry.orig_path)
                self.known_rows.add(entry.id)
                self.copied_hashes[entry.key] = entry
                self.copied_hashes_without_date[entry.key_without_date] = entry

            else:
                print(f'*** NOT Found {real_path}, original (and dups) CANNNOT be deleted from {entry.orig_path}',
                      file=self.log)

        print(f'Found {len(self.safe_to_delete)} files for deletion')
        print(f'Found {len(self.safe_to_delete)} files for deletion', file=self.log)

    def _find_duplicates(self):
        count = 0
        for entry in self.db.iterate_photo_entries():
            if entry.id in self.known_rows:
                continue

            if not os.path.exists(entry.orig_path):
                self.known_rows.add(entry.id)
                continue

            if entry.key in self.copied_hashes:
                print(f'! DUPLICATE found at {entry.orig_path}, original: {self.copied_hashes[entry.key].orig_path}',
                      file=self.log)
                self.known_rows.add(entry.id)
                self.safe_to_delete.append(entry.orig_path)
                count += 1
            elif entry.key_without_date in self.copied_hashes_without_date:
                try:
                    date_line = subprocess.check_output([self.config.exiftool, '-t', entry.orig_path]).decode(
                        'UTF-8')
                    date_new = \
                        [x.split('\t')[1] for x in date_line.splitlines(keepends=False)
                         if x.startswith('Date/Time Original')]
                except subprocess.CalledProcessError:
                    date_new = []

                if not date_new:
                    print(f'** Missing exif date info in file {entry.orig_path}', file=self.log)
                    continue

                date_new = date_new[0]
                date_new_ts = time.mktime(time.strptime(date_new, '%Y:%m:%d %H:%M:%S'))

                if abs(date_new_ts - entry.mod_date) < self.MOD_DATE_MAX_DIFF or \
                                abs(abs(date_new_ts - entry.mod_date) - 3600) < self.MOD_DATE_MAX_DIFF:
                    print(
                        f'. DUPLICATE found at {entry.orig_path}, original: ' + self.copied_hashes_without_date[
                            entry.key_without_date].orig_path + \
                        f' date diff is {entry.mod_date - date_new_ts}',
                        file=self.log)
                    self.known_rows.add(entry.id)
                    self.safe_to_delete.append(entry.orig_path)
                    count += 1

        print(f'Found {count} more files for deletion')
        print(f'Found {count} more files for deletion', file=self.log)

    def _erase_duplicates(self):
        print(f'Deleting {len(self.safe_to_delete)} files')
        print(f'Deleting {len(self.safe_to_delete)} files', file=self.log)
        count = 0
        missing = 0
        for path in self.safe_to_delete:
            if self.config.dry_run or os.path.exists(path):
                print(f'DELETE {path}', file=self.log)
                if not self.config.dry_run:
                    try:
                        os.unlink(path)
                    except Exception as e:
                        print(f'Exception occurred; class={e.__class__.__name__}, msg={e}, path={path}')
                        print(f'Exception occurred; class={e.__class__.__name__}, msg={e}, path={path}', file=self.log)

                count += 1
            else:
                print(f'ALREADY DELETED {path}', file=self.log)
                missing += 1

        print(f'Deleted {count} of {len(self.safe_to_delete)} files; already removed (missing) {missing} files')
        print(f'Deleted {count} of {len(self.safe_to_delete)} files; already removed (missing) {missing} files',
              file=self.log)


class SafeEraserCommand(Command):
    name = 'safe-delete-images'
    description = "Erase duplicated photos - or files that successfully copied to their target location"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--sql', '--sqlite-db', '--db', '-d', dest='db', required=True,
            help='SQLite database to read and update')

        parser.add_argument('--log-file', dest='log_file', required=True,
                            help='Log file for detailed run')

        parser.add_argument('--dry-run', '-n', dest='dry_run', action='store_true',
                            help='Do change file system, just print what would do')

    def run(self, args: argparse.Namespace):
        config = SafeEraserConfig()
        config.sqlite_filename = args.db
        config.dry_run = args.dry_run
        config.log_file = args.log_file

        sorter = SafeEraser(config)
        sorter.run()


SafeEraserPlugin = CommandPlugin.create(SafeEraserCommand)
