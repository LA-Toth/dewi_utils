# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import json
import os.path
import ssl
import sys
import time
import traceback
import urllib.request

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from dewi.commands.packt.config import Config
from dewi.commands.packt.packt import Packt
from dewi.commands.packt.utils import save_screenshot
from dewi.core.logger import logger


def run(config: Config) -> int:
    return PacktDownloader(config).run()


class Runner:
    def __init__(self, config: Config):
        self._config = config

    def run(self) -> int:
        driver = None
        try:
            driver = self._create_web_driver()
            return self._run(driver)
        except Exception as exc:
            einfo = sys.exc_info()
            tb = traceback.extract_tb(einfo[2])
            tb_str = 'An exception occured:\n  Type: %s\n  Message: %s\n\n' % \
                     (einfo[0].__name__, einfo[1])
            for t in tb:
                tb_str += '  File %s:%s in %s\n    %s\n' % (t.filename, t.lineno, t.name, t.line)

            for line in tb_str.splitlines(keepends=False):
                logger.debug(line)

            logger.error('{}'.format(exc))

            if driver is not None:
                save_screenshot(driver, self._config.driver.screenshot_directory, 'packt-fail')

        finally:
            if driver:
                try:
                    if self._config.wait_before_close:
                        logger.info('Sleeping 60 seconds for checking content')
                        time.sleep(60)
                except:
                    driver.quit()
                    raise

                driver.quit()

            return 1

    def _run(self, driver):
        raise NotImplementedError()

    def _create_web_driver(self) -> RemoteWebDriver:
        if not os.path.exists(self._config.driver.driver_path):
            raise Exception("Selenium web driver not found at " + self._config.driver.driver_path)

        if self._config.driver.name == 'chrome':
            driver = self._create_chrome_web_driver()
        else:
            driver = self._create_firefox_web_driver()

        driver.implicitly_wait(self._config.driver.timeout)
        return driver

    def _create_chrome_web_driver(self):
        prefs = {
            # Below two chrome preference settings will disable popup dialog when download file.
            'profile.default_settings.popups': 0,
            'download.prompt_for_download': "false",

            # Set file save to directory.
            'download.default_directory': self._config.driver.download_directory,
        }
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', prefs)
        if self._config.driver.headless:
            chrome_options.add_argument('headless')
            chrome_options.add_argument('window-size=1200x600')
        driver = webdriver.Chrome(self._config.driver.driver_path, options=chrome_options)
        self._fix_download_for_headless_mode(driver)
        return driver

    def _fix_download_for_headless_mode(self, driver: webdriver.Chrome):
        url = driver.service.service_url + '/session/' + driver.session_id + '/chromium/send_command'

        command = {
            'cmd': 'Page.setDownloadBehavior',
            'params': {
                'behavior': 'allow',
                'downloadPath': self._config.driver.download_directory,
            }
        }

        request = urllib.request.Request(url
                                         , method='POST'
                                         , data=json.dumps(command).encode('UTF-8')
                                         , headers={'Content-Type': 'application/json; charset=UTF-8'}
                                         )

        self._urlopen(request)

    def _create_firefox_web_driver(self):
        options = Options()
        if self._config.driver.headless:
            options.headless = True

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", self._config.driver.download_directory)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-msdownload")

        return webdriver.Firefox(executable_path=self._config.driver.driver_path, firefox_options=options,
                                 firefox_profile=profile)

    def _update(self, url: str, data: dict):
        logger.debug('Patching data', dict(url=url, data=data))
        request = urllib.request.Request(url
                                         , method='PATCH'
                                         , data=json.dumps(data).encode('UTF-8')
                                         , headers={'Content-Type': 'application/json; charset=UTF-8'}
                                         )

        self._urlopen(request)

    def _urlopen(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        kwargs.update(dict(context=ctx))

        return urllib.request.urlopen(*args, **kwargs)


class PacktDownloader(Runner):
    def _run(self, driver):
        packt = Packt(driver, self._config)

        packt.login()

        packt.download()
        return 0
