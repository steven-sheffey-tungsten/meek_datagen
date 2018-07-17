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

import argparse
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
import toml

from proxy import Proxy
from requester import Requester 
from utils import build_logger, load_alexa, load_alexa_lazy

def main(args):
    # Read in the config
    config = None
    with args.config_filename.open('r') as config_file:
        config = toml.load(config_file)
    # Initialize the logger 
    logger = build_logger(config)

    # Load randomization options
    seed = config["common"]["seed"]
    shuffle = config["common"]["shuffle"]
    
    # Seed the rng
    random.seed(seed)

    # Initialize proxy configuration
    proxy = Proxy(config, args.tbb_path) 

    # Initialize a browser
    with Requester(config) as requester:
        # Load the dataset
        urls = load_alexa_lazy(args.urls_path, "http")
        # Navigate to all of the urls
        for idx, url in enumerate(urls):
            with proxy as _:
                # TODO: log this somewhere auditable
                # Log the request
                logger.info("Navigating to {} ({}/{})".format(
                    url,
                    idx,
                    "UNKNOWN"
                ))
                # Request the URL 
                requester.request(url)


# Run the program
if __name__ == "__main__":
    # Get a command line parser 
    arg_parser = argparse.ArgumentParser(
        description = "Automatically browses using a list of urls, in order to generate traffic"
    )
    # Config filename
    arg_parser.add_argument(
        'config_filename',
        metavar='CONFIG_FILENAME',
        type=Path,
        help='path to the config file'
    )
    # TBB location 
    arg_parser.add_argument(
        'tbb_path',
        metavar='TBB_PATH',
        type=Path,
        help='path to the Tor Browser Bundle'
    )
    # Path to urls dataset
    # TBB location 
    arg_parser.add_argument(
        'urls_path',
        metavar='URLS_PATH',
        type=Path,
        help='path to a dataset of URLs'
    )
    # Parse the arguments
    args = arg_parser.parse_args()
    # Run the main function
    main(args)
