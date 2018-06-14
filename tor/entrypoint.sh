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

# Where to find alexa top1m data
export ALEXA_PATH="$HOME/data/top-1m.csv"
# Amount of time to wait for tcpdump to start
export TCPDUMP_TIME=5
# Prefix for captures
export PCAP_PREFIX="meek-azure"


# Used to gracefully quit on interrupt
gracefully_quit() {
	# Stop tcpdump
	echo "Gracefully stopping tcpdump"
	sudo stop_tcpdump.sh
}

# Run tor browser once initially to get profiles set up
# xvfb-run ./initial_tor_browser_setup.sh "$TBB_PATH"

# Start capturing traffic
sudo start_tcpdump.sh $PCAP_PREFIX &
# Wait a bit for tcpdump to start
echo "Waiting ${TCPDUMP_TIME} seconds for tcpdump to start"
sleep "$TCPDUMP_TIME"
echo "Finished waiting for tcpdump"

# Activate the python environment
export PS1=""
source ./env/bin/activate
# Using the meek client mask in TBB requires being in the bundle/Browser directory
cd "$TBB_PATH/Browser"
# Generate some data by downloading many webpages over meek 
xvfb-run python3 -u /usr/local/bin/tor_datagen.py "$TBB_PATH" "$ALEXA_PATH" 10000 $(hostname) &
# Set up the signal handler
trap 'gracefully_quit' SIGINT SIGTERM SIGSTOP SIGKILL EXIT
# Wait for the python script to finish (or be interrupted)
wait $!
# Exit, which triggers the signal
exit 0
