# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import re
import typing

from dewi.logparser.loghandler import LogParserModule
from dewi.module_framework.messages import Level


class WebModule(LogParserModule):
    """
    An example plugin when a web-based authentication framework logs authentication failures
    A log example: 2016-09-20T23:42+0200 host.domain web: Authentication failed; username='unknown_user'
    """

    def get_registration(self):
        return [
            {
                'program': 'web',
                'message_regex': r'^.*Authentication failed; username=\'.*\'$',
                'callback': self.auth_failure
            }
        ]

    def start(self):
        self._failed_auths = dict()

    def auth_failure(self, time: str, program: str, pid: typing.Optional[str], msg: str):
        m = re.match(r'.*; username=\'([^\']+)\'', msg)
        if m:
            self._add_to_map(self._failed_auths, m.group(1), time)

    def _add_to_map(self, map, key: str, value: str):
        if key not in map:
            map[key] = list()

        map[key].append(value)

    def finish(self):
        for user in self._failed_auths:
            self.add_message(
                Level.WARNING, 'Web', 'Auth',
                "User '{}' has {} failed auth(s)".format(user, len(self._failed_auths[user])))
