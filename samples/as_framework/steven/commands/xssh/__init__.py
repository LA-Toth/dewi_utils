# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import subprocess

from dewi.core.command import Command


class XSshCommand(Command):
    """Logs into an SSH server and chroots on the server if necessary"""

    name = 'xssh'
    aliases = [
        'x' + postfix
        for postfix in ['chroot', 'srv']]
    description = "Start ssh to log in to a server or on a chroot"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('server', help='The SSH server address to log in to')

    def run(self, args: argparse.Namespace):
        cmd = 'chroot /srv/chroot/example' if args.running_command_.endswith('chroot') else 'bash'
        res = subprocess.run(
            ['ssh', '-oUserKnownHostsFile=/dev/null', '-oStrictHostKeyChecking=no',
             '-l', 'root', args.server, '-t', cmd])
        return res.returncode
