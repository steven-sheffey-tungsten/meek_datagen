#!/usr/bin/env python3
# Copyright 2018 Steven Sheffey
# This file is part of meek_datagen.
# 
# meek_datagen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# meek_datagen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with meek_datagen.  If not, see <http://www.gnu.org/licenses/>.
import logging
import os
from os import path
import random
import signal
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


# Filename of geckodriver/firefox logs
FIREFOX_LOG_PATH=path.join(path.expanduser("~"), "logs", "firefox.log")
# Where to find static data
DATA_FOLDER = path.join(path.expanduser("~"), "data")
# Alexa top 1M filename (in the data
ALEXA_TOP_1M_PATH = path.join(DATA_FOLDER, "top-1m.csv")

# Timeouts and timings for webdriver 
PAGE_LOAD_TIMEOUT = 30
WAIT_TIMEOUT = 10
WAIT_INTERVAL = 1
# How many websites to load before clearing cookies
COOKIE_CLEAR_FREQUENCY = 20
# Random seed
RANDOM_SEED=1337

# Initialize a logger
logger = logging.getLogger("automate_browsing")
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("%(filename)s %(asctime)s %(levelname)s %(funcName)s:%(lineno)d  %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

def line_to_url(line, protocol=None):
    """
    Parses a line from the alexa top 1M into a URL
    :param line: A line of data (potentially with a newline) from the alexa top1m dataset
    :type line: str
    :param protocol: the protocol (such as http or https) to request. Default is 'https'
    :type protocol: str
    :return: A URL (as the given protocol) from the line
    :rtype: str
    """
    if not protocol:
        protocol = 'https'
    else:
        protocol = protocol.lower()
    return "{}://{}".format(protocol, line.rstrip().split(",")[1])

def get_browser_controller():
    # Spawn a webdriver
    driver = webdriver.Firefox(log_path=FIREFOX_LOG_PATH)
    # Set timeouts
    driver.set_page_load_timeout(10)
    # Returns the driver
    return driver
        
def main():
    # Seed the RNG
    random.seed(RANDOM_SEED)
    # Get a browser 
    logger.info("Getting a connection to the browser")
    browser = get_browser_controller()
    logger.info("Got a connection to the browser")
    # Load the alexa top 1M dataset
    with open(ALEXA_TOP_1M_PATH, "r") as alexa_top1m_file:
        alexa_top1m = list(map(line_to_url, alexa_top1m_file.readlines()))
    # Shuffle the URLs
    random.shuffle(alexa_top1m)
    # Navigate to the alexa top 1M
    for index, website in enumerate(alexa_top1m):
        logger.info("Navigating to {} ({}/{})".format(website, index + 1, len(alexa_top1m)))
        # Navigate to the website
        try:
            browser.get(website)
        except Exception as err:
            logger.error("Error navigating: {}".format(err))
            logger.info("{} timed out during navigation or load".format(website))
        # Attempt to disable any alerts 
        while True:
            try:
                alert = browser.switch_to_alert()
                alert.dismiss()
                logger.warn("Alert appeared on {}. It was disabled".format(website))
            except:
                break
        # Print what page we are on
        try:
            logger.debug(u"Current page title: {}".format(browser.title))
        except:
            logger.error("Failed to print title for some reason")
        # Clear cookies occasionally so we don't accumulate memory leaks
        if index % COOKIE_CLEAR_FREQUENCY == 0:
            try:
                browser.delete_all_cookies()
                logger.info("Deleted all cookies")
            except:
                logger.error("Failed to delete cookies")
if __name__ == "__main__":
    main()
