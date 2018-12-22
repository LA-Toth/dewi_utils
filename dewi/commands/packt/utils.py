# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import os.path
import time

from selenium import webdriver

from dewi.core.logger import logger


def save_screenshot(driver: webdriver.Chrome, directory: str, filename_prefix: str):
    os.makedirs(directory, exist_ok=True)
    if filename_prefix and filename_prefix[-1] not in ('-', '_'):
        filename_prefix += '_'

    timestamp = time.strftime('%Y%m%d_%H%M%S_UTC', time.gmtime(time.time()))
    filename = '{}{}.png'.format(filename_prefix, timestamp)

    logger.info('Saving screenshot', dict(directory=directory, filename=filename))
    driver.get_screenshot_as_file(
        os.path.join(directory, filename))
