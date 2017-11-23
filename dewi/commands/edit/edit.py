# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import re
import subprocess

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin


def convert_to_vim_args(args):
    result = []
    if len(args) == 1:
        match = re.match(r'(.*?):([[0-9]+)(:[0-9]+)?:?$', args[0])
        if match:
            result.append(match.group(1))
            result.append('+' + match.group(2))
        else:
            result.append(args[0])
    elif len(args) > 1:
        result = ['-p'] + args

    return result


class EditCommand(Command):
    name = 'edit'
    aliases = ['ed']
    description = 'Calls vim with the file names and line numbers parsed from argument list.'

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('file_list', nargs=argparse.REMAINDER, help='List of files for editing')

    def run(self, ns: argparse.Namespace):
        args = ['vim'] + convert_to_vim_args(ns.file_list)
        pipe = subprocess.Popen(args)
        pipe.communicate()


EditPlugin = CommandPlugin.create(EditCommand)
