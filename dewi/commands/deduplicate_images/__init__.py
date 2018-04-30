# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import os
import shutil
import subprocess
import time
import typing

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin
from dewi.images.filedb import FileDatabase
from dewi.images.fileentry import FileEntry
from dewi.images.filtering import Filter, FilterResult


class DeduplicatorConfig:
    def __init__(self):
        self.filter_filename: str = None
        self.sqlite_filename: str = None
        self.result_sqlite_filename: str = None
        self.main_target_dir: str = None
        self.log_file: str = None

        # On macOS mount points parent directory is /Volumes.
        # The typical system root is both / (as directory) and /Volumes/Macintosh HD (as symlink).
        # I don't know how this should work in a (customized) Linux, maybe the symlinks are the solution.
        # FIXME: not used in first implementation
        self.mount_points_parent_directory: str = '/Volumes'

        self.dry_run = False
        self.exiftool = 'exiftool-5.26'


class Step:
    def __init__(self, func: callable, help: str):
        self.func = func
        self.help = help


class ImageDeduplicator:
    MOD_DATE_MAX_DIFF = 5  # seconds between mtime and EXIF date/time original entry

    def __init__(self, config: DeduplicatorConfig):
        self.config = config
        self.filter = Filter(self.config.filter_filename)
        self.db = FileDatabase(self.config.sqlite_filename)
        self.log = open(self.config.log_file, 'a')
        self.moved = dict()
        self._selected_for_move: typing.List[FileEntry] = list()
        self._selected_hash = dict()  # (uppercase-name, file-size, date, checksum) => true
        self._count = dict(n=0, r=0, d=0)  # new, reject, dup
        self._print_count = False

        self._target_entries: typing.Dict[str, FileEntry] = dict()

        self.steps: typing.List[Step] = [
            Step(self._read_from_db, 'Read file information from database and select accepted images'),
            Step(self._make_file_names_unique, 'Prepare file information as unique target names'),
            Step(self._store_file_path_map, 'Store (cache) file mapping information into the DB'),
            Step(self._copy_files, 'Copy files')
        ]

    def run(self):
        self._run_steps()
        self._print_stats()

    def _run_steps(self):
        count = len(self.steps)
        current = 0

        for step in self.steps:
            current += 1
            print(f' * Step {current} of {count}: {step.help}')
            self.log.write(f' * Step {current} of {count}: {step.help}\n')
            step.func()

    def _read_from_db(self):
        if self.db.has_new_path_info():
            return

        self._print_count = True

        for entry in self.db.iterate_photo_entries():
            if entry.key in self._selected_hash:
                self._count['d'] += 1
                continue

            result = self.filter.decide(entry)
            if result == FilterResult.ACCEPT:
                self._select_entry(entry)
            else:
                self._count['r'] += 1

    def _select_entry(self, entry: FileEntry) -> bool:
        self._selected_for_move.append(entry)
        self._selected_hash[entry.key] = True
        self._count['n'] += 1
        return True

    def _make_file_names_unique(self):
        if self.db.has_new_path_info():
            return

        for entry in self._selected_for_move:
            self._add_entry_to_fs(entry)

    def _add_entry_to_fs(self, entry: FileEntry):
        full_path = os.path.join(self.config.main_target_dir, entry.new_name)

        if full_path not in self._target_entries:
            self._target_entries[full_path] = entry

        elif entry.checksum == self._target_entries[full_path].checksum:
            # This is likely the same file, even if the time stamp differs. This can occur
            # when importing into iPhoto (eg. before 2010!), or
            # when copying to different machines.
            # I saw such issue on Mac using Midnight Commander as FTP machine: the server's file timestamp
            # depends on the current time zone (more preciesly on daylight saving time enabled or not): CET vs. CEST

            self.log.write('\n** CHEKSUM DUP: (new):' + entry.orig_path + ' (old):' + self._target_entries[
                full_path].orig_path + ' ' + full_path + '\n')
            entry.print(self.log)
            self._target_entries[full_path].print(self.log)

            if not os.path.exists(entry.orig_path):
                self._target_entries[full_path] = entry
                print('Choosing NEW entry (missing original file)', file=self.log)

            elif os.path.exists(entry.orig_path):
                # The modification date of the entry can be exactly the same as in the EXIF data
                # or it has to be within a few seconds, probably because it takes time to write to the memory card.
                # I saw mostly 1 second difference, sometimes 2 seconds.
                # It seems to be a good start to use 5 seconds treshold.
                try:
                    date_line = subprocess.check_output(
                        [self.config.exiftool, '-t', self._target_entries[full_path].orig_path]).decode('UTF-8')
                    date_old = \
                        [x.split('\t')[1] for x in date_line.splitlines(keepends=False)
                         if x.startswith('Date/Time Original')]
                except subprocess.CalledProcessError:
                    date_old = []

                if not date_old:
                    print('Keeping original as date and time information is not available for OLD', file=self.log)
                    return

                date_old = date_old[0]
                date_old_ts = time.mktime(time.strptime(date_old, '%Y:%m:%d %H:%M:%S'))

                print(f'(old) date in exif data of path \'{self._target_entries[full_path].orig_path}\' is {date_old}',
                      file=self.log)

                if date_old != self._target_entries[full_path].date_as_exif_data and abs(
                                date_old_ts - self._target_entries[full_path].mod_date) > self.MOD_DATE_MAX_DIFF:
                    try:
                        date_line = subprocess.check_output([self.config.exiftool, '-t', entry.orig_path]).decode(
                            'UTF-8')
                        date_new = \
                            [x.split('\t')[1] for x in date_line.splitlines(keepends=False)
                             if x.startswith('Date/Time Original')]
                    except subprocess.CalledProcessError:
                        date_new = []

                    if not date_new:
                        print('Keeping original as date and time information is not available for NEW', file=self.log)
                        return

                    date_new = date_new[0]
                    date_new_ts = time.mktime(time.strptime(date_new, '%Y:%m:%d %H:%M:%S'))
                    print(f'(new) date in exif data of path \'{entry.orig_path}\' is {date_old}', file=self.log)

                    if date_new == entry.date_as_exif_data or abs(
                                    date_new_ts - entry.mod_date) < self.MOD_DATE_MAX_DIFF:
                        self._target_entries[full_path] = entry
                        print('Choosing NEW entry (almostmatching date and time)', file=self.log)
                    else:
                        print('Keeping original / OLD', file=self.log)

                else:
                    print('Keeping original / OLD as EXIF timestamp and file mtime (almost) matches', file=self.log)

        else:
            print(f"Duplicated file entry detected on path: {full_path}")
            self.log.write(f"\n*** Duplicated file entry detected on path: {full_path}\n")
            entry.print(self.log)
            self._target_entries[full_path].print(self.log)
            base, ext = os.path.splitext(full_path)

            i = 1
            new_name = f'{base}_{i}{ext}'
            while new_name in self._target_entries:
                i += 1
                new_name = f'{base}_{i}{ext}'

            self._target_entries[new_name] = entry
            self.log.write(f'{self._target_entries[full_path].orig_path} became {new_name}\n')

    def _store_file_path_map(self):
        if self.db.has_new_path_info():
            return

        for path, entry in self._target_entries.items():
            self.db.insert_new_path(entry.id, path)

        self.db.commit()

    def _copy_files(self):
        count = len(self.config.main_target_dir)
        for path, entry in self.db.iterate_target_path_entries():
            suffix = path[count:]
            if suffix[0] == os.path.sep:
                suffix = suffix[1:]

            (year, month, day, remaining) = suffix.split(os.path.sep, 3)
            path = os.path.join(self.config.main_target_dir, year, f'{year}-{month}', f'{year}-{month}-{day}',
                                remaining)
            mode = 'SKIP' if os.path.exists(path) else 'COPY'
            print(f'{mode}: {entry.orig_path} -> {path}', file=self.log)

            if not self.config.dry_run:
                if not os.path.exists(entry.orig_path):
                    print(f'SKIP MISSING SOURCE FILE: {entry.orig_path}', file=self.log)
                elif not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), 0o755, exist_ok=True)
                    shutil.copy2(entry.orig_path, path)
                else:
                    print(f'SKIP EXISTING TARGET {path} - SOURCE FILE: {entry.orig_path}', file=self.log)

    def _print_stats(self):
        if not self._print_count:
            return

        print('Stats: ')
        print(f'* NEW      : {self._count["n"]}')
        print(f'* DUP      : {self._count["d"]}')
        print(f'* REJECTED : {self._count["r"]}')
        print(f'# DONE     : ' + str(self._count['n'] + self._count['d'] + self._count['r']))


class ImageDeduplicatorCommand(Command):
    name = 'deduplicate-images'
    aliases = ['dedup-images']
    description = "Select photos - or files"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--filter', '--filter-file', dest='filter_file', required=True,
            help='File of filters')

        parser.add_argument(
            '--sql', '--sqlite-db', '--db', '-d', dest='db', required=True,
            help='SQLite database to read and update')

        parser.add_argument('--target-directory', dest='target', required=True,
                            help='Target directory to store unique files')

        parser.add_argument('--log-file', dest='log_file', required=True,
                            help='Log file for detailed run')

        parser.add_argument('--dry-run', '-n', dest='dry_run', action='store_true',
                            help='Do change file system, just print what would do')

    def run(self, args: argparse.Namespace):
        config = DeduplicatorConfig()
        config.filter_filename = args.filter_file
        config.sqlite_filename = args.db
        config.main_target_dir = args.target
        config.dry_run = args.dry_run
        config.log_file = args.log_file

        sorter = ImageDeduplicator(config)
        sorter.run()


ImageDeduplicatorPlugin = CommandPlugin.create(ImageDeduplicatorCommand)
