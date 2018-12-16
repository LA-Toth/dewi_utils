# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import sys
import time
import traceback
import typing
import urllib.request

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, \
    ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dewi.commands.packt.config import Config
from dewi.commands.packt.utils import save_screenshot
from dewi.core.logger import logger
from dewi.utils.yaml import save_to_yaml


class TimeoutChanger:
    def __init__(self, runner, timeout: int):
        self.runner = runner
        self.timeout = timeout
        self.previous_timeouts = []

    def __enter__(self):
        self.previous_timeouts.append(self.runner._timeout)
        self.runner._timeout = self.timeout
        self.runner._driver.implicitly_wait(self.timeout)

        return self

    def __exit__(self, *args):
        timeout = self.previous_timeouts.pop()
        self.runner._timeout = timeout
        self.runner._driver.implicitly_wait(timeout)


class Packt:
    LOGIN_RETRY_LIMIT = 5

    def __init__(self, driver: webdriver.Chrome, config: Config):
        self._driver = driver
        self._config = config
        self._timeout = config.driver.timeout

    def _save_screenshot(self, filename_prefix: str):
        save_screenshot(self._driver, self._config.driver.screenshot_directory, filename_prefix)

    def _save_failure(self, prefix: typing.Optional[str] = None):
        self._save_screenshot(prefix or 'siebel-fail')

    def login(self) -> bool:
        logger.info('Logging in, trying at most 5 times')

        success = False
        counter = 0

        while not success and counter < self._config.packt.login_retry_limit:
            counter += 1

            logger.info('Login attempt #{}'.format(counter))
            try:
                self._driver.get('https://www.packtpub.com/#')

                self._wait_and_click_by_xpath("//div[@id='account-bar-login-register']/a[1]")

                self._driver.find_elements_by_xpath("//input[@id='email']")[1].send_keys(self._config.packt.username)
                self._driver.find_elements_by_xpath("//input[@id='password']")[1].send_keys(self._config.packt.password)
                self._driver.find_elements_by_xpath("//input[@id='edit-submit-1']")[1].click()

                time.sleep(3)

                success = True

            except:
                logger.error(
                    "Login failed for " + str(counter) + " time, in " + str(self._timeout) +
                    " sec, page title is: " + self._driver.title)
                self._save_failure('siebel-login-failure')

                time.sleep(1)

        return counter <= 5

    def _wait_and_click_by_xpath(self, xpath: str):
        logger.debug(f'Wait and click on xpath "{xpath}"')
        WebDriverWait(self._driver, self._timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        WebDriverWait(self._driver, self._timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        WebDriverWait(self._driver, self._timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))

        for i in range(10):
            try:
                self._driver.find_element_by_xpath(xpath).click()
                return

            except ElementNotInteractableException:
                logger.error('Element is not interactable as of now')
                time.sleep(4)
            except WebDriverException as e:
                if 'is not clickable at point' in e.msg and (
                        ' Other element would receive the click' in e.msg  # chrome
                        or ' because another element ' in e.msg  # firefox
                ):
                    logger.error('Another element would receive the click, try again after a while')
                    time.sleep(4)
                else:
                    raise e

        raise WebDriverException(f"Unable to click on xpath \"{xpath}\"")

    def _find_element_by_xpath(self, xpath):
        return WebDriverWait(self._driver, self._timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))

    def has_unfinished_download(self):
        for item in os.listdir(self._config.driver.download_directory):
            if item.endswith('.crdownload'):
                return True

        return False

    def _wait_for_dl(self):
        while self.has_unfinished_download():
            logger.debug('Waiting to finish download')
            time.sleep(3)

    def _move_dl_file_to(self, book_title):
        target_dir = os.path.join(self._config.driver.download_directory, 'ebooks', book_title)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        for item in os.listdir(self._config.driver.download_directory):
            full_path = os.path.join(self._config.driver.download_directory, item)
            if os.path.isfile(full_path):
                new_name = os.path.join(target_dir, item)
                os.rename(full_path, new_name)

    def _is_downloaded(self, book_title) -> bool:
        return os.path.exists(os.path.join(self._config.driver.download_directory, 'ebooks', book_title))

    def _ensure_clean_dl_dir(self):
        for item in os.listdir(self._config.driver.download_directory):
            full_path = os.path.join(self._config.driver.download_directory, item)
            if os.path.isfile(full_path):
                logger.debug('Unlink unknown file', dict(path=full_path))
                os.unlink(full_path)

    def _full_path_for_title(self, book_title: str, filename: str):
        return os.path.join(self._config.driver.download_directory, 'ebooks', book_title, filename)

    def download(self):

        for page in range(1, 6):
            done = False
            while not done:
                try:
                    self._driver.get('https://www.packtpub.com/account/my-ebooks?page={}'.format(page))
                    logger.info('Loaded site, wait 5 seconds', dict(page=page))
                    time.sleep(5)

                    with TimeoutChanger(self, 5):
                        try:
                            self._driver.find_element_by_xpath("//a[@aria-label='dismiss cookie message']").click()
                        except:
                            pass

                    for elem in self._driver.find_elements_by_xpath("//div[@class = 'product-line unseen']"):
                        close_elem = elem.find_element_by_xpath(".//div[contains(@class, 'toggle-product-line')]")
                        title = elem.find_element_by_xpath(".//div[@class='title']").text.strip().replace('[eBook]',
                                                                                                          '').strip()
                        price_text = elem.find_element_by_xpath(".//span[@class='uc-price']").get_attribute('innerHTML')

                        book_picture = elem.find_element_by_xpath(
                            ".//div[@class='float-left product-thumbnail toggle']//noscript").get_attribute(
                            'innerHTML').split(' ', 3)[1].replace('src=', '').replace('"', '')

                        logger.info('Processing book', dict(title=title, page=page))

                        if self._is_downloaded(title):
                            logger.info('Book is already downloaded')
                            continue

                        self._ensure_clean_dl_dir()

                        close_elem.click()

                        a_elems = elem.find_elements_by_xpath(".//a")

                        for a_elem in a_elems:
                            if '/ebook_download/' not in a_elem.get_attribute(
                                    'href') and '/code_download/' not in a_elem.get_attribute('href'):
                                continue

                            logger.info('Clicking on link', dict(href=a_elem.get_attribute('href')))

                            a_elem.click()
                            time.sleep(1.5)

                        logger.debug('Wait 2 seconds before checking if there is a download')
                        time.sleep(2)
                        self._wait_for_dl()
                        self._move_dl_file_to(title)

                        with open(self._full_path_for_title(title, 'price.txt'), 'wt') as f:
                            f.writelines([price_text])

                        with open(self._full_path_for_title(title, 'cover.png'), 'wb') as f:
                            with urllib.request.urlopen(book_picture) as response:
                                f.write(response.read())

                        close_elem.click()
                        logger.debug('Wait 2 seconds before loading next book to lower server load')
                        time.sleep(2)

                    done = True
                except KeyboardInterrupt:
                    raise
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
                    time.sleep(1)

    def download_urls(self):
        books = {}
        for i in range(1, 6):
            done = False
            while not done:
                try:
                    self._driver.get('https://www.packtpub.com/account/my-ebooks?page={}'.format(i))
                    logger.info('Loaded site, wait 5 seconds', dict(page=i))
                    time.sleep(5)

                    for elem in self._driver.find_elements_by_xpath("//div[@class = 'product-line unseen']"):
                        title = elem.find_element_by_xpath(".//div[@class='title']").text.strip().replace('[eBook]',
                                                                                                          '').strip()

                        print(title)
                        books[title] = []

                        a_elems = elem.find_elements_by_xpath(".//a")

                        for a_elem in a_elems:
                            if '/ebook_download/' not in a_elem.get_attribute(
                                    'href') and '/code_download/' not in a_elem.get_attribute('href'):
                                continue

                            books[title].append(a_elem.get_attribute('href'))

                    done = True
                except KeyboardInterrupt:
                    raise

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

            save_to_yaml(books, os.path.expanduser('~/ebooks.yml'))
