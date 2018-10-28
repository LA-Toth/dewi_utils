#!/usr/bin/env python3

import sys

from dewi.core.application import MainApplication
from dewi.loader.loader import PluginLoader


def main():
    args = sys.argv[1:]

    loader = PluginLoader()
    app = MainApplication(loader, 'dewi')
    app.run(args)


if __name__ == '__main__':
    main()
