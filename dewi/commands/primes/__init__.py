# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse
import typing

from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin


class PrimeGenerator:
    def __init__(self, smaller_than: typing.Optional[int], count: typing.Optional[int]):
        self.smaller_than = smaller_than
        self.count = count

    def run(self):
        # from https://hackernoon.com/prime-numbers-using-python-824ff4b3ea19
        print(2)

        count = 1
        possible_prime = 3
        while True:
            if self.smaller_than is not None and possible_prime > self.smaller_than:
                break

            # Assume number is prime until shown it is not.
            is_prime = True
            for num in range(2, int(possible_prime ** 0.5) + 1):
                if possible_prime % num == 0:
                    is_prime = False
                    break

            if is_prime:
                print(possible_prime)
                count += 1

            if self.count is not None and count >= self.count:
                break

            possible_prime += 1


class PrimesCommand(Command):
    name = 'primes'
    aliases = ['prime']
    description = "Calculate first N primes"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('-s', '--smaller-than', dest='smaller_than', type=int,
                            help='Print till the primes are smaller than this value.')
        parser.add_argument('-c', '--count', type=int,
                            help='Max number of printed primes (if --smaller-than is not specified, count is 100)')

    def run(self, args: argparse.Namespace):
        if args.smaller_than is None and args.count is None:
            args.count = 100

        p = PrimeGenerator(args.smaller_than, args.count)
        return p.run()


PrimesPlugin = CommandPlugin.create(PrimesCommand)
