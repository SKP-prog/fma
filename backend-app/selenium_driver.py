import time

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import os


class Selenium:
    def __init__(self, is_headless=True):
        LOGGER.setLevel(logging.CRITICAL)
        os.environ["WDM_LOG"] = '0'

        options = Options()
        if is_headless:
            options.add_argument("--headless=new")
        else:
            options.add_experimental_option("detach", True)

        options.add_argument("--incognito")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=1")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)

    def get_driver(self):
        return self.driver

    def find_element(self, xpath, attempts=5):
        for i in range(attempts + 1):
            try:
                if i > 0:
                    print(f"Failed to Find Element with XPATH: {xpath}. Retry ({i}/{attempts})")
                    print(self.driver.current_url)
                elem = self.driver.find_element(By.XPATH, xpath)
                return elem
            except selenium.common.exceptions.NoSuchElementException as e:
                time.sleep(1)
                continue

        raise TimeoutError(f"Failed to find Element with XPATH: {xpath}")
