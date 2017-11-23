# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import typing

from dewi.logparser.loghandler import LogParserModule
from dewi.module_framework.messages import Level


class KernelModule(LogParserModule):
    """
    Example module to track processes which are unresponsible on a system having high - I/O - load
    """

    def get_registration(self):
        return [
            {
                'program': 'kernel',
                'message_substring': 'blocked for more than 120 seconds',
                'callback': self._blocked_process
            }
        ]

    def start(self):
        self._blocked_process_list = list()

    def _blocked_process(self, time: str, program: str, pid: typing.Optional[str], msg: str):
        # example msg:
        # [16974495.906550] INFO: task java:14545 blocked for more than 120 seconds.

        parts = msg.split(' ', 4)
        self._blocked_process_list.append(dict(time=time, program=parts[3]))

    def finish(self):
        self.set('system.blocked_processes.count', len(self._blocked_process_list))
        if len(self._blocked_process_list):
            self.add_message(
                Level.WARNING, 'System', 'Kernel',
                "Blocked processes; count='{}'".format(len(self._blocked_process_list)))

            for process in self._blocked_process_list:
                self.append('system.blocked_processes.details', process)
