# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import re
import time
import typing

from dewi.config.config import Config
from dewi.logparser.syslog import GenericParser, Parser
from dewi.module_framework.messages import CORE_CATEGORY, Level, Messages
from dewi.module_framework.module import GenericModule, Module


class LogParserModule(GenericModule):
    def get_registration(self) -> typing.List[typing.Dict[str, typing.Union[str, callable]]]:
        return []

    def start(self):
        pass

    def finish(self):
        pass


class _Pattern:
    def __init__(self, config: typing.Dict[str, typing.Union[str, callable]]):
        self.program = config.get('program', '')
        self.message_substring = config.get('message_substring', '')
        self.callback: typing.Union[callable, typing.List[callable]] = config['callback']
        regex = config.get('message_regex', '')
        self.single_callback = True

        if regex:
            self.message_regex: typing.Pattern[str] = re.compile(regex)
            self.process = self.process_regex
        else:
            self.message_regex: typing.Pattern[str] = ''
            if self.message_substring:
                self.process = self.process_substring
            else:
                self.process = self.callback

    def process_regex(self, time, program, pid, msg):
        m = self.message_regex.match(msg)

        if m:
            self.callback(time, program, pid, msg)

    def process_substring(self, time, program, pid, msg):
        if self.message_substring in msg:
            self.callback(time, program, pid, msg)

    def process_regex_multiple_times(self, time, program, pid, msg):
        m = self.message_regex.match(msg)

        if m:
            self.callback(time, program, pid, msg)

    def process_substring_multiple_times(self, time, program, pid, msg):
        if self.message_substring in msg:
            self.callback(time, program, pid, msg)

    def call_multiple_callbacks(self, time, program, pid, msg):
        for cb in self.callback:
            cb(time, program, pid, msg)

    def add_another_callback(self, callback: typing.Callable):
        # Checking state as originally it was optimized
        if self.single_callback:
            if self.process == self.process_regex:
                self.process = self.process_regex_multiple_times
            elif self.process == self.process_substring:
                self.process = self.process_substring_multiple_times
            else:
                self.process = self.call_multiple_callbacks
            self.callback = [self.callback]
            self.single_callback = False

        self.callback.append(callback)


class LogFileDefinition:
    def __init__(self, directory_list: typing.List[str], file_regex: typing.Union[typing.Pattern[str], str],
                 parser: Parser):
        self.directory_list = directory_list
        self.file_regex = file_regex
        self.parser = parser


class GenericLogFileDefinition(LogFileDefinition):
    def __init__(self):
        super().__init__(['/var/log'], r'^(syslog|system.log|messages)', GenericParser())


class LogHandlerModule(Module):
    """
    @type modules typing.List[LogParserModule]
    """

    def __init__(self, config: Config, messages: Messages, log_file_definition: LogFileDefinition):
        """
        base_path: which contains the directory of log messages
        It can be e.g. '/var'
        """
        super().__init__(config, messages)
        self._log_file_definition = log_file_definition
        self.modules = list()
        self._program_parsers = dict()
        self._other_parsers = set()
        self._patterns: typing.Dict[typing.Tuple, _Pattern] = dict()

    def provide(self):
        return 'log'

    def register_module(self, m: type):
        self.modules.append(m(self._config, self._messages))

    def run(self):
        self._init_parsers()
        files = self._collect_files()
        self._process_files(files)
        self._finalize_parsers()

    def _init_parsers(self):
        for module in self.modules:
            registrations = module.get_registration()
            for reg in registrations:
                self._process_registration(reg)
            module.start()

    def _process_registration(self, req: dict):
        key = (req.get('program', ''), req.get('message_substring', ''), req.get('message_regex', ''))

        if key in self._patterns:
            self._patterns[key].add_another_callback(req['callback'])
        else:
            pattern = _Pattern(req)
            self._patterns[key] = pattern

            if 'program' in req:
                self._add_to_map(self._program_parsers, req['program'], pattern)
            else:
                self._other_parsers.add(pattern)

    @staticmethod
    def _add_to_map(dictionary, key, value):
        if key not in dictionary:
            dictionary[key] = set()

        dictionary[key].add(value)

    def _finalize_parsers(self):
        for module in self.modules:
            module.finish()

    def _collect_files(self):
        date_file_map = dict()
        log_dir: str = None

        for entry in self._log_file_definition.directory_list:
            if os.path.exists(entry):
                log_dir = entry
        files = os.listdir(log_dir)
        for file in files:
            if not re.match(self._log_file_definition.file_regex, file):
                continue

            filename = os.path.join(log_dir, file)
            with open(filename, encoding='UTF-8', errors='surrogateescape') as f:
                line = f.readline()
                parsed = self._log_file_definition.parser.parse_date(line)
                date_file_map[parsed.group('date')] = filename

        return [date_file_map[k] for k in sorted(date_file_map.keys())]

    def _process_files(self, files: typing.List[str]):
        start = time.clock()
        cnt = 0
        for fn in files:
            with open(fn, encoding='UTF-8', errors='surrogateescape', newline='\n') as f:
                cnt += self._process_file(f)

        end = time.clock()
        diff = end - start
        self.add_message(
            Level.DEBUG, CORE_CATEGORY, CORE_CATEGORY,
            "Run time: {} line(s) in {} s ({:.2f} kHz)".format(cnt, diff, cnt / diff / 1000))

    def _process_file(self, f):
        # This is a heavily optimized code, please consider the consequences before changing it
        # The loop body must be extremely fast, because it runs on every log line

        cnt = 0
        line = 'non-empty'
        while line:
            line = f.readline()
            cnt += 1
            parts = line.split(' ', 3)
            if len(parts) != 4:
                continue

            if '[' in parts[2]:
                program, pid = parts[2].split('[')
                pid = pid.split(']')[0]
            else:
                program, pid = parts[2][:-1], None

            if program in self._program_parsers:
                for module in self._program_parsers[program]:
                    module.process(parts[0], program, pid, parts[3])
            else:
                for module in self._other_parsers:
                    module.process(parts[0], program, pid, parts[3])

        return cnt
