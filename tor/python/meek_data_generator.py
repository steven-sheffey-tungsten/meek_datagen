#!/usr/bin/env python2
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
from __future__ import print_function
import hashlib
import logging
import os
from os import path
import random
import signal
import socket
import struct
import subprocess
import sys
import time
import marionette_driver
from marionette_driver.marionette import Marionette


# Marionette connection information
MARIONETTE_HOST = "localhost"
MARIONETTE_PORT = 2828
# Filename of geckodriver/firefox logs
TBB_LOG=os.environ["TBB_LOG"]
# Filename for tor browser
TBB_PATH=os.environ["TBB_PATH"]
# Path to start tor browser
START_TBB=path.join(TBB_PATH, "Browser", "start-tor-browser")
# Where to find static data
DATA_FOLDER = path.join(path.expanduser("~"), "data")
# Alexa top 1M filename (in the data
ALEXA_TOP_1M_PATH = path.join(DATA_FOLDER, "top-1m.csv")

# Timeouts and timings for webdriver 
STARTUP_TIMEOUT=3600
PAGE_LOAD_TIMEOUT = 30000
WAIT_TIMEOUT = 10
WAIT_INTERVAL = 1
# How many websites to load before clearing cookies
COOKIE_CLEAR_FREQUENCY = 20
# Random seed
# RANDOM_SEED=1337
# Seed random generator from hostname so containers produce predictably different orders
def generate_random_seed():
    hostname = socket.gethostname()
    # Convert to 4 (fairly random) bytes
    hostname_hash = hashlib.sha512(hostname).digest()[:4]
    # Convert those bytes to a long
    return struct.unpack("<L", hostname_hash)
RANDOM_SEED = generate_random_seed()


# Initialize a logger
logger = logging.getLogger("meek_datagen")
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
        protocol = 'http'
    else:
        protocol = protocol.lower()
    return "{}://{}".format(protocol, line.rstrip().split(",")[1])

class TorBrowser:
    def __init__(self, tbb_path, log_path=None):
        # Command to initialize tor browser
        self.start_command = [START_TBB, "-marionette"]
        # Add log if necessary
        if log_path:
            self.start_command += ["-l", log_path]
        # Set browser process
        self.browser_process = None
        # Set marionette instance
        self.marionette = None

    def start(self):
        if self.browser_process:
            logger.warn("Browser already started")
        else:
            # Start tor browser process
            logger.info("Starting TOR Browser")
            self.browser_process = subprocess.Popen(self.start_command)
            logger.info("Started TOR Browser")
            # Start marionette
            self.start_marionette()

    def stop(self):
        if self.marionette is None:
            logger.error("Cannot stop TOR Browser. No marionette connection exists. To force, use TorBrowser.kill")
            # raise Exception("Cannot stop TOR Browser.")
        else:
            # Send kill signal
            self.marionette._send_message("quitApplication", {"flags": ["eForceQuit"]})
        if self.browser_process is None:
            logger.warn("No control over browser process. Hopefully it's not started")
        # Wait for browser to end
        self.browser_process.wait()
        # Nullify marionette and browser
        self.browser_process = None
        self.marionette = None
    def restart(self):
        self.stop()
        self.start()

    def kill(self):
        if self.browser_process is None:
            logger.error("Cannot kill TOR Browser if it doesn't exist")
            raise Exception("Cannot kill TOR Browser if it doesn't exist")
        self.browser_process.kill()
        self.browser_process = None
        self.marionette = None
        self.wait = None
    def start_marionette(self):
        if self.marionette:
            logger.warn("Marionette already started")
        else:
            # Spawn a webdriver
            logger.info("Connecting to Marionette")
            self.marionette = Marionette(host=MARIONETTE_HOST, port=MARIONETTE_PORT, startup_timeout=STARTUP_TIMEOUT)
            self.marionette = None
            # Start the session
            # self.marionette.start_session()
            # Set timeouts
            # self.marionette.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            # Get object for waiting
            # self.wait = marionette_driver.Wait(self.marionette, timeout=WAIT_TIMEOUT, interval=WAIT_INTERVAL)
            logger.info("Connected to Marionette")
    def get_marionette():
        return self.marionette
    def navigate(self, *args, **kwargs):
        if self.marionette:
            return self.marionette.navigate(*args, **kwargs)
        else:
            logger.error("Marionette is not initialized.")
    @staticmethod
    def page_is_ready(marionette):
        try:
            return marionette.execute_script("document.readyState == 'complete'")
        except:
            return False
    def wait_until_ready(self):
        if self.wait:
            return self.wait.until(TorBrowser.page_is_ready)
        else:
            logger.error("Marionette is not initialized.")
    
def main():
    # Seed the RNG
    random.seed(RANDOM_SEED)
    # Load the alexa top 1M dataset
    with open(ALEXA_TOP_1M_PATH, "r") as alexa_top1m_file:
        alexa_top1m = list(map(line_to_url, alexa_top1m_file.readlines()))
    # Shuffle the URLs
    random.shuffle(alexa_top1m)
    # Get a tor browser
    tor_browser = TorBrowser(TBB_PATH, TBB_LOG)
    # Navigate to the alexa top 1M
    for index, website in enumerate(alexa_top1m):
        # Start tor browser
        tor_browser.start()
        # Navigate to a webpage 
        logger.info("Navigating to {} ({}/{})".format(website, index + 1, len(alexa_top1m)))
        try:
            # Navigate to the website
            logger.info("Navigating to {} ({}/{})".format(website, index + 1, len(alexa_top1m)))
            tor_browser.navigate(website)
            # If navigation is successful, wait a bit for the page to load
            logger.info("Waiting for {} to load".format(website))
            tor_browser.wait_until_ready()
            # TODO: if that is successful, browse a bit
        except Exception as err:
            logger.error("Timeout or exception for navigation: {}".format(err))
        # Close the browser
        tor_browser.stop()
if __name__ == "__main__":
   main()
