# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import os
import typing

import time

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin


class LicenseChange:
    EXTENSIONS = (
        '.c', '.cc', '.ccp', '.cxx', '.h', '.hh', '.hpp',
        '.py', '.rb', '.md', '.rst', '.php', '.tpl', '.erb')

    COPYRIGHT_PREFIX = '# Copyright '
    COPYRIGHT_PREFIX2 = '# Copyright (c) '
    LICENSE_PREFIX = '# Distributed under the terms of'
    LICENSES = {
        'gplv3': 'the GNU General Public License v3',
        'lgplv3': 'the GNU Lesser General Public License v3',
    }

    def __init__(self, target: typing.List[str]):
        self.target = target
        self.license = 'lgplv3'
        self.year = time.strftime('%Y')

    def run(self):
        for file in self._walk():
            self._update_file(file)

    def _walk(self) -> typing.Iterable[str]:
        for entry in self.target:
            if not os.path.exists(entry):
                continue

            if os.path.isdir(entry):
                for root, dirs, files in os.walk(entry):
                    for name in files:
                        _, ext = os.path.splitext(name)
                        if ext.lower() not in self.EXTENSIONS:
                            continue
                        full_path = os.path.join(root, name)
                        yield full_path
            else:
                yield os.path.abspath(entry)

    def _update_file(self, filename: str):
        lines = []
        update_needed = False
        with open(filename) as f:
            for line in f:
                line = line[:-1]
                if len(lines) > 10 and not update_needed:
                    break
                lines.append(line)
                if not update_needed and line.startswith(self.LICENSE_PREFIX) and \
                        line != f'{self.LICENSE_PREFIX} {self.LICENSES[self.license]}':
                    update_needed = True

        if update_needed:
            headers = self._update_headers(lines[0:10])
            others = lines[10:]

            with open(filename, 'w') as f:
                for line in headers:
                    print(line, file=f)
                for line in others:
                    print(line, file=f)

    def _update_headers(self, headers: typing.List[str]):
        result = []
        for header in headers:
            if header.startswith(self.LICENSE_PREFIX):
                result.append(f'{self.LICENSE_PREFIX} {self.LICENSES[self.license]}')
            elif header.lower().startswith(self.COPYRIGHT_PREFIX2.lower()):
                result.append(self._get_copyright_header(header[len(self.COPYRIGHT_PREFIX2):]))
            elif header.startswith(self.COPYRIGHT_PREFIX):
                result.append(self._get_copyright_header(header[len(self.COPYRIGHT_PREFIX):]))
            else:
                result.append(header)
        return result

    def _get_copyright_header(self, date_and_others: str):
        date, others = date_and_others.split(' ', 1)

        years = date.split('-')

        if len(years) == 1:
            if years[0] != self.year:
                date = f'{years[0]}-{self.year}'
        else:
            date = f'{years[0]}-{self.year}'

        return f'{self.COPYRIGHT_PREFIX}{date} {others}'


class LicenseCommand(Command):
    name = 'license'
    description = "Switches between licenses (Distributed under the terms of X)"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.set_defaults(func=parser.print_usage)
        subparsers = parser.add_subparsers(dest='subcmd')
        change = subparsers.add_parser('change')
        change.add_argument(
            '--lgpl-v3', required=True, action='store_true',
            help='Swithces to LGPL v3')

        change.add_argument(
            'target', nargs="+", help='One or more directory or file to be updated')
        change.set_defaults(func=self._license_change)

    def run(self, args: argparse.Namespace):
        if 'subcmd' in args:
            self.ns = args
        return args.func()

    def _license_change(self):
        LicenseChange(self.ns.target).run()


LicensePlugin = CommandPlugin.create(LicenseCommand)
