# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin
from dewi.images.filedb import FileDatabase
from dewi.images.fileentry import FileEntry
from dewi.images.filtering import Filter, FilterResult, ProcessInputToFilter


class ImageSelector:
    INTERACTIVE = True

    def __init__(self, filter_filename: str, sqlite_filename: str):
        self.filter_filename = filter_filename
        self.filter = Filter(filter_filename)
        self.sqlite_filename = sqlite_filename
        self.db = FileDatabase(sqlite_filename)
        self.read_to_filter = ProcessInputToFilter(self.filter, self.__class__.__name__)
        self.moved = dict()
        self._selected_for_move = list()
        self._selected_hash = dict()  # (uppercase-name, file-size, date, checksum) => true
        self._count = dict(n=0, r=0, d=0, s=0)  # new, reject, dup, skipped

    def run(self):
        set_quit = False
        for entry in self.db.iterate_photo_entries():
            if set_quit:
                break

            if entry.key in self._selected_hash:
                self._count['d'] += 1
                continue

            self.read_to_filter.set_entry(entry)
            result = FilterResult.UNSPECIFIED

            while result == FilterResult.UNSPECIFIED:
                result = self.filter.decide(entry)
                if result == FilterResult.UNSPECIFIED:
                    if self.INTERACTIVE:
                        if not self.read_to_filter.read_and_process_line():
                            set_quit = True
                        break
                    else:
                        self._count['s'] += 1
                        result = FilterResult.ACCEPT  # doesn't matter
                else:
                    if result == FilterResult.ACCEPT:
                        self._select_entry(entry)
                    else:
                        self._count['r'] += 1

            if set_quit:
                break

        self._print_stats()

    def _select_entry(self, entry: FileEntry) -> bool:
        self._selected_for_move.append(entry)
        self._selected_hash[entry.key] = True
        self._count['n'] += 1
        return True

    def _print_stats(self):
        print('Stats: ')
        print(f'* NEW      : {self._count["n"]}')
        print(f'* DUP      : {self._count["d"]}')
        print(f'* REJECTED : {self._count["r"]}')
        print(f'* SKIP     : {self._count["s"]}')
        print(f'# DONE     : ' + str(self._count['n'] + self._count['d'] + self._count['r']))
        print(f'# TOTAL    : ' + str(self._count['n'] + self._count['d'] + self._count['r'] + self._count['s']))


class ImageSelectorCommand(Command):
    name = 'select-images'
    aliases = ['image-selector']
    description = "Select photos - or files collected by 'collect-images' and create a filter file in YAML format. " \
                  "Use 'dedup-images' for next step."

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--filter', '--filter-file', dest='filter_file', required=True,
            help='File of filters')

        parser.add_argument(
            '--sql', '--sqlite-db', '--db', '-d', dest='db', required=True,
            help='SQLite database to read')

    def run(self, args: argparse.Namespace):
        sorter = ImageSelector(args.filter_file, args.db)
        sorter.run()


ImageSelectorPlugin = CommandPlugin.create(ImageSelectorCommand)
