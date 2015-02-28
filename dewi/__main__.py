# Copyright 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

from argparse import ArgumentParser
import collections
import sys
from dewi.core.application import MainApplication
from dewi.loader.loader import PluginLoader


def main():
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        '-p', '--plugin', help='Load this plugin. This option can be specified more than once.',
        default=[], action='append')

    opts, args = parser.parse_known_args(sys.argv[1:])
    _main(opts.plugin or {'dewi.core.application.DewiPlugin'}, args)


def _main(plugins: collections.Iterable, args: collections.UserList):
    app = MainApplication()
    sys.exit(app.run(plugins, args))

if __name__ == '__main__':
    main()
