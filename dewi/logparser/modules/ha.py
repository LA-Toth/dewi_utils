# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import typing

from dewi.logparser.loghandler import LogParserModule
from dewi.module_framework.messages import Level


class HaModule(LogParserModule):
    """
    An example module, which processes all log entries of HA (cl_status is a process that belongs to it)
    http://www.linux-ha.org/wiki/Heartbeat
    """
    def get_registration(self):
        """
        If the program name is cl_status, call process_entry.

        The return value is an array, therefore multiple conditions can be added
        """
        return [{'program': 'cl_status', 'callback': self.process_entry}]

    def process_entry(self, time: str, program: str, pid: typing.Optional[str], msg: str):
        """
        Processes the whole match, and depending on the content may add some messages
        In this example every log message is added to the warnings.
        """
        self.add_message(Level.WARNING, 'HA', 'HA', 'CL:' + msg)
