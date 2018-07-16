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

import hashlib
import logging
import os
from pathlib import Path
import random
import signal
import socket
import sys
from time import sleep

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from stem import process as stem_process
import toml

# TODO: argument parsing with argparse

# Read in the config
config_filename = sys.argv[1]
with open(config_filename,'r') as config_file:
    config = toml.load(config_file)
# Load config settings
# Mode
mode = config["mode"]
# Common config
log_level = config["common"]["loglevel"].upper()
page_timeout = int(config["common"]["page_timeout"])
seed = int(config["common"]["seed"])
shuffle = bool(config["common"]["shuffle"])

# TODO: move different modes into functions
# TODO: use __main__
if mode == "tor":
    # Load the tor config section
    bridge = config["tor"]["bridge"]
    port = int(config["tor"]["port"])
    # Load the tor timeouts
    initial_tor_timeout = config["tor"]["timeout"]["initial"]
    regular_tor_timeout = config["tor"]["timeout"]["regular"]
# Set up a logger
logger = logging.getLogger("meek_datagen")
# Convert the log level to an enum
logger.setLevel(logging.getLevelName(log_level))
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("%(filename)s %(asctime)s %(levelname)s %(funcName)s:%(lineno)d  %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

# Parse command line arguments
# Get path to browser bundle
tbb_path = Path(sys.argv[2])
# Get path to urls
urls_path = Path(sys.argv[3])
# Get number of URLS to retrieve
num_urls = int(sys.argv[4])


# Parameters for the requester
# Timeout for requests in seconds
REQUEST_TIMEOUT=5
# Get path to tor folder
tor_path = tbb_path / "Browser" / "TorBrowser" / "Tor"
# Tor daemon
tor_executable_path = tor_path / "tor"
# Meek client
meek_client_path = tor_path / "PluggableTransports" / "meek-client"
# Meek client helper
meek_client_tb_path = tor_path / "PluggableTransports" / "meek-client-torbrowser"

# Set environment to use tor directory for dynamic libs
if "LD_LIBRARY_PATH" in os.environ:
    os.environ["LD_LIBRARY_PATH"] = "{}:{}".format(os.environ["LD_LIBRARY_PATH"], str(tor_path))
else: 
    os.environ["LD_LIBRARY_PATH"] = str(tor_path)


def start_tor():
    # Set up tor daemon configuration options 
    tor_config = {
        "UseBridges": "1",
        # "ClientTransportPlugin": "meek exec {} -log /home/user/logs/meek_helper.log -- {} -log /home/user/logs/meek.log".format(meek_client_tb_path.absolute(), meek_client_path.absolute()),
        "ClientTransportPlugin": "meek exec {} --log helper.log -- {} --log meek.log".format(meek_client_tb_path.absolute(), meek_client_path.absolute()),
        # "ClientTransportPlugin": "obfs2,obfs3,obfs4,scramblesuit exec {}".format(obfsproxy_client_path), 
        "Bridge": bridge,
        'Log': [
          'NOTICE stdout',
          'ERR file /tmp/tor_error_log',
        ]
    }
    return stem_process.launch_tor_with_config(
        config = tor_config,
        tor_cmd = str(tor_executable_path),
        timeout = initial_tor_timeout if idx == 0 else regular_tor_timeout,
        take_ownership = True,
        # TODO: set this if a debug flag is enabled
        init_msg_handler = print
    )


# Set up firefox to run in headless mode to avoid graphical overhead
opts = FirefoxOptions()
opts.set_headless(False)

# Configure profile settings
profile = FirefoxProfile()
# Add the proxy
profile.set_preference("network.proxy.type", 1)
profile.set_preference("network.proxy.socks", "127.0.0.1")
profile.set_preference("network.proxy.socks_port", 9050)
profile.set_preference("network.proxy.socks_remote_dns", True)

# Build a Firefox webdriver
driver = webdriver.Firefox(profile, firefox_options=opts)

# Set timeouts
driver.set_page_load_timeout(page_timeout)
driver.implicitly_wait(page_timeout)

# Create a requests session that uses a static proxy config
"""
session = requests.Session()
session.proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
# Ensure we don't retry too many times
session.mount("http", HTTPAdapter(max_retries=1))
session.mount("https", HTTPAdapter(max_retries=1))
"""

# Iterate over URLs
with urls_path.open('r') as urls_file:
    # Read in hosts from the alexa top 1M
    urls = list(map(lambda line: line.rstrip().split(",")[1], urls_file.readlines()))
    # Shuffle them
    if shuffle:
        random.shuffle(urls)
    # Pick some number of them out
    urls = urls[:num_urls]
    for idx, url in enumerate(urls):
        # Add protocol
        # TODO: add https
        url = "http://{}".format(url)
        # Start the tor process
        # TODO: refactor this into a class with `with` enabled
        if mode == "tor":
            logger.info("Starting tor")
            tor_process = start_tor()
            sleep(5)
            logger.info("Started tor")
        # Make a get request to the tor process
        while True:
            try:
                # TODO: log this somewhere auditable
                logger.info("Navigating to {} ({}/{})".format(url, idx + 1, num_urls))
                # Request the page
                driver.get(url)
            # Ignore broken pipe and try again
            except BrokenPipeError as _:
                logger.error("Geckodriver had a broken pipe error. Retrying request")
                continue 
                # Ignore other exceptions
                # TODO: look deeper into this
            except Exception as exc:
                logger.error("Failed to request {}: {}".format(url, exc))
            # If the request succeeded, break the loop
            break
        # Log the title just to see if *something* loaded
        try:
            logger.debug("Title of loaded page: {}".format(driver.title))
        except:
            pass
        # Cleanup
        try:
            # Go to blank page so residual requests dont persist
            driver.get("about:blank")
            # In intervals, clear cookies
            # TODO: make this a config option
            if idx % 10 == 0:
                driver.clear_all_cookies()
        except Exception as exc:
            logger.error("Failed to cleanup: {}".format(url, exc))
        # Kill the tor process and wait for it to end so we can restart it
        if mode == "tor":
            logger.info("Killing tor")
            tor_process.kill()
            logger.info("Killed tor")
driver.close()
