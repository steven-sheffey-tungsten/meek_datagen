#!/bin/bash
# Copyright 2018 Steven Sheffey
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


# Constants
# TODO: Put this in /var/run
export PID_FILE="/tmp/tcpdump.pid"

# Get arguments from command line
# TODO: check existence
export PREFIX="$1"

# Run tcpdump
# TODO: use expect instead of sleep
echo "Starting tcpdump"
tcpdump -j host_hiprec -K \
	-w "/pcap_data/${PREFIX}_$(date +%s)_$(hostname).pcap" &
# Store the PID as a variable
export TCPDUMP_PID="$!"
# Store its PID in a file
echo "$TCPDUMP_PID" > "${PID_FILE}"
# Let user know what is happening
echo "tcpdump has been started. You may want to wait a few seconds to ensure capture is happening"
# Wait for TCPDUMP to finish
wait $TCPDUMP_PID
# Once TCPDUMP is finished, clean up the PID file. This will let whatever killed it know
# that tcpdump is dead
rm "${PID_FILE}"
