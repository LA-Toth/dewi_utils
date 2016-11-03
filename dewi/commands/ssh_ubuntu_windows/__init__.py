# Copyright (c) 2016 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3


import argparse
import collections
import os
import shlex
import subprocess

from dewi.core.command import Command
from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class SshToUbuntuOnWindows(Command):
    name = 'ssh_chdir'
    aliases = ['ssh_ubuntu_on_owndiws', 'cu', 'chroot']
    parser_description = "Ssh to localhost, to ubuntu on windows, into current directory"

    def run(self, args: argparse.Namespace):
        path = self.__prepare_path(os.getcwd())
        res = subprocess.run(
            ['ssh', '-oUserKnownHostsFile=/dev/null', '-oStrictHostKeyChecking=no', '127.0.0.1',
             '-t', 'cd {} && bash'.format(path)])
        return res.returncode

    def __prepare_path(self, path: str):
        return shlex.quote('/mnt/' + path[0].lower() + '/'.join(path[2:].split('\\')))


class SshToUbuntuOnWindowsPlugin(Plugin):
    def get_description(self) -> str:
        return 'Command plugin of: ' + SshToUbuntuOnWindows.description

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}

    def load(self, c: Context):
        c['commands'].register_class(SshToUbuntuOnWindows)
