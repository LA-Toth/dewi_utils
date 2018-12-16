# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os.path

from dewi.config.node import Node


class PacktOptions(Node):
    def __init__(self):
        self.username: str = None
        self.password: str = None
        self.login_retry_limit = 5


class DriverOptions(Node):
    def __init__(self):
        self.name: str = None
        self.driver_path: str = None
        self.download_temp_suffix: str = None
        self.screenshot_directory: str = '.'
        self.download_directory: str = '/tmp'
        self.headless: bool = False
        self.timeout: int = 60


class ChromeDriverOptions(DriverOptions):
    def __init__(self):
        super().__init__()
        self.name = 'chrome'
        self.driver_path: str = os.path.expanduser("~/.config/dewi/chromedriver")
        self.download_temp_suffix = '.crdownload'


class FirefoxDriverOptions(DriverOptions):
    def __init__(self):
        super().__init__()
        self.name = 'firefox'
        self.driver_path: str = os.path.expanduser("~/.config/dewi/geckodriver")
        self.download_temp_suffix = 'tmp'


class Config(Node):
    def __init__(self):
        self.packt = PacktOptions()
        self.driver: DriverOptions = None
        self.wait_before_close: bool = False

    def set_driver(self, driver: str):
        self.driver = ChromeDriverOptions() if driver == 'chrome' else FirefoxDriverOptions()


class ConfigError(RuntimeError):
    pass


def load_config() -> Config:
    filename = os.path.expanduser('~/.config/dewi/packt.conf')
    if not os.path.exists(filename):
        raise ConfigError('Config file is missing, path=' + filename)

    config = Config()
    with open(filename) as f:
        config.packt.username = f.readline()[:-1]
        config.packt.password = f.readline()[:-1]

    config.set_driver('chrome')

    return config
