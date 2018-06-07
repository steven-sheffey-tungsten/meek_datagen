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
import logging
import time
import marionette_driver
from marionette_driver.marionette import Marionette

# Address for connecting to marionette
MARIONETTE_HOST = "localhost"
MARIONETTE_PORT = 2828
# How long in seconds to wait for Marionette to start
MARIONETTE_STARTUP_TIMEOUT = 3600

# Initialize a logger
logger = logging.getLogger("wait_for_tor_browser")
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("%(filename)s %(asctime)s %(levelname)s %(funcName)s:%(lineno)d  %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

# Create a marionette handle
marionette = Marionette(
        host=MARIONETTE_HOST,
        port=MARIONETTE_PORT,
        startup_timeout=MARIONETTE_STARTUP_TIMEOUT
)

try:
    # Try to start session. If this fails, it could just mean
    # a tor browser issue, so we ignore failure, and assume the browser started at least
    marionette.start_session()
except Exception as exc:
    logger.warning("Marionette failed to start: {}".format(exc))
