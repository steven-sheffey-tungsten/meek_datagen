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

# Add local scripts to path
PATH=$HOME/bin:$PATH

# Prefix for captures
PCAP_PREFIX=$PLUGGABLE_TRANSPORT

# Log file for tor browser
export TBB_LOG=$HOME/logs/tbb-$(hostname).log

# Start XVFB
source start_xvfb.sh
# Start VNC
start_vnc.sh

# Start capturing packets
echo "Starting TCPDUMP"
# Captures all traffic on port 443
sudo tcpdump -j host_hiprec -K -w pcap_data/${PCAP_PREFIX}_$(date +%s)_$(hostname).pcap port not 5900 &
# Get PID of tcpdump
export TCPDUMP_PID=""
while [[ $TCPDUMP_PID == "" ]]; do
	export TCPDUMP_PID=`ps --ppid $! -o pid=`
done
echo "TCPDUMP started on $TCPDUMP_PID"

# Set up a trap so TCPdump gets killed cleanly 
cleanly_kill_tcpdump() {
	# Kill firefox if it exists
	# Once program is done, wait until we have cleanly killed tcpdump
	echo "Waiting for TCPDUMP to exit cleanly"
	while sudo kill $TCPDUMP_PID; do
		sleep 0.5
	done
}
trap cleanly_kill_tcpdump SIGTERM
trap cleanly_kill_tcpdump SIGINT
trap cleanly_kill_tcpdump SIGKILL

# Copy the proper meek config to into the tor browser's profile
# generate_tor_prefs.py $PLUGGABLE_TRANSPORT > $TBB_PATH/Browser/TorBrowser/Data/Browser/profile.default/prefs.js


# Activate the python environment
source ./env/bin/activate
# Run the capture script
# ./meek_data_generator.py &
# Run "asynchronously" so BASH can capture signals
wait $!
# Deactivate the python environment
deactivate

cleanly_kill_tcpdump
