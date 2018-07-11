#!/bin/bash
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

set -eu

# Get tor browser path from arguments
export TBB_PATH="$1"

# Configure the tor browser to use the meek bridge
# TODO: pass in meek-azure from environment
./generate_tor_prefs.py meek-azure >> "$TBB_PATH/Browser/TorBrowser/Data/Browser/profile.default/prefs.js"
# Start tor browser with marionette enabled
echo "Starting tor browser"
echo $TBB_PATH
$TBB_PATH/Browser/start-tor-browser --verbose -marionette &
echo "Started tor browser"
# Store tor browser's pid
export TOR_BROWSER_PID=$!
# Enter the environment for python 2
export PS1=""
source ./env2/bin/activate
# Run a python script that finishes when the browser has started
echo "Waiting for tor browser"
./wait_for_tor_browser.py
echo "Done waiting for tor browser"
# Exit the python2 environment
deactivate
# Wait for tor browser to be killed
pkill firefox
