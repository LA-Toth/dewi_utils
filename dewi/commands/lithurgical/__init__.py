# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin
from dewi.utils.lithurgical import print_events_of_year


class LithurgicalCommand(Command):
    name = 'lithurgical'
    aliases = []
    description = "Prints Lutheran liturgical events of a calendar year"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('year', type=int, help='The calendar year')

    def run(self, args: argparse.Namespace):
        year: int = args.year
        if year < 1600:
            print('Please specify a year not earlier than 1600')
            return 1
        if year > 2200:
            print('Please specify a year not later than 2200')
            return 1

        print_events_of_year(year)
        return


LithurgicalPlugin = CommandPlugin.create(LithurgicalCommand)
