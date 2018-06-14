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

from bs4 import BeautifulSoup
import hashlib
import logging
import os
from pathlib import Path
import random
import requests
from requests.adapters import HTTPAdapter
import signal
import socket
import sys
from stem import process as stem_process
from time import sleep


# Set up a logger
logger = logging.getLogger("meek_datagen")
logger.setLevel(logging.DEBUG)
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
# Random ranges for data
EXTRA_PAGES_MEAN = 1
EXTRA_PAGES_STDEV = 5
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
# Extension config
extension_override_path = tbb_path / "Browser/TorBrowser/Data/Browser/profile.default/preferences/extension-overrides.js"

# Set environment to use tor directory for dynamic libs
if "LD_LIBRARY_PATH" in os.environ:
    os.environ["LD_LIBRARY_PATH"] = "{}:{}".format(os.environ["LD_LIBRARY_PATH"], str(tor_path))
else: 
    os.environ["LD_LIBRARY_PATH"] = str(tor_path)

# Configure tor to use the proper pluggable transport
# Extract the proper pluggable transport from the tor browser plugin preferences
def get_bridges(extension_override_path, bridge_type):
    bridges = []
    with extension_override_path.open("r") as extension_override_file:
        # Iterate over each configuration option
        # TODO: something more resilient such as a js parser
        for config_line in extension_override_file.readlines():
            # ignore non-preference lines
            if not config_line.startswith("pref("):
                continue
            # Parse the line into key, value
            key, value = config_line.lstrip("pref(").rstrip(");\n").split(", ")
            # Strip all quotes and spaces from key and value
            key = key.strip("\" ")
            value = value.strip("\" ")
            # Grab all config lines that refer to
            if key.startswith("extensions.torlauncher.default_bridge.{}".format(bridge_type)):
                bridges.append(value)
    return bridges




# Get the first bridge
bridge = get_bridges(extension_override_path, "meek-azure")[0]
# bridge = "meek 0.0.2.0:3 97700DFE9F483596DDA6264C4D7DF7641E1E39CE url=https://meek.azureedge.net/ front=ajax.aspnetcdn.com"
logger.info("Using bridge {}".format(bridge))
# Set up tor daemon configuration options 
tor_config = {
    "UseBridges": "1",
    "ClientTransportPlugin": "meek exec {} -log /home/user/logs/meek_helper.log -- {} -log /home/user/logs/meek.log".format(meek_client_tb_path.absolute(), meek_client_path.absolute()),
    "Bridge": bridge
}
# Create a requests session that uses a static proxy config
session = requests.Session()
session.proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
# Ensure we don't retry too many times
session.mount("h", HTTPAdapter(max_retries=1))
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
        tor_process = stem_process.launch_tor_with_config(config=tor_config, tor_cmd=str(tor_executable_path), timeout=600, take_ownership=True, init_msg_handler=print)
        logger.info("Started tor")
        # Print the URL
        logger.info("Navigating to {} ({}/{})".format(url, idx + 1, num_urls))
        # Make a get request to the tor process
        try:
            # Request the website
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            # Print some debug information
            logger.debug("Code: {}, Body Length: {}".format(response.status_code, len(response.text)))
            # Choose some number of pages to grab additionally
            num_extra_urls = max(int(round(random.gauss(EXTRA_PAGES_MEAN, EXTRA_PAGES_STDEV),0)),0)
            if num_extra_urls != 0:
                # Parse the page
                soup = BeautifulSoup(response.text, 'lxml')
                # Get all elements with "src" attribute
                extra_urls = list(map(lambda element: element["src"], soup.find_all(attrs={"src": True})))
                # Shuffle them
                random.shuffle(urls)
                # Grab the number of urls generated
                for extra_url in extra_urls[:num_extra_urls]:
                    logger.info("Pulling extra URL {}".format(extra_url))
                    response = session.get(extra_url, timeout=REQUEST_TIMEOUT)
                    logger.debug("Code: {}, Body Length: {}".format(response.status_code, len(response.text)))

        except Exception as exc:
            logger.info("Failed to request {}: {}".format(url, exc))
        # Kill the tor process and wait for it to end so we can restart it
        logger.info("Killing tor")
        tor_process.kill()
        logger.info("Killed tor")
