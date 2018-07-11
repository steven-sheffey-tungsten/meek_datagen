#!/usr/bin/env python3
# Copyright 2018 Steven Sheffey
# This fHOMEile is part of meek_datagen.
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
# TODO: config file as argument
with open('config.toml','r') as config_file:
    config = toml.load(config_file)
# Load config settings
# Mode
mode = config["mode"]
# Common config
common = config["common"]
timeout = int(common["timeout"])
seed = int(common["seed"])
log_level = common["loglevel"].upper()

# TODO: move different modes into functions
# TODO: use __main__
if mode == "tor":
    # Load the tor config section
    tor = config["tor"]
    bridge = tor["bridge"]
    port = int(tor["port"])


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
tbb_path = Path(sys.argv[1])
# Get path to urls
urls_path = Path(sys.argv[2])
# Get number of URLS to retrieve
num_urls = int(sys.argv[3])
# Get random seed
try:
    seed = sys.argv[4]
    random.seed(seed)
except:
    print("Error getting seed")
    random.seed(0)


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


bridge = "meek 0.0.2.0:3 97700DFE9F483596DDA6264C4D7DF7641E1E39CE url=https://meek.azureedge.net/ front=ajax.aspnetcdn.com"
logger.info("Using bridge {}".format(bridge))

# Change directory into tor browser bundle folder before starting tor
os.chdir(tbb_path / "Browser") 
# Set up tor daemon configuration options 
tor_config = {
    "UseBridges": "1",
    # "ClientTransportPlugin": "meek exec {} -log /home/user/logs/meek_helper.log -- {} -log /home/user/logs/meek.log".format(meek_client_tb_path.absolute(), meek_client_path.absolute()),
    "ClientTransportPlugin": "meek exec {} -- {}".format(meek_client_tb_path.absolute(), meek_client_path.absolute()),
    # "ClientTransportPlugin": "obfs2,obfs3,obfs4,scramblesuit exec {}".format(obfsproxy_client_path), 
    "Bridge": bridge
}

# Set up firefox to run in headless mode to avoid graphical overhead
opts = FirefoxOptions()
opts.add_argument("--headless")

# Set up a firefox profile configured to retrieve sites over TOR
profile = FirefoxProfile()
proxy = Proxy()
proxy.socks_proxy = 'localhost:9050'
profile.set_proxy(proxy)

# Build a firefox webdriver
driver = webdriver.Firefox(firefox_profile=profile, firefox_options=opts)

# Open 
with urls_path.open('r') as urls_file:
    # Read in hosts from the alexa top 1M
    urls = list(map(lambda line: line.rstrip().split(",")[1], urls_file.readlines()))
    # Shuffle them
    random.shuffle(urls)
    # Pick some number of them out
    urls = urls[:num_urls]
    for idx, url in enumerate(urls):
        # Add protocol
        # TODO: add https
        url = "http://{}".format(url)
        # Start the tor process
        logger.info("Starting tor")
        tor_process = stem_process.launch_tor_with_config(
            config = tor_config,
            tor_cmd = str(tor_executable_path),
            timeout = 600,
            take_ownership = True,
            # TODO: set this if a debug flag is enabled
            # init_msg_handler = print
        )
        # TODO: check the control port until bootstrap is done
        logger.info("Started tor")
        # Print the current URL
        # TODO: log this somewhere auditable
        logger.info("Navigating to {} ({}/{})".format(url, idx + 1, num_urls))
        # Make a get request to the tor process
        try:
            # Request the webpage through the selenium driver
            driver.get(url)
        except Exception as exc:
            logger.error("Failed to request {}: {}".format(url, exc))
        # Kill the tor process and wait for it to end so we can restart it
        logger.info("Killing tor")
        tor_process.kill()
        logger.info("Killed tor")
driver.close()
