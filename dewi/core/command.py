# Copyright 2015-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import typing


class Command:
    name = ''
    aliases = list()
    description = ''

    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass

    def run(self, args: argparse.Namespace) -> typing.Optional[int]:
        raise NotImplementedError
