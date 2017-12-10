# Copyright 2017 Tóth, László Attila
# Distributed under the terms of the GNU Lesser General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

import argparse
import atexit
import collections
import enum
import os
import re
import shlex
import subprocess
import sys
import typing

import readline
import yaml

from dewi.config.config import Config
from dewi.images.fileentry import FileEntry


class FilterResult(enum.Enum):
    UNSPECIFIED = 'accept-or-reject'
    ACCEPT = 'accept'
    REJECT = 'reject'


class Filter:
    def __init__(self, filename: str):
        self._filename = filename
        self._config = Config()
        self._modified = False
        self.reload()

    def reload(self):
        if os.path.exists(self._filename):
            with open(self._filename) as f:
                self._config.overwrite_config(yaml.load(f))

    def __del__(self):
        self.save()

    def save(self):
        if self._modified:
            with open(self._filename, 'w') as f:
                self._config.dump(f)

    @property
    def filename(self) -> str:
        return self._filename

    def print(self):
        self._config.dump(sys.stdout)

    def add_accept_file_pattern(self, pattern: str):
        self._config.append('files.pattern.accept', pattern)
        self._modified = True

    def add_reject_file_pattern(self, pattern: str):
        self._config.append('files.pattern.reject', pattern)
        self._modified = True

    def add_accept_dir_path_part(self, partial_path: str):
        self._config.append('dirs.partial_path.accept', partial_path)
        self._modified = True

    def add_reject_dir_path_part(self, partial_path: str):
        self._config.append('dirs.partial_path.reject', partial_path)
        self._modified = True

    def add_reject_subdir_name(self, name: str):
        self._config.append('dirs.subdir.reject', name)
        self._modified = True

    def add_accept_subdir_name(self, name: str):
        self._config.append('dirs.subdir.accept', name)
        self._modified = True

    def add_accept_full_path(self, path: str):
        self._config.append('dirs.path.accept', path)
        self._modified = True

    def add_reject_full_path(self, path: str):
        self._config.append('dirs.path.reject', path)
        self._modified = True

    def decide(self, entry: FileEntry) -> FilterResult:
        accepted_dir = self._decide_dir_is_accepted(entry)
        return self._decide_file_is_accepted(entry, accepted_dir)

    def _decide_dir_is_accepted(self, entry: FileEntry) -> typing.Optional[bool]:
        directory = os.path.dirname(entry.orig_path)
        dir_parts = directory.split(os.path.sep)
        accepted_dir = None
        if directory in (self._config.get('dirs.path.accept') or []):
            accepted_dir = True
        else:
            for part in (self._config.get('dirs.subdir.accept') or []):
                if part in dir_parts:
                    accepted_dir = True
                    break

            if accepted_dir is None:
                for part in (self._config.get('dirs.partial_path.accept') or []):
                    if part in directory:
                        accepted_dir = True
                        break

            if directory in (self._config.get('dirs.path.reject') or []):
                accepted_dir = False

            if accepted_dir or accepted_dir is None:
                for part in (self._config.get('dirs.partial_path.reject') or []):
                    if part in directory:
                        accepted_dir = False
                        break

            if accepted_dir or accepted_dir is None:
                for part in (self._config.get('dirs.subdir.reject') or []):
                    if part in dir_parts:
                        accepted_dir = False
                        break

                if (accepted_dir or accepted_dir is None) and directory in (self._config.get('dirs.path.reject') or []):
                    accepted_dir = False

        return accepted_dir

    def _decide_file_is_accepted(self, entry: FileEntry, dir_is_accepted: typing.Optional[bool]) -> FilterResult:
        result = FilterResult.UNSPECIFIED
        if dir_is_accepted:
            matched = False
            for pattern in (self._config.get('files.pattern.accept') or []):
                if re.match(pattern, entry.uppercase_basename):
                    result = FilterResult.ACCEPT
                    matched = True
                    break
            if not matched:
                for pattern in (self._config.get('files.pattern.reject') or []):
                    if re.match(pattern, entry.uppercase_basename):
                        result = FilterResult.REJECT
                        break
        elif dir_is_accepted is None:
            for pattern in (self._config.get('files.pattern.reject') or []):
                if re.match(pattern, entry.uppercase_basename):
                    result = FilterResult.REJECT
                    break
        else:
            result = FilterResult.REJECT
        return result


class ProcessInputToFilter:
    def __init__(self, filter: Filter, prompt):
        self._filter = filter
        self._prompt = prompt
        self._histfile = os.path.join(os.path.expanduser("~"), ".dewi_select_images_history")
        self._parser = self._build_parser()
        self._load_history()
        self._current_entry: FileEntry = None
        self._process_exit_value: bool = None
        self._ns: argparse.Namespace = None

    def _build_parser(self) -> argparse.ArgumentParser:

        parser = argparse.ArgumentParser('')
        sp = parser.add_subparsers(dest='main_command')

        self._register_parser(sp, 'print', ['p'], self._print_entry_with_checksum, 'Print last entry and checksum')
        self._register_parser(sp, 'exit', ['x', 'quit', 'q'], self._handle_quit,
                              'Terminates program and save filter db')
        self._register_parser(sp, 'next', ['n', 'c', 'continue'], self._handle_next, 'Process next image entry')
        self._register_parser(sp, 'help', ['h', '?'], self._handle_help, 'Print main help')
        self._register_parser(sp, 'filter', ['f', 'print-filter', 'pf'], self._handle_filter, 'Print filter')
        self._register_parser(sp, 'edit', ['ed', 'e'], self._handle_edit, 'Edit filter file')
        p = self._register_parser(sp, 'add-dir', ['ad'], self._handle_dir_full_path,
                                  'Accept full directory path, alias of "add accept dir-full-path"')
        p.set_defaults(main_command='accept')
        p = self._register_parser(sp, 'reject-dir', ['rd'], self._handle_dir_full_path,
                                  'Reject full directory path, alias of "add accept dir-full-path"')
        p.set_defaults(main_command='reject')
        self._register_accept_reject(sp)

        return parser

    def _register_parser(self, subparsers, name: str, aliases: collections.Iterable, func: callable, help: str):
        parser = subparsers.add_parser(name, aliases=aliases, help=help)
        parser.set_defaults(func=func)
        return parser

    def _register_parser_with_default_help(self, subparsers, name: str, aliases: collections.Iterable, help: str):
        parser = subparsers.add_parser(name, aliases=aliases, help=help)
        parser.set_defaults(func=parser.print_help)
        return parser

    def _register_accept_reject(self, subparsers):
        parser_accept = self._register_parser_with_default_help(subparsers, 'accept', (), help='Add an ACCEPT rule')
        sp_accept = parser_accept.add_subparsers()
        parser_reject = self._register_parser_with_default_help(subparsers, 'reject', (), help='Add a REJECT rule')
        sp_reject = parser_reject.add_subparsers()

        for item in [sp_accept, sp_reject]:
            self._register_file_pattern(item)
            self._register_subdir_name(item)

            partial_p = self._register_parser(item, 'dir-partial-path', [], self._handle_dir_partial_path,
                                              'Add a REJECT/ACCEPT rule for a part of the directory path, '
                                              'eg. .aplibrary/Preview')
            partial_p.add_argument('partial_path', nargs=1, help='The partial path')
            self._register_parser(item, 'dir-full-path', [], self._handle_dir_full_path,
                                  "Add an ACCEPT/REJECT rule for current file's directory and all of its items")

    def _register_file_pattern(self, subparsers):
        parser = self._register_parser(subparsers, 'file-pattern', [], self._handle_file_pattern,
                                       'Add a (REJECT/ACCEPT) regex pattern for uppercase filename')
        # parser.add_argument('pattern', nargs=1, help='The regex pattern')

    def _register_subdir_name(self, subparsers):
        parser = self._register_parser(subparsers, 'dir-subdir-name', [], self._handle_subdir_name,
                                       'Add a (REJECT/ACCEPT) rule for a name of a subdirectory part of the file path, eg. Preview')

        parser.add_argument('name', nargs=1, help='The directory name')

    def _load_history(self):
        try:
            readline.read_history_file(self._histfile)
            # default history len is -1 (infinite), which may grow unruly
            readline.set_history_length(10000)
        except FileNotFoundError:
            pass
        atexit.register(readline.write_history_file, self._histfile)

    def set_entry(self, entry: FileEntry):
        self._current_entry = entry

    def read_and_process_line(self):
        self._process_exit_value = None
        self._print_entry_with_checksum()
        while True:
            t = self._read_line()

            if not t:
                continue

            try:
                self._ns = self._parser.parse_args(shlex.split(t))
                self._ns.func()
            except SystemExit:
                pass
            except ValueError as e:
                print('VALUE ERROR: ' + str(e))
                pass

            if self._process_exit_value is not None:
                return self._process_exit_value

    def _read_line(self):
        read = False
        t = ''
        while not read:
            try:
                t = input(f'> {self._current_entry.orig_path}\n> {self._prompt}$ ')
                read = True
            except KeyboardInterrupt:
                print('')
                pass
            except EOFError:
                print('')
                t = 'exit'
                read = True

        return t.strip()

    def _print_entry_with_checksum(self):
        self._current_entry.print()

    def _handle_quit(self):
        self._process_exit_value = False

    def _handle_next(self):
        self._process_exit_value = True

    def _handle_help(self):
        self._parser.print_help()

    def _handle_filter(self):
        self._filter.print()

    def _handle_edit(self):
        self._filter.save()
        subprocess.call(['editor', self._filter.filename])
        self._filter.reload()

    def _handle_file_pattern(self):
        pattern = self._current_entry.uppercase_basename
        pattern = re.sub(r'([][.*+(){}])', r'\\\1', pattern)
        pattern = re.sub(r'[0-9]', '[0-9]', pattern)
        if self._ns.main_command == 'accept':
            self._filter.add_accept_file_pattern(pattern)
        else:
            self._filter.add_reject_file_pattern(pattern)

    def _handle_subdir_name(self):
        if self._ns.main_command == 'accept':
            self._filter.add_accept_subdir_name(self._ns.name[0])
        else:
            self._filter.add_reject_subdir_name(self._ns.name[0])

    def _handle_dir_partial_path(self):
        if self._ns.main_command == 'accept':
            self._filter.add_accept_dir_path_part(self._ns.partial_path[0])
        else:
            self._filter.add_reject_dir_path_part(self._ns.partial_path[0])

    def _handle_dir_full_path(self):
        if self._ns.main_command == 'accept':

            self._filter.add_accept_full_path(os.path.dirname(self._current_entry.orig_path))
        else:
            self._filter.add_reject_full_path(os.path.dirname(self._current_entry.orig_path))
