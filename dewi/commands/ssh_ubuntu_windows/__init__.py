# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


import argparse
import os
import shlex
import subprocess

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin


class SshToUbuntuOnWindows(Command):
    name = 'ssh_ubuntu_on_windows'
    aliases = ['cu', 'chroot']
    description = "Ssh to localhost, to ubuntu on windows, into current directory"

    def run(self, args: argparse.Namespace):
        path = self.__prepare_path(os.getcwd())
        res = subprocess.run(
            ['ssh', '-oUserKnownHostsFile=/dev/null', '-oStrictHostKeyChecking=no', '127.0.0.1',
             '-t', 'cd {} && bash'.format(path)])
        return res.returncode

    def __prepare_path(self, path: str):
        return shlex.quote('/mnt/' + path[0].lower() + '/'.join(path[2:].split('\\')))


SshToUbuntuOnWindowsPlugin = CommandPlugin.create(SshToUbuntuOnWindows)
