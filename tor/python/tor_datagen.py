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

import os
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
import signal
import sys
from stem import process as stem_process
from time import sleep


def ls(path):
    messages = []
    for path in path.iterdir():
        messages.append("{} {}".format("d" if path.is_dir() else "f", path))
    messages.sort()
    for message in messages:
        print(message)
# Parse command line arguments
# Get path to browser bundle
tbb_path = Path(sys.argv[1])
# Get path to urls
urls_path = Path(sys.argv[2])

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

# Configure tor to use the proper pluggable transport
meek_bridge = "meek 0.0.2.0:3 97700DFE9F483596DDA6264C4D7DF7641E1E39CE url=https://meek.azureedge.net/ front=ajax.aspnetcdn.com"
tor_config = {
    "ClientTransportPlugin": "meek exec {} -- {}".format(meek_client_tb_path, meek_client_path),
    "Bridge": meek_bridge
}

# Create a requests session that stores a static proxy config
session = requests.Session()
session.proxies = {
    "http": "socks5://localhost:9050",
    "https": "socks5://localhost:9050"
}
# Ensure we don't retry too many times
session.mount("h", HTTPAdapter(max_retries=1))
with urls_path.open('r') as urls_file:
    for url in urls_file.readlines():
        # Strip off useless info and add in protocol
        url = "http://{}".format(url.rstrip().split(",")[1])
        # Start the tor process
        print("Starting tor")
        tor_process = stem_process.launch_tor_with_config(config=tor_config, tor_cmd=str(tor_executable_path))
        print("Started tor")
        # Print the URL
        print("Navigating to {}".format(url))
        # Make a get request to the tor process
        try:
            response = session.get(url, timeout=(5, None))
        except:
            print("Failed to request {}".format(url))
        # Print some debug info
        print("Code: {}, Body Length: {}".format(response.status_code, len(response.text)))
        # Kill the tor process and wait for it to end so we can restart it
        print("Killing tor")
        tor_process.kill()
        print("Killed tor")
