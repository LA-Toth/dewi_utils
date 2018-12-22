# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import argparse

from dewi.commands.packt.config import load_config
from dewi.commands.packt.runner import run
from dewi.core.command import Command
from dewi.core.commandplugin import CommandPlugin


class PacktCommand(Command):
    name = 'packt'
    aliases = []
    description = "Packt stuffs"

    def register_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--wait', help='Wait a minute before closing Chrome', action='store_true')

        driver_grp = parser.add_argument_group(
            'Browser and WebDriver options',
            description='Options influences the behaviour of Selenium Web Driver and Google Chrome / Firefox')

        driver_grp.add_argument('--screenshots', '--screenshot-dir', dest='screenshot_dir', default='.',
                                help='The directory to save any screenshot, default: current directory')
        driver_grp.add_argument('--download-directory', '--dl-dir', dest='download_dir', required=True,
                                help='Download directory')
        driver_grp.add_argument('--headless', action='store_true', help='Start Chrome in headless mode')
        driver_grp.add_argument('--timeout', type=int, default=60,
                                help='Timeout for waiting any element or action, default: 60s')

    def run(self, args: argparse.Namespace):
        config = load_config()
        config.driver.screenshot_directory = args.screenshot_dir
        config.driver.download_directory = args.download_dir
        config.driver.headless = args.headless
        config.driver.timeout = args.timeout
        config.wait_before_close = args.wait

        return run(config)


PacktPlugin = CommandPlugin.create(PacktCommand)
