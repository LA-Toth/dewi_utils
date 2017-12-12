# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


import argparse
import collections
import errno
import os
import re
import sys

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin


class Splitter:
    def __init__(self, file_name: str, target_dir: str, delimiter: str = ':', reopen: bool = False,
                 silent: bool = False):
        self.file_handles = collections.OrderedDict()
        self._file_name = file_name
        self._target_dir = target_dir
        self._delimiter = delimiter
        self._reopen_files = reopen
        self._silent = silent

    def run(self):
        if os.path.exists(self._target_dir) and not self.__is_directory_empty():
            print("Target directory '{0}' is not empty".format(self._target_dir))
            return 1

        if not os.path.exists(self._target_dir):
            os.mkdir(self._target_dir, 0o755)
        self.__split_session()
        return 0

    def __is_directory_empty(self):
        listing = os.listdir(self._target_dir)
        return len(listing) == 0

    def __split_session(self):
        if self._file_name == '-':
            self.__split_session_opened(sys.stdin)
        else:
            with open(self._file_name, encoding='UTF-8', errors='surrogateescape') as f:
                self.__split_session_opened(f)

        self.__close_files()

    def __split_session_opened(self, file):
        line = file.readline()
        line_number = 0
        while line:
            file_id = self.__get_file_id_from_line(line)
            if file_id:
                fw = self.__open(*file_id)
                fw.write(line)
                if self._reopen_files:
                    fw.close()
            line = file.readline()
            line_number += 1
            if not self._silent and (line_number % 10000) == 0:
                print(line_number)

    def __get_file_id_from_line(self, line):
        parts = line.split(None, 7)
        if len(parts) < 6:
            return None

        if parts[4] == '->' and parts[3].startswith('0x'):
            index = 6
        else:
            index = 4
        full_session_id = parts[index].split('/', 4)
        if len(full_session_id) >= 2 and full_session_id[0] == '(svc':
            session_id = self.__strip_session_id(full_session_id)
            pid = re.sub(r'.*\[([0-9]+)\].*', r'\1', parts[2])
            return (pid, session_id)
        return None

    def __strip_session_id(self, session_id_parts: list):
        prefix = session_id_parts[1].split(':', 2)
        index = 1
        if len(prefix) == 1:
            # it's an unique number for the current instance (process)
            index += 1

        return session_id_parts[index].strip(':)')

    def __open(self, pid, session_id):
        if self._delimiter != ':':
            session_id = session_id.replace(':', self._delimiter)

        if (pid, session_id) in self.file_handles:
            return self.file_handles[(pid, session_id)]

        directory = os.path.join(self._target_dir, pid)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, session_id + '.log')

        try:
            f = open(file_path, 'at', encoding='UTF-8', errors='surrogateescape')
        except IOError as e:
            if e.errno == errno.EMFILE:
                self.__close_some_files()
                f = open(file_path, 'at')
            else:
                raise

        if not self._reopen_files:
            self.file_handles[(pid, session_id)] = f
        return f

    def __close_some_files(self):
        close_count = len(self.file_handles) / 2
        while close_count > 0:
            (_, fh) = self.file_handles.popitem(last=False)
            fh.close()
            close_count -= 1

    def __close_files(self):
        for handle in self.file_handles.values():
            handle.close()
        self.file_handles = dict()


class SplitZorpLogCommand(Command):
    name = 'splitzorplog'
    aliases = ['split-to-sessions']
    description = "Splits a Zorp log into several file, one session per file"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '-d', '--directory', '--target-directory', dest='directory', required=True,
            help='An empty or non-existant directory where the splitted logs will be')
        parser.add_argument(
            '--reopen', dest='reopen',
            help='Reopen each file when appending to it instead of store handles.'
                 ' It works with thousands of sessions but it is very slow')
        parser.add_argument(
            '-s', '--silent', dest='silent', action='store_true',
            help='Do not print status, the line numbers')
        parser.add_argument(
            '-D', '-m', '--delimiter', dest='delimiter', default='.' if sys.platform == 'win32' else ':',
            help='Delimiter character used in filename, default: same as in session_id, the colon')
        parser.add_argument(
            'zorplogfile', nargs='?', default='-',
            help='The original Zorp log file to be splitted. Omit or use - to read from stdin')

    def run(self, args: argparse.Namespace):
        splitter = Splitter(args.zorplogfile, args.directory, args.delimiter, args.reopen, args.silent)
        splitter.run()


SplitZorpLogPlugin = CommandPlugin.create(SplitZorpLogCommand)
